# MemorialCare FHMS - Setup & Deployment Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables (.env):**
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DB_ENGINE=postgresql
   DB_NAME=memorial_care_db
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   PAYSTACK_PUBLIC_KEY=your_key
   PAYSTACK_SECRET_KEY=your_key
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run server:**
   ```bash
   python manage.py runserver
   ```

## Database Setup

### PostgreSQL
```sql
CREATE DATABASE memorial_care_db;
CREATE USER memorial_user WITH PASSWORD 'password';
ALTER ROLE memorial_user SET client_encoding TO 'utf8';
ALTER ROLE memorial_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE memorial_user SET default_transaction_devel TO ON;
GRANT ALL PRIVILEGES ON DATABASE memorial_care_db TO memorial_user;
```

### Or use SQLite (Development)
Change in settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Creating Sample Data

```python
# Create sample deceased records
python manage.py shell

>>> from fhms.models import Deceased
>>> d = Deceased.objects.create(
...     first_name="John",
...     last_name="Doe",
...     date_of_birth="1950-01-01",
...     date_of_death="2024-01-15",
...     gender="M",
...     identity_number="12345678",
...     address="123 Main St"
... )
```

## Testing

```bash
python manage.py test fhms
```

## Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn memorial_care.wsgi:application
```

### Using uWSGI
```bash
pip install uwsgi
uwsgi --http :8000 --wsgi-file memorial_care/wsgi.py
```

### Environment for Production
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=generate-a-new-strong-key
```

## Troubleshooting

### Migration Issues
```bash
python manage.py showmigrations
python manage.py migrate fhms zero  # Rollback
python manage.py makemigrations fhms
```

### Database Issues
```bash
python manage.py migrate --check
python manage.py dbshell
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

## Performance Tuning

- Enable query logging in development
- Use database connection pooling in production
- Implement caching for reports
- Use CDN for static files
- Enable gzip compression

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Update ALLOWED_HOSTS
- [ ] Use HTTPS only
- [ ] Set secure cookies
- [ ] Regular security updates
- [ ] Strong database passwords
- [ ] Regular backups
