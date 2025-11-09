#!/bin/bash

cd "$(dirname "$0")"

source venv/bin/activate

celery -A tasks.celery_app worker --loglevel=info --concurrency=4

celery -A tasks.celery_app beat --loglevel=info

