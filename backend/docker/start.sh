#!/bin/bash -e

case $1 in
  "run")
    shift
    #gunicorn app:app --bind ${HOST:-0.0.0.0}:${PORT:-5000} --worker-class sanic.worker.GunicornWorker -w 3 --capture-output
    python -m sanic app.app --host=${HOST:0.0.0.0} --port=5000 --workers=4    
    ;;
  "test")
    ./test.sh "$@"
    ;;
  *)
    echo "usage: $0 [run]"
    exit 1
    ;;
esac
