FROM tiangolo/uwsgi-nginx-flask:python3.10

COPY requirements.txt ./

RUN apt-get update && \
    pip install -r ./requirements.txt

COPY ./ /app