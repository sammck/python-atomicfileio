#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"

if ! command -v pip3 &> /dev/null; then
  sudo apt install -y python3-pip
fi

if ! ( pip3 list | grep -G '^virtualenv ' > /dev/null ) ; then
  pip3 install --user virtualenv
fi

if ! ( pip3 list | grep -G '^virtualenv ' > /dev/null ) ; then
  pip3 install --user virtualenv
fi

PYENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$PYENV_DIR" ]; then
  python3 -m venv "$PYENV_DIR"
fi

ACTIVATE="$PYENV_DIR/bin/activate"
PYTHON="$PYENV_DIR/bin/python"
PIP3="$PYENV_DIR/bin/pip3"

if [ ! -e "$ACTIVATE" ]; then
  if [ -e "$ACTIVATE-orig" ]; then
    mv "$ACTIVATE-orig" "$ACTIVATE"
  else
    echo "venv activate script does not exist at $ACTIVATE" >&2
    exit 1
  fi
fi

if [[ ! -L "$ACTIVATE" ]]; then
  echo "hooking virtualenv activate script..." >&2
  mv "$ACTIVATE" "$ACTIVATE-orig"
  ln -s "../../env-vars.sh" "$ACTIVATE"
else
  echo "virtualenv activate script $ACTIVATE is already a symlink"
fi

if ! ( "$PIP3" list | grep -G '^wheel ' > /dev/null ) ; then
  "$PIP3" install wheel
fi

if ! ( "$PIP3" list | grep -G '^setuptools ' > /dev/null ) ; then
  "$PIP3" install setuptools
fi

if ! ( "$PIP3" list | grep -G '^Sphinx ' > /dev/null ) ; then
  "$PIP3" install sphinx
fi

if ! ( "$PIP3" list | grep -G '^sphinx-rtd-theme ' > /dev/null ) ; then
  "$PIP3" install sphinx_rtd_theme
fi

"$PIP3" install -r requirements.txt

. "$SCRIPT_DIR/env-vars.sh"

"$PIP3" install --upgrade -e .

echo "Python is at $PYTHON"
echo "Python version is $($PYTHON --version)"
