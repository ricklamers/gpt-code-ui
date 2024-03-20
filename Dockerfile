FROM node:16.16.0-alpine AS uibuild
RUN apk add --no-cache make rsync
RUN mkdir frontendbuild
WORKDIR /frontendbuild
COPY Makefile ./
COPY frontend/ ./frontend
COPY pyproject.toml ./
COPY gpt_code_ui/webapp/static ./gpt_code_ui/webapp/static
RUN ls -al .
RUN make compile_frontend


FROM python:3.10-slim as backendbuild
# runtime binary dependencies
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libxrender1 \
        libxext6 \
        curl \
    ; \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.7.1

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN mkdir backendbuild
WORKDIR /backendbuild

# first install only dependencies
COPY poetry.lock pyproject.toml ./
RUN touch README.md
RUN poetry install --without dev --without devtools --no-root --no-ansi && rm -rf $POETRY_CACHE_DIR


# install actual project
COPY run_with_app_service_config.py ./
COPY gpt_code_ui/ ./gpt_code_ui
RUN poetry install --without dev --without devtools --no-ansi && rm -rf $POETRY_CACHE_DIR

# Inject frontend into backend resources to be served from there
COPY --from=uibuild /frontendbuild/frontend/dist/ ./gpt_code_ui/webapp/static

RUN mkdir workspace
RUN chmod 0777 workspace
RUN touch app.log
RUN chmod 0777 app.log

RUN ls -al .
RUN ls -al ./gpt_code_ui
RUN which python

EXPOSE 8080

# restrict access to /proc to make it more difficult to access other proccesses, see https://superuser.com/a/704035
RUN cat /etc/fstab
RUN ls -al /etc/fstab
RUN echo "proc /proc proc nosuid,nodev,noexec,hidepid=2 0 0" >> /etc/fstab
RUN cat /etc/fstab

RUN adduser --no-create-home gpt_code_ui
USER gpt_code_ui

CMD ["python", "./run_with_app_service_config.py", "./gpt_code_ui/main.py"]
