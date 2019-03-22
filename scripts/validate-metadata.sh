#!/usr/bin/env bash

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

echo "[info] all required metadata tags present"

