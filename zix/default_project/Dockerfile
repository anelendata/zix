FROM python:3.9-slim

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install --yes --no-install-recommends ffmpeg

# RUN install sqlcipher libsqlcipher0 libsqlcipher-dev
# RUN pip3 install pysqlcipher3

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install gunicorn==20.1.0
RUN pip install uvicorn==0.19.0

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 people_reach.backend.main:app

# CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout=600  people_reach.backend.main:app
# https://stackoverflow.com/a/70944554
CMD ["uvicorn", "app.server.main:app", "--host", "0.0.0.0", "--port", "8080"]
