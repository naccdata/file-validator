# Contributing

## Getting started

1. Follow instructions to [install poetry](https://python-poetry.org/docs/#installation).
2. Follow instructions to [install pre-commit](https://pre-commit.com/#install)

After cloning the repo:

1. Run `poetry install` to install project and all dependencies
(see __Dependency management__ below)
2. Run `pre-commit install` to install pre-commit hooks
(see __Linting and Testing__ below)

(If you need to change your python version:)

```shell
poetry env use <path/to/your/python/executable>
poetry update
```

## Dependency management

This gear uses [`poetry`](https://python-poetry.org/) to manage dependencies,
develop, build and publish.

### Dependencies

Dependencies are listed in the `pyproject.toml` file.

#### Managing dependencies

* Adding: Use `poetry add [--dev] <dep>`
* Removing: Use `poetry remove [--dev] <dep>`
* Updating: Use `poetry update <dep>` or `poetry update` to update all deps.
  * Can also not update development dependencies with `--no-dev`
  * Update dry run: `--dry-run`

#### Using a different version of python

Poetry manages virtual environments and can create a virtual environment
with different versions of python,
however that version must be installed on the machine.

You can configure the python version
by using `poetry env use <path/to/executable>`

#### Helpful poetry config options

[See full options here](https://python-poetry.org/docs/configuration/#available-settings).

List current config: `poetry config --list`

* `poetry config virtualenvs.in-project <true|false|None>`:
create virtual environment inside project directory
* `poetry config virtualenvs.path <path>`: Path to virtual environment directory.

## Linting and Testing

Local linting and testing scripts
are managed through [`pre-commit`](https://pre-commit.com/).
Pre-commit allows running hooks which can be defined locally, or in other
repositories. Default hooks to run on each commit:

* check-json: JSON syntax validator
* check-toml: TOML syntax validator (for pyproject.toml)
* pretty-format-json: Pretty print json
* no-commit-to-branch: Don't allow committing to master
* isort-poetry: Run isort in poetry venv
* black-poetry: Run black in poetry venv
* pytest-poetry: Run pytest in poetry venv

These hooks will all run automatically on commit, but can also be run manually
or just be disabled.

### pre-commit usage

* Run hooks manually:
  * Run on all files: `pre-commit run -a`
  * Run on certain files: `pre-commit run --files test/*`
* Update (e.g. clean and install) hooks: `pre-commit clean && pre-commit install`
* Disable all hooks: `pre-commit uninstall`
* Enable all hooks: `pre-commit install`
* Skip a hook on commit: `SKIP=<hook-name> git commit`
* Skip all hooks on commit: `git commit --no-verify`

## Adding a contribution

Every contribution should be
associated with a ticket on the GEAR JIRA board, or be a hotfix.
You should contribute by creating
a branch titled with either `hotfix-<hotfix_name` or `GEAR-<gear_num>-<description>`.
For now, other branch names will be accepted,
but soon branch names will be rejected
if they don't follow this pattern.

When contributing, make a Merge Request against the main branch.

### Merge requests

The merge request should contain at least two things:

1. Your relevant change
2. Update the corresponding entry under `docs/release_notes.md`

Adding the release notes does two things:

1. It makes it easier for the
reviewer to identify what relevant changes
they should expect and look for in the MR, and
2. It makes it easier to create a release.

### Creating a release

When your merge request is reviewed and approved, you should pull from main locally:

```bash
git checkout main # Locally change to main branch
git pull origin main # Locally pull updates from main branch
```

Then update the versions accordingly:

1. Update poetry version: `poetry version <new_version>`
2. Update the version in the manifest:
    1. Update `"version"` key with new version
    2. Update `"custom.gear-builder.image"` key with new image version
3. Commit version changes

Then you can tag the version and push:

```bash
git tag <new_version>
git push origin main
git push origin --tags
```

Once you've pushed tags,
you can go to the gitlab UI -> Project Overview -> Releases and
create a new release.
You can copy the release notes that are
already populated in the `docs/release_notes.md` document.
