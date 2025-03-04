# Chop Chop

Chop continuous stream of simulated data into more realistic LISA data packets.

## Usage

To use this package, you need to install it first. You can do so by cloning the
repository and running the setup script.

```bash
git clone git@gitlab.in2p3.fr:LISA/ogip-eg/lolipops.git
cd lolipops
pip install .
```

Refer to the documentation for more information.

## Contribute

### Report an issue

We use the issue-tracking management system associated with the project provided
by Gitlab. If you want to report a bug or request a feature, open an issue at
<https://gitlab.in2p3.fr/lisa_irfu/chopchop/-/issues>. You may also thumb-up
or comment on existing issues.

### Development environment

This project uses [Poetry](https://python-poetry.org/) to manage dependencies
and packaging. Poetry can prepare a virtual environment for developement, and is
used to build the package. After you clones the project, run

```bash
poetry install
```

Refer to the [Poetry documentation](https://python-poetry.org/docs/) for more
information.

We recommend you install pre-commit hooks to detect errors before you even
commit.

```bash
pre-commit install
```

### Syntax

We enforce PEP 8 (Style Guide for Python Code) with Pylint syntax checking, and
code formatting with Black. Both are implemented in the continuous integration
system, and merge requests cannot be merged if it fails. Pre-commit hooks will
also run Black before you commit.

You can run them locally with

```bash
pylint src
black .
```

Note that VS Code can be configured to run Black when saving a file, and to
display Pylint errors in the editor.

### Unit tests

Correction of the code is checked by the pytest testing framework. It is
implemented in the continuous integration system, but we recommend you run the
tests locally before you commit, with

```bash
python -m pytest
```

Note that VS Code can be configured to run the tests easily.
