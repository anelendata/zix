FROM python:3.9-slim

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install --yes --no-install-recommends ffmpeg

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./
RUN pip install uv
RUN uv pip install --system .
RUN uv pip install --system gunicorn==20.1.0

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD ["uvicorn", "app.server.main:app", "--host", "0.0.0.0", "--port", "8080"]
