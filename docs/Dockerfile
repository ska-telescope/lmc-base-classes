FROM readthedocs/build:latest

COPY docs/requirements.txt .
RUN python3 -m pip install --exists-action=w --no-cache-dir --disable-pip-version-check -r requirements.txt

ENTRYPOINT python3 -m sphinx -T -E -b html -d project/docs/build/doctrees project/docs/src project/docs/build/html
