FROM readthedocs/build:latest

ARG dir=docs
ENV dir=${dir}

ENTRYPOINT python3 -m sphinx -T -E -b html -d project/docs/build/doctrees project/docs/src project/docs/build/html
