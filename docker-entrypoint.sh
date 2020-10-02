#!/bin/bash

## Nginx
service nginx start

cd /src
make clean

## Start server
make up WORKERS=$WORKERS
