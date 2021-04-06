FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install tesseract-ocr -y
RUN mkdir /hops
WORKDIR /hops
COPY requirements.txt /hops/
RUN pip install -r requirements.txt
RUN pip install docker
COPY . /hops/