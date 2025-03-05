from collections import namedtuple
import time
from datetime import datetime, timezone
from json import JSONDecodeError

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
)

from urllib3 import Retry


from opendors.abc import WorkflowRule
from opendors.model import VersionType, SourceCodeRepository

SwhIdentifiers = namedtuple("IDs", ["swh_id", "swh_dir_id"])


class SWHIdError(Exception):
    pass


class APIQueryError(Exception):
    """Custom exception for API query failures."""

    pass


class RateLimitExceededError(Exception):
    """Custom exception for rate limit exceeded scenarios."""

    pass


class SWHAPIQueryManager:
    def __init__(self, swh_token: str, log):
        self.timeout = 30
        self.queries_per_hour = 1200
        self.session = SWHAPIQueryManager._create_session(swh_token)
        self.query_timestamps = []
        self.base_url = "https://archive.softwareheritage.org/api/1/"
        self.log = log

    @staticmethod
    def _create_session(swh_token: str) -> requests.Session:
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {swh_token}"})
        retry = Retry(
            connect=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
            raise_on_status=False,  # Don't raise exception on retry-able status codes
            respect_retry_after_header=True,  # Respect Retry-After header
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def query(
        self, endpoint, post: bool = False, retry: bool = True
    ) -> Response | None:
        try:
            return self._safe_query(endpoint, post)

        except RateLimitExceededError as rle:
            if retry:
                self.log.warning("Retrying query once.")
                return self.query(endpoint, post, False)
            else:
                self.log.error(f"Query failed, returning None: {rle}")
                return None

        except APIQueryError as aqe:
            self.log.error(f"Query failed: {aqe}")
            return None

        except HTTPError as he:
            self.log.error(f"HTTP error for '{endpoint}': {he.response.status_code}.")
            return None

    def _safe_query(self, endpoint: str, post: bool) -> Response | None:
        _url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            if post:
                response = self.session.post(_url)
            else:
                response = self.session.get(_url)

            self._handle_rate_limit(response)

            # Raise an HTTPError for bad responses that weren't retried
            response.raise_for_status()

            # Sleep for 3 seconds hard limit to avoid rate limiting
            time.sleep(3)

            return response

        except (ConnectionError, Timeout) as e:
            self.log.warning(f"Connection error: {e}")
            raise APIQueryError(f"Connection failed: {e}")

        except HTTPError as e:
            # Handle specific HTTP error codes
            if e.response.status_code == 429:  # Rate limit exceeded
                retry_after = int(e.response.headers.get("Retry-After", 60))
                self.log.warning(
                    f"Rate limit exceeded. Retry after {retry_after} secs."
                )
                time.sleep(retry_after)
                raise RateLimitExceededError(
                    f"Rate limit hit. Retry after {retry_after} secs."
                )

            raise  # Re-raise for other HTTP errors

    def _handle_rate_limit(self, response: Response):
        # Check remaining calls
        remaining_calls = response.headers.get("X-RateLimit-Remaining")
        reset_timestamp = response.headers.get("X-RateLimit-Reset")
        if remaining_calls is not None:
            remaining = int(remaining_calls)

            # If no calls remaining, check reset time
            if remaining <= 0 and reset_timestamp is not None:
                try:
                    # Convert reset timestamp to datetime
                    reset_time = datetime.fromtimestamp(float(reset_timestamp))
                    current_time = datetime.now()

                    # Calculate and wait until reset time
                    wait_time = max(0, int((reset_time - current_time).total_seconds()))

                    self.log.warning(
                        f"Rate limit exhausted. Waiting {wait_time:.2f} secs."
                    )
                    time.sleep(wait_time)

                except (ValueError, TypeError) as e:
                    self.log.error(
                        f"Error parsing rate limit reset time: {e}. Waiting 60 secs."
                    )
                    # Fallback to default wait if parsing fails
                    time.sleep(60)  # Default 1-minute wait


class SWHIdRetriever(WorkflowRule):
    """
    TODO
    """

    def __init__(
        self,
        input_json: str,
        output_json: str,
        swh_token: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_json = output_json
        self.api_manager = SWHAPIQueryManager(swh_token, self.log)

    def run(self) -> None:
        self.log.debug(
            f"Retrieving Software Heritage archive data for file {self.input_json}."
        )

        corpus = self.read_corpus(self.input_json)
        software = corpus.research_software[0]

        for repo in software.repositories:
            if repo.accessible and repo.latest is not None:
                swh_identifiers = self.retrieve_swh_ids(repo)
                if swh_identifiers is not None:
                    repo.latest.swh_id = swh_identifiers.swh_id
                    repo.latest.swh_dir_id = swh_identifiers.swh_dir_id

        self.write_corpus(corpus, self.output_json)

    def retrieve_swh_ids(self, repo: SourceCodeRepository) -> SwhIdentifiers:
        latest = repo.latest
        if latest.version_type == VersionType.TAG:
            if latest.tag_sha is not None:
                return self._retrieve_swh_ids_release(repo)
            else:
                return self._retrieve_swh_ids_revision(repo)
        elif latest.version_type == VersionType.REVISION:
            return self._retrieve_swh_ids_revision(repo)

    def _retrieve_swh_ids_release(
        self, repo: SourceCodeRepository, new_snp: bool = False
    ) -> SwhIdentifiers | None:
        response = self.api_manager.query(f"release/{repo.latest.tag_sha}/")
        if response is None:
            return None
        match response.status_code:
            case 200:
                try:
                    data = response.json()
                except JSONDecodeError as jde:
                    self.log.error(
                        f"Could not decode JSON from SWH response on URL release/{repo.latest.tag_sha}: {jde}"
                    )
                    return None
                revision_id = self.extract_revision_id(data)
                if revision_id is not None:
                    swh_ids = self._retrieve_swh_ids_revision(repo, revision_id)
                    if swh_ids is not None:
                        return SwhIdentifiers(
                            swh_ids.swh_id,
                            swh_ids.swh_dir_id,
                        )
                self.log.debug(
                    f"In lieu of revision + directory SWH ids, "
                    f"constructing release id for latest version of {repo.clone_url}."
                )
                return SwhIdentifiers(self.construct_swh_id("rel", data["id"]), None)
            case 404:
                if new_snp:
                    self.log.warning(
                        f"Release {repo.latest.tag_sha} could not be found in newly created snapshot."
                    )
                    return None
                snp_id = self.save_swh_snapshot(repo)
                if snp_id is not None:
                    self._retrieve_swh_ids_release(repo, True)
                else:
                    return None
            case 400:
                self.log.warning(f"Bad request for: 'release/{repo.latest.tag_sha}'.")
                return None
            case _:
                self.log.warning(
                    f"Something went wrong retrieving SWH IDs for latest version {repo.latest.tag_sha} "
                    f"of repo {repo.clone_url}."
                )
                return None

    def _retrieve_swh_ids_revision(
        self, repo: SourceCodeRepository, revision_id: str = None, new_snp: bool = False
    ) -> SwhIdentifiers | None:
        if revision_id is None and repo.latest.commit_sha is not None:
            revision_id = repo.latest.commit_sha
        response = self.api_manager.query(f"revision/{revision_id}/")
        if response is None:
            return None
        match response.status_code:
            case 200:
                try:
                    data = response.json()
                except JSONDecodeError as jde:
                    self.log.error(
                        f"Could not decode JSON from SWH response on URL revision/{revision_id}: {jde}"
                    )
                    return None
                self.log.debug(
                    f"Successfully retrieved revision + directory SWH ids for latest version of {repo.clone_url}."
                )
                return SwhIdentifiers(
                    self.construct_swh_id("rev", data["id"]),
                    self.construct_swh_id("dir", data["directory"]),
                )
            case 404:
                if new_snp:
                    self.log.warning(
                        f"Revision {revision_id} could not be found in newly created snapshot."
                    )
                    return None
                snp_id = self.save_swh_snapshot(repo)
                if snp_id is not None:
                    self._retrieve_swh_ids_revision(repo, revision_id, True)
                else:
                    return None
            case 400:
                self.log.warning(f"Bad request for: 'revision/{revision_id}'.")
                return None
            case _:
                self.log.warning(
                    f"Something went wrong retrieving SWH IDs for latest version {repo.latest.version} "
                    f"of repo {repo.clone_url}."
                )
                return None

    def calculate_secs_until_reset(self, reset_secs: str) -> int:
        return int(reset_secs) - int(datetime.now(tz=timezone.utc).timestamp())

    def construct_swh_id(self, typ: str, sha: str) -> str:
        return f"swh:1:{typ}:{sha}"

    def save_swh_snapshot(self, repo: SourceCodeRepository) -> str | None:
        url_path = f"origin/save/{repo.vcs.value}/url/{str(repo.clone_url).removesuffix('.git')}/"
        response = self.api_manager.query(url_path, True)
        if response is None:
            return None
        try:
            data = response.json()
        except JSONDecodeError as jde:
            self.log.error(
                f"Could not decode JSON from SWH response on URL {url_path}: {jde}"
            )
            return None
        if response.status_code == 400:
            self.log.warning(
                f"Bad request. An invalid visit type or origin URL has been provided: {repo.clone_url}."
            )
        elif response.status_code == 403:
            self.log.warning(
                f"The repository URL is blacklisted for the Software Heritage Archive: {repo.clone_url}."
            )
        elif response.status_code == 200:
            if data["save_request_status"] == "accepted":
                visit = self.track_swh_request(data["id"])
                if visit is not None:
                    if visit["save_task_status"] == "succeeded":
                        self.log.info(
                            f"Successfully created new SWH snapshot for {repo.clone_url}."
                        )
                        return visit["snapshot_swhid"]
                    elif visit["save_task_status"] == "failed":
                        note = "No failure note"
                        if "note" in visit:
                            note = visit["note"]
                        self.log.warning(
                            f"Creating a new SWH snapshot for {repo.clone_url} failed: "
                            f"{note if note is not None else 'reason unclear'}."
                        )
                        return None
                else:
                    self.log.warning(
                        f"Could not check completion status for snapshot request {data['id']}."
                    )
                    return None

    def track_swh_request(self, request_id: str) -> dict | None:
        while True:
            try:
                has_completed, result = self.save_completed(
                    f"origin/save/{request_id}/"
                )
                if has_completed:
                    return result
                else:
                    time.sleep(30)
            except SWHIdError:
                return None

    def save_completed(self, url_path: str) -> (bool, dict | None):
        response = self.api_manager.query(url_path)
        if response is None:
            return False, None
        if response.status_code == 200:
            try:
                data = response.json()
            except JSONDecodeError as jde:
                self.log.error(
                    f"Could not decode JSON from SWH response on URL {url_path}: {jde}"
                )
                return False, None
            if data["save_task_status"] in ["succeeded", "failed"]:
                return True, data
            else:
                return False, data
        else:
            raise SWHIdError(
                f"Non 200 status code for querying SWH API with {url_path}."
            )

    def extract_revision_id(self, release_data: dict) -> str | None:
        if release_data["target_type"] == "revision":
            return release_data["target"]
        else:
            return None
