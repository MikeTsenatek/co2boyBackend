#!/bin/bash

set -e

exec python3 /code/main.py -b &
exec python3 /code/main.py -w 
