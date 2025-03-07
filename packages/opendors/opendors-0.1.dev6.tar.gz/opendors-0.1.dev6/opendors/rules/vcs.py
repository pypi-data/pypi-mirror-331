import json
import subprocess
from subprocess import CalledProcessError
import re

import urllib3
from ratelimit import sleep_and_retry, limits

from opendors.abc import WorkflowRule
from opendors.model import VCS, Platform
from opendors.rules.urls import get_sourceforge_api_url


########################################################################################################################
############################## Class
########################################################################################################################


class VCSRetriever(WorkflowRule):
    """
    Identifies the applicable version control system to use with a specific repository URL and saves these data in an
    OpenDORS Corpus.
    """

    def __init__(
        self,
        input_json: str,
        output_json: str,
        log_file: str,
        log_level: str = "DEBUG",
        indent: int = 0,
    ):
        super().__init__(__name__, log_file, log_level, indent)
        self.input_json = input_json
        self.output_json = output_json

    ##################################################
    ########## Methods
    ##################################################

    @sleep_and_retry
    @limits(calls=3, period=1)
    def _get_sourceforge_vcs_data(self, url: str) -> list[tuple[VCS, str]] | None:
        """
        Identifies the applicable version control repositories for a Sourceforge project.
        This is necessary, because Sourceforge projects can provide >=1 either Subversion or Git repositories.

        :param url: The URL for the Sourceforge project
        :return: A list of tuples of VCS Enum and clone URL, or None if neither git nor svn are in the project's tools
        """
        api_url = get_sourceforge_api_url(url)
        response = urllib3.request(
            "GET", api_url, headers={"Content-Type": "application/json"}
        )
        if response.status == 200:
            repos = []
            response_data = response.data.decode("utf-8").strip()
            data = json.loads(response_data)
            for tool in data["tools"]:
                if tool["name"] == VCS.git.value:
                    repos.append((VCS.git, tool["clone_url_https_anon"]))
                elif tool["name"] == VCS.svn.value:
                    repos.append((VCS.svn, tool["clone_url_https_anon"]))
                elif tool["name"] == VCS.cvs.value:
                    repos.append((VCS.cvs, tool["url"]))
            return repos
        else:
            self.log.error(
                "Could not retrieve repository data for Sourceforge repository at %s.",
                api_url,
            )

    ##########
    ### Main method
    ##########

    def run(self) -> None:
        """
        Runs the workflow rule.

        :return: None
        """
        corpus = self.read_corpus(self.input_json)
        total_software = len(corpus.research_software)
        for i_rs_in, rs_in in enumerate(corpus.research_software):
            self.log.debug(
                f"Determining VCS systems for repositories in software {i_rs_in + 1}/{total_software}"
            )
            if not rs_in.repositories:
                if rs_in.platform == Platform.SOURCEFORGE_NET:
                    lst_sf_vcs_data = self._get_sourceforge_vcs_data(
                        rs_in.canonical_url
                    )
                    if lst_sf_vcs_data:
                        for vcs, clone_url in lst_sf_vcs_data:
                            rs_in.add_repository(vcs=vcs, url=clone_url)
                            self.log.debug(
                                f"Added {vcs} repository to software at {rs_in.canonical_url}."
                            )
                else:
                    # Safeguarding that the canonical git repo URL is set,
                    # even if setting it was forgotten beforehand.
                    rs_in.add_repository(VCS.git, str(rs_in.canonical_url) + ".git")
                    self.log.debug(
                        f"Added git repository to software at {rs_in.canonical_url}."
                    )
        self.write_corpus(corpus, self.output_json)


def git_ls_remote_head(clone_url_str: str) -> str:
    """
    Retrieve the commit hash for HEAD from a remote git repository.

    :param clone_url_str: The clone URL string to retrieve the HEAD hash for
    :return: The HEAD hash for the given git repository
    """
    try:
        stdout = subprocess.check_output(["git", "ls-remote", clone_url_str, "HEAD"])
        return re.split(r"\s+", stdout.decode("utf-8"), maxsplit=1)[0]
    except CalledProcessError:
        raise RuntimeError(
            f"Could not run 'git ls-remote' to retrieve the HEAD for repository {clone_url_str}."
        )
