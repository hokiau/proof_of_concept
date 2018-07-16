FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir google-cloud-spanner google-cloud-pubsub tornado==4.2

COPY . .

CMD [ "python", "./cmdline.py" ]