#!/bin/bash

# this is tweaked to resolve symlinks first before getting dir
SCRIPT_DIR="$( cd "$( dirname "$(realpath "${BASH_SOURCE[0]}")" )" &> /dev/null && pwd )"

#echo "env-vars.sh script dir=$SCRIPT_DIR"

PYTHON_VENV="$SCRIPT_DIR/venv"
if [ "$VIRTUAL_ENV" != "$PYTHON_VENV" ]; then
  if [ -n "$VIRTUAL_ENV" ]; then
    echo "Overriding old python virtualenv (at $VIRTUAL_ENV ) to $PYTHON_VENV" >&2
  fi
  if [ -f "$PYTHON_VENV/bin/activate-orig" ]; then
    . "$PYTHON_VENV/bin/activate-orig"
  else
    echo "original virtualenv activate symlink missing from $PYTHON_VENV/bin/activate-orig" >&2
  fi
fi

if [ -f "$SCRIPT_DIR/.dev-env" ]; then
  while IFS="" read -r p || [ -n "$p" ]; do
    eval "export '$p'"
  done < "$SCRIPT_DIR/.dev-env"
fi

export FLASK_APP=flaskr
export FLASK_ENV=development
