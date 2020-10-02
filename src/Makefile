#!/bin/bash

SHELL=/bin/bash

clean:
	find . -name '*.pyc' -delete

up:
	python manage.py makemigrations
	python manage.py migrate
	gunicorn --timeout 30 --workers $(WORKERS) -b 127.0.0.1:8000 pyronear.wsgi:application