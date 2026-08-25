#!/bin/bash
set -e

if [ -n "$POSTGRES_DB" ]; then
  echo "Waiting for postgres at $POSTGRES_HOST:$POSTGRES_PORT..."
  while ! (echo > /dev/tcp/${POSTGRES_HOST:-db}/${POSTGRES_PORT:-5432}) 2>/dev/null; do
    sleep 1
  done
  echo "Postgres is up."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear || true

if [ "$DJANGO_CREATE_SUPERUSER" = "True" ]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@supmeal.local', 'admin1234')
" || true
fi

if [ "$DJANGO_DEBUG" = "True" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  exec gunicorn supmeal.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
