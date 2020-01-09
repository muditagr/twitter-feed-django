
release: python manage.py migrate --noinput
web: gunicorn twitterapp_11577.wsgi --timeout 600 --log-file - --log-level debug
