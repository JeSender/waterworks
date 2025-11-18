# 🚂 Railway Deployment Guide - Balilihan Waterworks

This guide will help you deploy the Balilihan Waterworks Management System to Railway.

---

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code must be pushed to GitHub
3. **Database Ready**: PostgreSQL will be provided by Railway

---

## 🚀 Deployment Steps

### Step 1: Connect GitHub Repository

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `JeSender/waterworks`
5. Railway will automatically detect it's a Django project

---

### Step 2: Add PostgreSQL Database

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL instance
4. The database credentials will be available as environment variables

---

### Step 3: Configure Environment Variables

Add these variables in Railway → **Variables** tab:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=waterworks.settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=*.railway.app,yourdomain.com

# Database (Auto-provided by Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Static Files
STATIC_ROOT=/app/staticfiles
STATIC_URL=/static/

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (Optional - for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

### Step 4: Create Required Files

#### 1. **Procfile** (for Railway)
Create in project root:
```
web: gunicorn waterworks.wsgi --log-file -
release: python manage.py migrate --no-input && python manage.py collectstatic --no-input
```

#### 2. **runtime.txt** (specify Python version)
```
python-3.11.6
```

#### 3. **railway.json** (Railway configuration)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn waterworks.wsgi --log-file -",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### Step 5: Update Django Settings for Production

Add to your `waterworks/settings.py`:

```python
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Database
# Use Railway's DATABASE_URL if available
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local SQLite fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

---

### Step 6: Update requirements.txt

Ensure these packages are in your `requirements.txt`:

```txt
Django>=4.2,<5.0
gunicorn>=21.2.0
psycopg2-binary>=2.9.9
dj-database-url>=2.1.0
whitenoise>=6.6.0
python-decouple>=3.8
Pillow>=10.1.0
```

---

### Step 7: Deploy to Railway

1. **Commit the changes**:
   ```bash
   git add Procfile runtime.txt railway.json requirements.txt
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Railway Auto-Deploy**:
   - Railway will detect the push and automatically deploy
   - Monitor the deployment in Railway dashboard
   - Check the logs for any errors

3. **Wait for Build**:
   - The build process takes 2-5 minutes
   - Railway will run migrations automatically
   - Static files will be collected

---

### Step 8: Create Superuser (Admin Account)

1. In Railway dashboard, go to your project
2. Click on your service → **"Settings"**
3. Scroll down to **"One-off Commands"**
4. Run this command:
   ```bash
   python manage.py createsuperuser
   ```
5. Follow the prompts to create admin account

**Or** use Railway CLI:
```bash
railway run python manage.py createsuperuser
```

---

### Step 9: Load Test Data (Optional)

If you want to populate with test data:

```bash
# Via Railway CLI
railway run python manage.py shell

# Then in Django shell:
from consumers.models import *
from django.contrib.auth.models import User

# Create barangays
barangays = ['Anoling', 'Baja', 'Boyog Norte', 'Boyog Sur', 'Cabacngan',
             'Cahayag', 'Cambigsi', 'Candasig', 'Canlangit', 'Poblacion']
for name in barangays:
    Barangay.objects.get_or_create(name=name)

# Create meter brands
brands = ['Sensus', 'Itron', 'Neptune', 'Badger Meter', 'Elster']
for brand in brands:
    MeterBrand.objects.get_or_create(name=brand)

# Create system settings
SystemSetting.objects.get_or_create(
    id=1,
    defaults={
        'residential_rate_per_cubic': 22.50,
        'commercial_rate_per_cubic': 25.00,
        'fixed_charge': 50.00
    }
)
```

---

### Step 10: Access Your Deployment

1. **Get Your URL**: Railway provides a URL like `https://waterworks-production-xxxx.railway.app`
2. **Test the Dashboard**: Visit `/` to see your dashboard
3. **Login to Admin**: Visit `/admin` and login with superuser credentials

---

## 🔍 Troubleshooting

### Issue: Static Files Not Loading

**Solution:**
```bash
railway run python manage.py collectstatic --no-input
```

### Issue: Database Connection Error

**Solution:**
1. Check if PostgreSQL service is running
2. Verify `DATABASE_URL` variable is set
3. Check Railway logs for connection errors

### Issue: Migration Failed

**Solution:**
```bash
railway run python manage.py migrate --run-syncdb
```

### Issue: 500 Internal Server Error

**Solution:**
1. Check Railway logs: Click service → **Deployments** → **View Logs**
2. Enable debug temporarily: Set `DEBUG=True` in environment variables
3. Check `ALLOWED_HOSTS` includes your Railway domain

---

## 📊 Monitoring & Logs

### View Logs
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# View logs
railway logs
```

### Check Service Status
- Go to Railway Dashboard
- Click on your service
- Monitor CPU, Memory, and Network usage

---

## 🔄 Continuous Deployment

Railway automatically deploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Railway will automatically deploy
```

---

## 🌐 Custom Domain (Optional)

1. In Railway dashboard, go to your service
2. Click **Settings** → **Domains**
3. Click **"Generate Domain"** or **"Custom Domain"**
4. Follow instructions to configure DNS

---

## 📱 Environment-Specific URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| Development | `http://localhost:8000` | Local testing |
| Production | `https://your-app.railway.app` | Live deployment |
| Admin Panel | `/admin` | Django admin |
| API (if any) | `/api/` | REST API endpoints |

---

## ✅ Post-Deployment Checklist

- [ ] PostgreSQL database is connected
- [ ] Migrations have run successfully
- [ ] Static files are loading correctly
- [ ] Superuser account created
- [ ] Test data loaded (optional)
- [ ] Dashboard is accessible
- [ ] All features working as expected
- [ ] SSL certificate is active
- [ ] Environment variables are secure
- [ ] Backups are configured

---

## 🔐 Security Best Practices

1. **Never commit** `.env` files or secrets to GitHub
2. **Use** Railway's environment variables for sensitive data
3. **Enable** SSL/HTTPS (Railway provides this automatically)
4. **Set** `DEBUG=False` in production
5. **Use** strong `SECRET_KEY` (50+ random characters)
6. **Regularly update** dependencies: `pip install --upgrade -r requirements.txt`
7. **Monitor** Railway logs for suspicious activity

---

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Django Docs**: [docs.djangoproject.com](https://docs.djangoproject.com)
- **GitHub Issues**: Create an issue in your repository

---

**Last Updated:** January 2025
**Deployment Platform:** Railway.app
**Django Version:** 4.2+
