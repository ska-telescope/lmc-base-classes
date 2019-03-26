#!/usr/bin/env bash

# PACKAGE METADATA
# ----------------
if [[ $(python setup.py --name) == "UNKNOWN" ]] ; then
    echo "[err] metadata: name missing"
    exit 2
fi

if [[ $(python setup.py --version) == "0.0.0" ]] ; then
    echo "[err] metadata: version missing"
    exit 2
fi

if ! python setup.py --version | grep -q -E '^((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$' ; then
    echo "[err] metadata: version is not according to versioning standards"
    exit 2
fi


if [[ $(python setup.py --url) == "UNKNOWN" ]] ; then
    echo "[err] metadata: url missing"
    exit 2
fi

if [[ $(python setup.py --license) == "UNKNOWN" ]] ; then
    echo "[err] metadata: license missing"
    exit 2
fi

if [[ $(python setup.py --description) == "UNKNOWN" ]] ; then
    echo "[err] metadata: description missing"
    exit 2
fi

if ! [[ $(python setup.py --classifiers) ]] ; then
    echo "[err] metadata: classifiers missing"
    exit 2
fi

echo "[info] metadata: all required tags present"

# CONFIRM TAG VERSION
# -------------------
# TODO: This presently breaks due to setuptools normalizing the package version to something that may not conform to semantic versioning in some cases.
#       On future versions of setuptools this issue should be solved (a patch was jsut merged) so we can get back to this.
#       See: https://github.com/pypa/setuptools/issues/308
#if [[ $(python setup.py --version) != $CI_COMMIT_TAG ]] ; then
#    echo "[err] metadata: python package version differs from git tag version"
#    exit 2
#fi