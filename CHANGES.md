# Changes

This is a record of all past pytask-julia releases and what went into them in reverse
chronological order. Releases follow [semantic versioning](https://semver.org/) and all
releases are available on [PyPI](https://pypi.org/project/pytask-julia) and
[Anaconda.org](https://anaconda.org/conda-forge/pytask-julia).

## 0.x.x - 2024-xx-xx

- {pull}`XX` removes tox in favor of pixi for typing.
- {pull}`56` updates pre-commit hooks.
- {pull}`54` drops support for Python 3.8 and 3.9 and adds support for Python 3.14.
- {pull}`55` switches type checking to ty.
- {pull}`31` uses pixi to provision Julia if possible.
- {pull}`32` uses trusted publishing for PyPI.
- {pull}`33` uses uuid4 to generate more robust file names for serialized arguments.
- {pull}`36` updates tests for pytask v0.5.
- {pull}`37` improves type-checking.

## 0.4.0 - 2023-10-08

- {pull}`24` prepares the release of pytask v0.4.0.

## 0.3.0 - 2023-01-24

- {pull}`16` adds mypy, refurb, and ruff.
- {pull}`18` deprecates INI configurations and aligns the package with pytask v0.3.

## 0.2.1 - 2022-04-16

- {pull}`12` includes `pyproject.toml` in the package.

## 0.2.0 - 2022-04-16

- {pull}`6` skip concurrent builds.
- {pull}`7` implements the new interface of pytask-julia with the decorator and an
  approach to serialize arguments to pass them to the executed script.
- {pull}`8` removes an unnecessary hook.

## 0.1.0 - 2022-01-19

- {pull}`2` polishes the first release of pytask-julia. (Thanks to {user}`hmgaudecker`,
  {user}`hildebrandecon`)
- {pull}`4` fixes the badges.
