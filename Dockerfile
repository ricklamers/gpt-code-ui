FROM python:3.9

WORKDIR /usr/src/app

COPY ./lib ./lib
RUN pip install -e  ./lib
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


