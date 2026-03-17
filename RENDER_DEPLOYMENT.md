# Render Deployment Guide

## Prerequisites
1. GitHub account with repo pushed
2. Render account (render.com)
3. Existing Render PostgreSQL database OR let Render create one

## Deployment Steps

### 1. Connect Repository
- Go to [Render Dashboard](https://dashboard.render.com)
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Name: `memorialcare`
- Branch: `main` (or your branch)

### 2. Configure Environment Variables
Render will auto-create from `render.yaml`, but you may need to set:

- `SECRET_KEY`: Generate a random string (Render creates this automatically)
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `*.render.com` (or your custom domain)

### 3. Database
- Render will create PostgreSQL from `render.yaml`
- Connection string automatically set as `DATABASE_URL`

### 4. Deploy
- Click "Create Web Service"
- Render will:
  - Run `build.sh` (installs dependencies, collects static, runs migrations)
  - Start `gunicorn` with your app

### 5. First Deploy Checklist
- [ ] Check build logs for errors
- [ ] Verify migrations ran (`python manage.py migrate`)
- [ ] Test login at your Render URL
- [ ] Seed test data if needed: `python manage.py seed_database`

## Troubleshooting

**Migrations not running:**
```bash
# Run in Render shell
python manage.py migrate
```

**Static files not showing:**
```bash
# Rebuild static files
python manage.py collectstatic --no-input
```

**Database issues:**
- Check PostgreSQL connection URL in Environment
- Ensure firewall allows Render service

## Custom Domain (Optional)
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records per Render instructions

## Continuing Development

### Local Changes
```bash
git add .
git commit -m "Feature: description"
git push
```

### Render Auto-Updates
- Each push triggers new deployment
- Previous version remains available as fallback

### Database Backups
- Render PostgreSQL has automated backups
- Manual backup: Render Dashboard → Database → Backup

## Adding Features Post-Deployment

1. Develop locally
2. Test thoroughly
3. Push to GitHub (auto-deploys)
4. No data loss—PostgreSQL persists between deployments
5. Can add Paystack/migrations without redeploying from scratch

## Support
- Render Docs: render.com/docs
- Django Deployment: docs.djangoproject.com/en/6.0/howto/deployment/
- Check Render logs: Dashboard → Web Service → Logs
