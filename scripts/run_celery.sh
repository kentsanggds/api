#!/bin/bash
set +x

if [ -z "$VIRTUAL_ENV" ] && [ -d venv ]; then
  echo 'activate venv for celery'
  source ./venv/bin/activate
  nooutput=' >&- 2>&- <&- &'
fi

# kill existing celery workers
ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9

eval "celery -A run_celery.celery worker --loglevel=INFO --concurrency=1"$nooutput
