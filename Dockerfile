FROM node:16.16.0-alpine AS uibuild
RUN apk add --no-cache make rsync
RUN mkdir frontendbuild
WORKDIR /frontendbuild
COPY Makefile ./
COPY frontend/ ./frontend
COPY setup.py ./
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
    ; \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools
RUN pip install \
        "ipykernel>=6,<7" \
        "numpy>=1.24,<1.25" \
        "dateparser>=1.1,<1.2" \
        "pandas>=1.5,<1.6" \
        "geopandas>=0.13,<0.14" \
        "tabulate>=0.9.0<1.0" \
        "PyPDF2>=3.0,<3.1" \
        "pdfminer>=20191125,<20191200" \
        "pdfplumber>=0.9,<0.10" \
        "matplotlib>=3.7,<3.8" \
        "openpyxl>=3.1.2,<4" \
        "rdkit>=2023.3.3" \
        "scipy>=1.11.1" \
        "scikit-learn>=1.3.0"

RUN mkdir backendbuild
WORKDIR /backendbuild
COPY gpt_code_ui/ ./gpt_code_ui
COPY setup.py ./
COPY README.md ./
RUN pip install -e .

# Inject frontend into backend resources to be served from there
COPY --from=uibuild /frontendbuild/frontend/dist/ ./gpt_code_ui/webapp/static

COPY run_with_app_service_config.py ./

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

RUN adduser --no-create-home codeimpact
USER codeimpact

CMD ["python", "./run_with_app_service_config.py", "./gpt_code_ui/main.py"]
