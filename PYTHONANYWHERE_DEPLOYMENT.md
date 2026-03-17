# PythonAnywhere Deployment Guide

## Prerequisites
1. PythonAnywhere account (pythonanywhere.com)
2. GitHub repo with your code

## Step 1: Create Web App on PythonAnywhere

1. Login to [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Web** tab → **Add a new web app**
3. Choose: **Manual configuration** (not Flask/Django auto-setup)
4. Python version: **3.11**
5. Your domain will be: `your_username.pythonanywhere.com`

## Step 2: Clone Repository

In **Bash console** (PythonAnywhere):
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/funeral-home.git
cd funeral-home
mkvirtualenv --python=/usr/bin/python3.11 venv
pip install -r requirements.txt
```

## Step 3: Configure Database

**Option A: Use PythonAnywhere MySQL** (Free, included)
- Set up in Web app settings
- Get connection string

**Option B: Use External PostgreSQL** (Recommended)
- Keep using your local PostgreSQL details
- Or use managed PostgreSQL (ElephantSQL, Railway, etc.)

## Step 4: Set Environment Variables

In PythonAnywhere Web App settings, create/upload `.env`:
```
SECRET_KEY=generate-a-random-long-string
DEBUG=False
ALLOWED_HOSTS=your_username.pythonanywhere.com
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Step 5: Configure WSGI File

PythonAnywhere creates a WSGI file. Point it to your Django app:

**Path**: `/var/www/your_username_pythonanywhere_com_wsgi.py`

Replace content with:
```python
import os
import sys
from pathlib import Path

# Add your project to the path
path = '/home/your_username/funeral-home'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'memorial_care.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Step 6: Set Static Files

In Web App settings, add static files mapping:
- **URL**: `/static/`
- **Directory**: `/home/your_username/funeral-home/staticfiles/`

Collect static files:
```bash
cd ~/funeral-home
python manage.py collectstatic --noinput
```

## Step 7: Run Migrations

```bash
cd ~/funeral-home
python manage.py migrate
python manage.py seed_database  # Optional: load test data
```

## Step 8: Reload Web App

In PythonAnywhere Dashboard:
- Go to Web tab
- Click **Reload** next to your domain

## Access Your App

Visit: `https://your_username.pythonanywhere.com`

---

## 🔄 Continuous Deployment (After Setup)

**Each time you push to GitHub:**
```bash
cd ~/funeral-home
git pull origin main
pip install -r requirements.txt  # if deps changed
python manage.py migrate  # if new migrations
python manage.py collectstatic --noinput  # if static files changed
# Then reload in Web tab
```

Or **automate** via:
- PythonAnywhere task scheduler
- GitHub Actions (webhook to PythonAnywhere)

---

## Troubleshooting

**500 Error?**
- Check error log: Web → Error log (tail it)
- Check `/var/log/myapp.log`

**Static files not loading?**
- Run `python manage.py collectstatic --noinput`
- Verify path in Web app settings

**Database connection error?**
- Verify `DATABASE_URL` in `.env`
- Test with: `psql $DATABASE_URL`

**Module not found?**
- Ensure venv is activated
- Check Python path in WSGI file

## Database Options

1. **PythonAnywhere MySQL** - Free, included
2. **External PostgreSQL** - Better for Django
   - ElephantSQL (free tier)
   - Railway.app
   - Heroku Postgres
   - Your local PostgreSQL (private network only)

---

Ready to deploy? Follow steps 1-8 above!
