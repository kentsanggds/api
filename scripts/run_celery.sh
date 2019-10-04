#!/bin/bash
set +x

ENV=development

if [ ! -z "$1" ]; then
    ENV=$1
fi

if [ -z "$VIRTUAL_ENV" ] && [ -d venv ]; then
  echo 'activate venv for celery'
  source ./venv/bin/activate
  nooutput=' >&- 2>&- <&- &'
fi

# kill existing celery workers
ps auxww | grep "celery worker-$ENV" | awk '{print $2}' | xargs kill -9

eval "celery -A run_celery.celery worker --loglevel=INFO -n worker-$ENV@%h --concurrency=1"$nooutput
eval "celery -A run_celery.celery flower"$nooutput
