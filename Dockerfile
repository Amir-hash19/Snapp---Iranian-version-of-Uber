FROM python:3.12.3-slim



LABEL maintainer="amirhosein.hydri1381@gmail.com"


ENV PYTHONUNBUFFERED=1


WORKDIR /usr/src/app/app


COPY ./requirements.txt .


RUN pip install --upgrade pip \
    && pip install -r requirements.txt

    
COPY ./app .

