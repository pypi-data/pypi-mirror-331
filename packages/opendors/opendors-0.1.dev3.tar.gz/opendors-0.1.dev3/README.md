# opendors

Library for creating and interacting with the OpenDORS dataset.

## Installation

```shell
# Clone git repository & change into clone directory
git clone git@gitlab.dlr.de:drus_st/opendorslib.git
cd opendorslib

# Install with poetry
poetry install
```

If you want to use the [`repository`](opendors/rules/repository.py) workflow rule,
you also need to install:

- Ruby >= 3.4.1
- `github-linguist` gem >= 9.0.0
- `licensee` gem >= 9.18.0

This repository contains a definition for a conda environment that you can use to install these extra dependencies:
[`conda-environment.yml`](conda-environment.yml).
To install the dependencies, do:

```shell
conda create -n opendors --file conda-environment.yml
conda activate opendors
gem install github-linguist
gem install licensee
```

Keep the environment activated to use the [`repository`](opendors/rules/repository.py) rule.

## Usage

`opendors` provides both an API for creating an OpenDORS dataset,
and a CLI tool to interact with an OpenDORS dataset.

```shell
usage: opendors [-h] [-c] [-v] {schema,filter,stats,merge} ...

Utilities to work with OpenDORS datasets.

positional arguments:
  {schema,filter,stats,merge}
                        Available commands
    schema              Exports the JSON schema for the opendors model to 'schema.json'.
    filter              Filters a given dataset by programming language and/or before/after dates.
    stats               Gather statistics on a given OpenDORS dataset.
    merge               Merge OpenDORS datasets into a single file.

options:
  -h, --help            show this help message and exit
  -c, --compressed      Export as unindented JSON
  -v, --verbose         Print tracebacks on error
```

## Build Python package

Run `poetry build`.

To publish to PyPI, run `poetry publish`.
You need to have a PyPI API token configured to do this.

## Build conda package

The conda package is configured in `conda/recipe/local/meta.yaml`,
and reuses information from `pyproject.toml`.

To build package locally, run

```shell
# Update to next dev version to keep build metadata intact
poetry version 0.1.dev<n>
conda create -n condabuild conda-build git
conda activate condabuild
conda build conda/recipe/local <optional: --output-folder [FOLDER]>
# e.g.:
#  conda build conda/recipe/local --output-folder /home/stephan/src/opendors/conda-pkgs
```

You can then install the package in a new environment and use it:

```shell
conda create -n my-env --use-local opendors
```

# Run tests

Tests can be run locally as follows:

```bash
poetry run python -m pytest tests/
```

## Test coverage

Coverage (with branch coverage) can be displayed as follows:

```bash
poetry run python -m pytest tests --cov=opendors --cov-branch --cov-report=html --cov-report=term
```

## Static code analysis

Run `prospector` to analyse the code.
