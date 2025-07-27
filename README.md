# Lunch

[@zookinheimer's](https://github.com/zookinheimer/Lunch/commits?author=zookinheimer) masterpiece. Gonna fill in the blanks and/or add tooling.

— [@pythoninthegrass](https://github.com/pythoninthegrass)

## Setup

* Install 
  * [uv](https://docs.astral.sh/uv/getting-started/installation/)
  * [docker compose](https://docs.docker.com/compose/install/)
  * [editorconfig](https://editorconfig.org/)
  * [playwright](https://playwright.dev/python/docs/intro#installation)

## Quickstart

### Clone repo

```bash
# clone repo
git clone https://github.com/pythoninthegrass/lunch.git

# change directory
cd lunch/
```

### Python virtual environment

```bash
# create virtual environment
python -m venv .venv

# activate virtual environment
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run program

```bash
python main.py
```

### Quit program

```bash
ctrl + c
```

### Deactivate virtual environment

```bash
deactivate
```

## Development

### Additional tooling

Additional tooling includes but is not limited to:

#### mise

* Install [mise](https://mise.jdx.dev/installing-mise.html)
* Usage

    ```bash
    # install all dependencies in .tool-versions
    mise install

    # install specific deps
    mise use uv@0.7.18
    ```

#### uv

* Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if not using `mise`
* Usage
   
    ```bash
    # create a venv w/system python (./.venv)
    uv venv

    # activate venv
    source .venv/bin/activate

    # install with extras (for development)
    uv pip install -r pyproject.toml --all-extras

    # add new dependency
    uv add <package>

    # add optional dependency to dev group
    uv add --optional dev <package>

    # export requirements.txt from pyproject.toml
    uv pip freeze > requirements.txt

    # run program
    python main.py

    # exit virtual environment
    deactivate
    ```

#### VSCode

* Install [VSCode](https://code.visualstudio.com/download)
* Setup [VSCode settings](.vscode/launch.json)
  * Handles debug settings for generic python programs as well as others (e.g., django, flask, etc.)
* Dev Containers
  * [Command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) (⇧⌘P) > Dev Containers: Reopen in Container
  * F5 for debug
    * May need to select interpreter (e.g., `/opt/venv/bin/python`) first

#### ruff

* Installed via `uv` or `pip`
* Add VSCode plugin for [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
  * **Optional**: disable pylance in favor of ruff in [repo settings](.vscode/settings.json)
    ```json
    "python.analysis.ignore": [
      "*"
    ],
    ```
* Usage
    ```bash
    # run linter
    ruff check <.|main.py>      # `--fix` arg to use a one-liner 

    # run linter and fix issues
    ruff fix .

    # run tests
    ruff

    # run tests with coverage
    ruff --coverage

    # run tests with coverage and open in browser
    ruff --coverage --open
    ```

#### pre-commit

```bash
# install pre-commit dev dependency
uv pip install -r pyproject.toml --all-extras

# install pre-commit hooks
pre-commit install

# update
pre-commit autoupdate
```

#### editorconfig

Handles formatting of files. [Install the editorconfig plugin](https://editorconfig.org/#download) for your editor of choice.

#### Renovate

* [Renovate](https://docs.renovatebot.com/) is a GitHub tool that automatically creates pull requests to keep dependencies up to date.

## TODO

See [TODO.md](TODO.md).

## Further Reading

* [flet](https://flet.dev/)
