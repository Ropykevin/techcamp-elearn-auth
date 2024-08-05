FROM tiangolo/uwsgi-nginx-flask:python3.11
COPY requirements.txt /tmp/
ENV OAUTHLIB_INSECURE_TRANSPORT=0
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt
RUN apt-get update
COPY ./app /app
