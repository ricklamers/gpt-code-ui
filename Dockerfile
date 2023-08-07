FROM node:16.16.0-alpine AS uibuild
RUN apk add --no-cache make rsync
WORKDIR /
COPY Makefile ./
COPY frontend/ ./frontend
COPY setup.py ./
COPY gpt_code_ui/webapp/static ./gpt_code_ui/webapp/static
RUN ls -al .
RUN make compile_frontend


FROM python:3.10-slim as backendbuild
# working directory
WORKDIR /
RUN pip install "numpy>=1.24,<1.25" "dateparser>=1.1,<1.2" "pandas>=1.5,<1.6" "geopandas>=0.13,<0.14" "tabulate>=0.9.0<1.0" "PyPDF2>=3.0,<3.1" "pdfminer>=20191125,<20191200" "pdfplumber>=0.9,<0.10" "matplotlib>=3.7,<3.8"
COPY setup.py ./
COPY README.md ./
RUN pip install -e .

COPY gpt_code_ui/ ./gpt_code_ui

# Inject frontend into backend resources to be served from there
COPY --from=uibuild /frontend/dist/ ./frontend/dist

EXPOSE 8080

CMD ["python", "gpt_code_ui/main.py"]
