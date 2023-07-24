FROM alpine:3.18 as base
RUN apk add --no-cache git
WORKDIR /app/gpt-code-ui/
COPY . .

FROM node:20-alpine as frontend
COPY --from=base /app /app
WORKDIR /app/gpt-code-ui/frontend
RUN npm install && npm run build


FROM python:3.10-slim-buster as backend
RUN pip3 install --upgrade pip wheel
COPY --from=base /app/gpt-code-ui /app
WORKDIR /app
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN pip install -r requirements.txt
COPY --from=frontend /app/gpt-code-ui/frontend/dist /app/gpt_code_ui/webapp/static
RUN python3 setup.py sdist bdist_wheel && \
    python3 setup.py install && \
    rm -rf /app/frontend && \
    rm -rf /app/notes && \
    rm -rf /app/scripts && \
    rm -rf /app/gpt_code_ui/webapp/static
WORKDIR /app/gpt_code_ui/
ENTRYPOINT gptcode