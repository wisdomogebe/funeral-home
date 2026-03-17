web: gunicorn memorial_care.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
release: python manage.py migrate && python manage.py collectstatic --no-input
