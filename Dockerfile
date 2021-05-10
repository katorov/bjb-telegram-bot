FROM python:3.8

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /src

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/katorov/bjb-api
RUN pip install git+https://github.com/katorov/bjb-toolkit

COPY . /src