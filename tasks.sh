#!/usr/bin/env bash

# make the script fail when one item fails
set -o errexit

cd $(dirname $0)

FORMAT=false
STYLE=false
TYPE=false
UNIT=false
FIX=false
TDD=false
COVERAGE=false

exit_and_show_usage() {
  echo "Usage: $0 [-fstucxd]" 1>&2
  exit 1
}

while getopts fstucxd OPT
do
  case $OPT in
    # task types
    'f' ) FORMAT=true ;;
    's' ) STYLE=true ;;
    't' ) TYPE=true ;;
    'u' ) UNIT=true ;;
    'c' ) COVERAGE=true ;;
    # options
    'x' ) FIX=true ;;
    'd' ) TDD=true ;;
    *) exit_and_show_usage;
  esac
done

# if no task is specified default to all tasks
if [ "$FORMAT" = false ] && [ "$STYLE" = false ] && [ "$TYPE" = false ] && [ "$UNIT" = false ] && [ "$COVERAGE" = false ]; then
  FORMAT=true
  STYLE=true
  TYPE=true
  UNIT=true
  COVERAGE=true
fi

autoformat() {
  BLACK_FLAG='--check'
  ISORT_FLAG='--check-only'

  if $FIX; then
    BLACK_FLAG=''
    ISORT_FLAG=''
  fi

  echo '---- format (black) ----'
  poetry run black . $BLACK_FLAG

  echo '---- format (isort) ----'
  poetry run isort ujcatapi tests $ISORT_FLAG
}

check_style() {
  echo '---- style ----'
  poetry run flake8 ujcatapi tests
}

check_type() {
  echo '---- type ----'
  poetry run mypy ujcatapi tests
}

check_unit() {
  # default to coverage mode
  PYTEST_FLAGS='--cov=ujcatapi --ignore=ujcatapi --cov-report=term-missing --cov-report=xml'

  if $TDD; then
    # in TDD mode, fail fast and don't bother with coverage
    PYTEST_FLAGS='-x'
  fi
  echo '---- unit test ----'
  poetry run py.test -s -vv $PYTEST_FLAGS .
}

check_coverage() {
  echo '---- coverage ----'
  if $UNIT; then
    # avoid duplicated output
    poetry run coverage report --fail-under=90 1> /dev/null && rc=$? || rc=$?
  else
    poetry run coverage report --fail-under=90 && rc=$? || rc=$?
  fi
  if [ $rc == 0 ]; then
    echo "Test coverage check OK."
  else
    echo "Test coverage check failed. Coverage cannot fall under 90%"
    exit $rc
  fi
}

if $FORMAT; then
  autoformat
fi
if $STYLE; then
  check_style
fi
if $TYPE; then
  check_type
fi
if $UNIT; then
  check_unit
fi
if $COVERAGE; then
  check_coverage
fi
