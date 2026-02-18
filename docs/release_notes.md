# Release Notes

## 0.3.6 [2025-12-17]

__Maintenance__:

- Updated `python` from `3.13.7` to `3.13.11`
- Updated dependencies to address known vulnerabilities

## 0.3.5 [2025-10-03]

__Enhancements__:

- Added comprehensive file metadata support including `created`, `modified`,
  `name`, `classification`, `modality`, `size`, `version`, and
  `zip_member_count` fields to Flywheel object validation
- Enhanced Flywheel metadata validation with support for `flywheel` file type
  in validator initialization

__Fixes__:

- Fixed string concatenation error in `FileError` class for required property
  validation that was causing incorrect error location paths
- Improved error handling for Flywheel hierarchy location parsing to properly
  extract container locations from key paths

__Maintenance__:

- Improved `.gitignore` to use explicit whitelist pattern for better repository
  management
- Updated project configuration and build files
- Added `.markdownlint.json` configuration file
- Updated `README.md` summary for better clarity
- Upgraded `python` from `3.13.2` to `3.13.7`
- Enhanced test coverage with new test cases for file metadata fields, required
  property error handling, and Flywheel location error mapping

## 0.3.4 [2025-07-01]

__Enhancements__:

- Added `requirements-dev.txt` to `.dockerignore` for improved build context
- Added multi-stage `Dockerfile` with separate `dev` and production stages
- Added `uv.lock` file to version control for reproducible builds
- Added `flywheel` user to production Docker image for improved security

__Fixes__:

- Fixed trailing whitespace issues throughout documentation files

__Maintenance__:

- Migrated from `poetry` to `uv` for dependency management
- Upgraded `python` from `3.10` to `3.13`
- Updated base Docker image to `flywheel/python:3.13-main`
- Updated CI configuration to reference `flywheel-io/tools/etc/qa-ci` (branch
  `sse`)
- Updated `.pre-commit-config.yaml` to revision
  `b783285a315e509aaf189222ba94601de659ed5c`
- Added `eolfix` and `pytest` hooks to pre-commit configuration
- Updated `ruff` hook configuration to explicitly use `pyproject.toml`
- Removed `flywheel-sdk` version pin (was `17.7.0`)
- Added environment variables to `manifest.json` for runtime configuration
  (`PYTHON_VERSION`, `VIRTUAL_ENV`, `PYTHONPATH`, `PATH`)
- Added `uid` and `gid` fields to gear custom configuration in `manifest.json`
- Converted `pyproject.toml` to PEP 621 format
- Migrated build backend from `poetry.core.masonry.api` to `hatchling.build`
- Added `VALIDATE_CLASSIFICATION` variable to CI configuration

__Documentation__:

- Fixed markdown formatting issues in `CONTRIBUTING.md` and `README.md`

## 0.3.2 [2025-04-03]

__Fixes__:

- Fixed CSV validation to handle columns present in data but not defined in the
  schema by defaulting to `str` type instead of raising `KeyError`
- Fixed empty column removal logic to preserve all columns during initial CSV
  loading, only removing empty values during validation when `drop_empty=True`

__Enhancements__:

- Added `drop_empty` parameter to `CsvValidator.validate()` to optionally
  control removal of empty CSV columns (defaults to `True` for backward
  compatibility)

## 0.3.1 [2025-03-05]

__Fixes__:

- Fixed CSV validation to properly handle quoted fields containing commas by
  using Python's `csv.reader` instead of counting commas

__Maintenance__:

- Added `.github/` directory to `.gitignore` whitelist
- Increased test coverage for CSV validation with quoted fields and edge cases

## 0.3.0 [2025-01-22]

__Enhancements__:

- Added validation for CSV files with duplicate column headers
- Added validation to detect malformed CSV files with inconsistent comma counts
  per row
- Added validation to detect empty files (JSON and CSV)
- Added validation to detect files that cannot be properly opened by the loader
- Added early validation checks before schema validation to catch file format
  issues

__Fixes__:

- Fixed handling of empty JSON files to return validation error instead of
  empty dict
- Fixed handling of empty CSV files to return validation error instead of empty
  list
- Fixed `run.py` to handle and save file format validation errors before schema
  validation

__Maintenance__:

- Updated return type annotations in `loader.py` from `dict` to
  `t.Tuple[dict, t.List[t.Dict]]`
- Updated return type annotations in `parser.py` from `(str, str)` to
  `tuple[str, str]`
- Added comprehensive test coverage for CSV file format validation functions
- Added `.gitignore` file to restrict tracked files to essential project files

## 0.2.9 [2024-07-01]

__Fixes__:

