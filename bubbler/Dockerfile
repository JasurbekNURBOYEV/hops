FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN useradd -s /bin/bash runner
USER root
RUN mkdir /bubbler /bubbler/code
WORKDIR /bubbler
COPY requirements.txt /bubbler/
RUN pip install -r requirements.txt
USER runner
COPY . /bubbler/