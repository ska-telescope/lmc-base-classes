#!/usr/bin/env bash

# PACKAGE METADATA
# ----------------
if [[ $(python setup.py --name) == "UNKNOWN" ]] ; then
    echo "[error] metadata: name missing"
    exit 2
fi

if [[ $(python setup.py --version) == "0.0.0" ]] ; then
    echo "[error] metadata: version missing"
    exit 2
fi

# TODO: This presently breaks due to setuptools normalizing the package version to something that may not conform to semantic versioning in some cases.
#       On future versions of setuptools this issue should be solved (a patch was jsut merged) so we can get back to this.
#       See: https://github.com/pypa/setuptools/issues/308
if ! python setup.py --version | grep -q -E '^(([0-9]+)\.([0-9]+)\.([0-9]+)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$' ; then
    echo "[warning] metadata: version is not according to versioning standards"
    # exit 2
fi

if [[ $(python setup.py --url) == "UNKNOWN" ]] ; then
    echo "[error] metadata: url missing"
    exit 2
fi

if [[ $(python setup.py --license) == "UNKNOWN" ]] ; then
    echo "[error] metadata: license missing"
    exit 2
fi

if [[ $(python setup.py --description) == "UNKNOWN" ]] ; then
    echo "[error] metadata: description missing"
    exit 2
fi

if ! [[ $(python setup.py --classifiers) ]] ; then
    echo "[error] metadata: classifiers missing"
    exit 2
fi

echo "[info] metadata: all required tags present"

# CONFIRM TAG VERSION
# -------------------
# TODO: To implement when setuptools issue is fixed upstream
#if [[ $(python setup.py --version) != $CI_COMMIT_TAG ]] ; then
#    echo "[error] metadata: python package version differs from git tag version"
#    exit 2
#fi