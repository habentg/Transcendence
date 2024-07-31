#!/bin/sh

echo "RUNNING MIGRATIONS"
python manage.py makemigrations
python manage.py migrate

echo "RUNNING SERVER"
python manage.py runserver 0.0.0.0:8000