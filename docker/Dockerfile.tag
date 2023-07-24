FROM alpine:3.18 as base
RUN apk add --no-cache wget
WORKDIR /app
ARG VERSION=0.42.35
RUN wget https://github.com/ricklamers/gpt-code-ui/archive/refs/tags/v${VERSION}.tar.gz
RUN tar zxvf v${VERSION}.tar.gz && rm v${VERSION}.tar.gz
RUN mv gpt-code-ui-${VERSION} gpt-code-ui


FROM node:20-alpine as frontend
COPY --from=base /app /app
WORKDIR /app/gpt-code-ui/frontend
RUN npm install && npm run build


FROM python:3.10-slim-buster as backend
RUN pip3 install --upgrade pip wheel
COPY --from=base /app/gpt-code-ui /app
WORKDIR /app
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN pip install Flask==2.3.2 Flask-Cors==3.0.10 requests==2.31.0 snakeMQ==1.6 ipykernel==6.23.1 python-dotenv==1.0.0 pandas==1.5.3
COPY --from=frontend /app/gpt-code-ui/frontend/dist /app/gpt_code_ui/webapp/static
RUN python3 setup.py sdist bdist_wheel && \
    python3 setup.py install && \
    rm -rf /app/frontend && \
    rm -rf /app/notes && \
    rm -rf /app/scripts && \
    rm -rf /app/gpt_code_ui/webapp/static
WORKDIR /app/gpt_code_ui/
ENTRYPOINT gptcode

# for easier using
RUN pip3 install matplotlib
RUN pip3 install geopandas