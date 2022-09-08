# When updating Python, you also need to update pyproject.toml:8 and poetry.lock (python-versions)
FROM python:3.10.7-slim-buster

RUN pip install --upgrade pip 'poetry==1.1.6'

ARG DEV
RUN apt update && apt install -y git
RUN if [ "${DEV}" != "no" ] ; then apt install -y curl ; fi

ARG uid=1000

RUN adduser -u ${uid} --disabled-password --disabled-login --gecos python python
USER python

ARG GITHUB_TOKEN
RUN echo "machine github.com" >> ~/.netrc && echo "login ${GITHUB_TOKEN}" >> ~/.netrc

WORKDIR /srv

COPY poetry.lock pyproject.toml /srv/
RUN poetry install --no-interaction --no-root `test "${DEV}" = "no" && echo "--no-dev" || echo ""`

COPY . /srv/

CMD ["poetry", "run", "python", "-m", "ujcatapi.main"]
