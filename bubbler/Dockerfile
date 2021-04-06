FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN useradd -u 1500 -s /bin/bash runner
RUN mkdir /bubbler /bubbler/code
WORKDIR /bubbler
COPY requirements.txt /bubbler/
RUN pip install -r requirements.txt
RUN mkdir /jail
RUN cp -a /usr /jail/
RUN cp -a /lib /jail/
RUN cp -a /lib64 /jail/
RUN cp -a /bin /jail/bin

RUN chroot --userspec=runner /jail /bin/bash
COPY . /bubbler/