- Fixed error handling for non-string location values in validation error
  reporting by converting all location elements to strings before joining

## 0.2.8 [2024-05-14]

__Maintenance__:

- Updated CI configuration reference from
  `flywheel-io/scientific-solutions/etc/sse-qa-ci` to
  `flywheel-io/tools/etc/qa-ci`
- Updated `.pre-commit-config.yaml` hooks reference to
  `dee3cd63f9f4d7a2ab95b41f01281b97fd480cf7`
- Added `test:gear` job extending `.test:gear` and `.gitlab-runner-medium` to
  CI pipeline
- Replaced `poetry_export` with new hook ordering: `gearcheck`, `hadolint`,
  `jsonlint`, `linkcheck`, `markdownlint`, `yamllint`, `ruff`, `ruff_format`,
  `ruff_tests`
- Removed `docker_build` and `pytest` hooks from `.pre-commit-config.yaml`
- Reformatted JSON test configuration files for consistent indentation and
  structure
- Added docstrings to functions and classes throughout the codebase
- Applied `ruff` code formatting to Python source files (`errors.py`,
  `loader.py`, `parser.py`, `utils.py`, `validator.py`, `run.py`)
- Fixed import ordering and added module-level docstrings
- Improved type annotations in function signatures

## 0.2.7 [2024-05-09]

__Maintenance__:

- Minor maintenance changes with minimal impact.

## 0.2.6 [2024-05-06]

__Enhancements__:

- Added structured error handling using `pydantic` models for file validation
  errors
- Improved error message structure with consistent field handling
- Standardized error codes to use kebab-case format (`empty-file`,
  `missing-header`, `unknown-field`)

__Fixes__:

- Fixed error location formatting for required field validation errors

__Maintenance__:

- Upgraded `python` from `3.9` to `3.10`
- Updated `fw-file` from `^2.1.1` to `^3.3.3`

## 0.2.5 [2024-04-11]

__Enhancements__:

- Added timestamp to validation error output to track when errors occurred

## 0.2.4 [2024-04-11]

__Enhancements__:

- Added automatic removal of empty CSV cell values during validation to treat
  blank cells as null values
- Added type casting validation for CSV columns to enforce single-type
  constraints per column

__Fixes__:

- Fixed CSV validation to properly handle optional fields with blank cells by
  treating them as missing values rather than empty strings

__Documentation__:

- Added comprehensive CSV typing documentation explaining how untyped CSV data
  is handled during validation
- Added table showing JSON-to-Python type mappings (`string` to `str`, `number`
  to `float`, `integer` to `int`, `boolean` to `bool`, `null` to `None`)
- Added examples of handling custom null values (`"NA"`, `"None"`) in schemas
  using `anyOf` patterns
- Added table demonstrating Python type casting behavior for common CSV string
  values
- Added explanation of Python boolean casting behavior where any non-empty
  string evaluates to `True`
- Fixed minor spacing inconsistencies in documentation

## 0.2.3 [2024-03-27]

__Enhancements__:

- Added Flywheel gear classification metadata including function, modality,
  organ, species, and therapeutic area
- Enabled job visibility with `show-job` flag in Flywheel configuration
- Added gear suite classification as "Utility"

## 0.2.2 [2024-03-27]

__Fixes__:

- Fixed `get_level_object()` method to properly return `flywheel.Group` objects
  for group-level hierarchy queries

## 0.2.1 [2024-03-26]

__Enhancements__:

- Added support for CSV file validation with header validation and row-by-row
  schema validation
- Added flywheel object validation mode to validate file metadata and parent
  container metadata
- Added configuration option to include parent containers in validation schema
- Added file tagging functionality to mark files as PASS/FAIL based on
  validation results
- Added empty file validation check for both JSON and CSV files
- Added error metadata tracking on files and containers with detailed error
  location information

__Maintenance__:

- Added CI/CD pipeline configuration using `sse-qa-ci`
- Added pre-commit hooks for code quality (`gearcheck`, `poetry_export`,
  `docker_build`, `yamllint`, `ruff`, `pytest`)
- Added `.dockerignore` to optimize Docker build context
- Added `python` `3.9` as base image in Dockerfile
- Updated dependencies: `fw-file` `^2.1.1`, `flywheel-gear-toolkit` `^0.6.10`,
  `flywheel-sdk` `17.7.0`, `argparse` `1.4.0`
- Added development dependencies: `ipython`, `pytest`, `pytest-cov`,
  `pytest-mock`

__Documentation__:

- Added comprehensive README with gear overview, usage instructions, and
  workflow diagram
- Added CONTRIBUTING.md with setup instructions and development guidelines
- Added LICENSE file (MIT)
- Added FAQ.md for common questions and errors
