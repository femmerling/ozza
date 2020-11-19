#!/bin/bash -e

case $1 in
  "run")
    shift
    echo "Starting Ozza Server at port 5000"
    echo "---------------------------------"
    echo "Activating 4 workers...."
    echo "Workers activated"
    echo "Ozza server is now serving"
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
