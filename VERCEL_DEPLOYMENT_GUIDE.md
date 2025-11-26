# Vercel + Neon Deployment Guide
## Balilihan Waterworks Management System

Complete step-by-step guide to deploy your Django project to Vercel with Neon PostgreSQL.

---

## PRE-DEPLOYMENT CHECKLIST

### Files Required
- [x] `requirements.txt` - Python dependencies
- [x] `vercel.json` - Vercel configuration
- [x] `build_files.sh` - Build script
- [x] `.gitignore` - Files to exclude from Git
- [x] `.env.example` - Environment variables template
- [x] Updated `settings.py` - Production configuration

### Settings Updated
- [x] Added `dj-database-url` for PostgreSQL
- [x] Added `whitenoise` for static files
- [x] Added `django-cors-headers` for Android app
- [x] Configured environment variables with `python-decouple`
- [x] Set up logging for production

---

## PART 1: SET UP NEON DATABASE

### Step 1: Create Neon Account

1. Go to https://neon.tech
2. Sign up with GitHub or email
3. Verify your email

### Step 2: Create a New Project

1. Click "Create a project"
2. Enter project name: `balilihan-waterworks`
3. Select region closest to you (e.g., `us-east-1`)
4. Click "Create project"

### Step 3: Get Connection String

1. After project creation, you'll see the connection details
2. Copy the **Connection string** (it looks like):
   ```
   postgresql://user:password@ep-xxx-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
3. **Save this securely** - you'll need it for Vercel

### Step 4: Note Important Details

- **Database Name:** neondb (default)
- **User:** Your Neon username
- **Host:** ep-xxx-xxx-xxx.us-east-1.aws.neon.tech
- **SSL:** Required (`?sslmode=require`)

---

## PART 2: PREPARE YOUR CODE

### Step 1: Verify Project Files

Ensure these files exist in your project root:

#### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "waterworks/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/staticfiles/$1"
    },
    {
      "src": "/(.*)",
      "dest": "waterworks/wsgi.py"
    }
  ]
}
```

#### build_files.sh
```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

### Step 2: Update settings.py for Vercel

Ensure your `settings.py` has these configurations:

```python
import os
import dj_database_url
from decouple import config, Csv

# Security
SECRET_KEY = config('SECRET_KEY', default='your-development-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Auto-add Vercel domains
VERCEL_URL = os.environ.get('VERCEL_URL', '')
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)
    ALLOWED_HOSTS.append('.vercel.app')

# Database
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware (add WhiteNoise)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add after security
    # ... rest of middleware
]

# CORS for Android app
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())
```

### Step 3: Push to GitHub

```bash
cd D:\balilihan_waterworks\waterworks

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create commit
git commit -m "Prepare for Vercel deployment"

# Add GitHub remote (replace with your repo)
git remote add origin https://github.com/JeSender/waterworks.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## PART 3: DEPLOY TO VERCEL

### Step 1: Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub (recommended)
3. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Click "Add New..." → "Project"
2. Select "Import Git Repository"
3. Find and select your repository: `JeSender/waterworks`
4. Click "Import"

### Step 3: Configure Project

1. **Framework Preset:** Other
2. **Root Directory:** `./` (leave default)
3. **Build Command:** `bash build_files.sh`
4. **Output Directory:** Leave empty
5. **Install Command:** Leave default

### Step 4: Add Environment Variables

Click "Environment Variables" and add:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate a new random key |
| `DEBUG` | `False` |
| `DATABASE_URL` | Your Neon connection string |
| `ALLOWED_HOSTS` | `.vercel.app,waterworks-rose.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | `https://waterworks-rose.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://waterworks-rose.vercel.app` |
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Your Gmail app password |

#### Generate SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use: https://djecrety.ir/

### Step 5: Deploy

1. Click "Deploy"
2. Wait for build to complete (2-5 minutes)
3. Check build logs for any errors

---

## PART 4: RUN DATABASE MIGRATIONS

### Option A: Using Local Environment

1. Set up local environment with Neon database:
   ```bash
   # Create .env file with your Neon DATABASE_URL
   echo "DATABASE_URL=postgresql://user:pass@host/db?sslmode=require" > .env
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

### Option B: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Link to your project:
   ```bash
   cd D:\balilihan_waterworks\waterworks
   vercel link
   ```

4. Run migrations using Vercel environment:
   ```bash
   vercel env pull .env.local
   source .env.local  # Linux/Mac
   # or manually set variables on Windows
   python manage.py migrate
   ```

---

## PART 5: CONFIGURE DOMAIN

### Get Your Vercel URL

After deployment, Vercel provides a URL like:
```
https://waterworks-rose.vercel.app
```

### Update Environment Variables

In Vercel Dashboard, update these if needed:
```
ALLOWED_HOSTS=.vercel.app,waterworks-rose.vercel.app
CORS_ALLOWED_ORIGINS=https://waterworks-rose.vercel.app
CSRF_TRUSTED_ORIGINS=https://waterworks-rose.vercel.app
```

### Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS as instructed
4. SSL is automatic

---

## PART 6: TESTING

### Test 1: Access Website

Open your Vercel URL in browser:
```
https://waterworks-rose.vercel.app
```

**Note:** First load may take 3-10 seconds (cold start)

### Test 2: Admin Login

Go to:
```
https://waterworks-rose.vercel.app/login/
```

Login with your superuser credentials.

### Test 3: Django Admin

Go to:
```
https://waterworks-rose.vercel.app/admin/
```

### Test 4: API Endpoints

Test with curl or Postman:

```bash
# Test rates endpoint
curl https://waterworks-rose.vercel.app/api/rates/

# Test login
curl -X POST https://waterworks-rose.vercel.app/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

---

## PART 7: UPDATE ANDROID APP

### Update API Base URL

In your Android app, change:

**Before:**
```java
String BASE_URL = "http://192.168.1.100:8000";
```

**After:**
```java
String BASE_URL = "https://waterworks-rose.vercel.app";
```

### Handle Cold Starts

Add timeout handling for Vercel cold starts:
```java
request.setRetryPolicy(new DefaultRetryPolicy(
    30000, // 30 seconds timeout
    0,     // No retries
    DefaultRetryPolicy.DEFAULT_BACKOFF_MULT
));
```

---

## PART 8: MAINTENANCE

### View Logs

1. Go to Vercel Dashboard
2. Select your project
3. Click "Deployments"
4. Click on any deployment → "Functions" → View logs

Or use CLI:
```bash
vercel logs
```

### Redeploy

Push to GitHub and Vercel auto-deploys:
```bash
git add .
git commit -m "Update: description"
git push
```

Or manual deploy:
```bash
vercel --prod
```

### Database Management

Access Neon SQL Editor:
1. Go to https://console.neon.tech
2. Select your project
3. Click "SQL Editor"

Or connect via psql:
```bash
psql "postgresql://user:pass@host/db?sslmode=require"
```

---

## TROUBLESHOOTING

### Issue 1: Build Fails

**Check:**
- `requirements.txt` syntax
- Python version compatibility
- Build logs in Vercel dashboard

**Solution:**
```bash
# Test build locally
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

### Issue 2: 500 Internal Server Error

**Check:**
- Environment variables are set correctly
- `DEBUG=False` but `ALLOWED_HOSTS` not configured
- Database connection issues

**Solution:**
- Temporarily set `DEBUG=True` to see error details
- Check Vercel function logs

### Issue 3: Static Files Not Loading

**Check:**
- WhiteNoise in MIDDLEWARE
- `collectstatic` runs in build
- `STATIC_ROOT` configured

**Solution:**
```python
# In settings.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Issue 4: Database Connection Error

**Check:**
- `DATABASE_URL` is correct
- SSL mode is included (`?sslmode=require`)
- Neon database is active (not sleeping)

**Solution:**
- Go to Neon dashboard and check database status
- Verify connection string format

### Issue 5: CORS Errors

**Check:**
- `CORS_ALLOWED_ORIGINS` includes your domain
- `corsheaders` in INSTALLED_APPS

**Solution:**
```python
CORS_ALLOWED_ORIGINS = [
    'https://waterworks-rose.vercel.app',
]
```

### Issue 6: Cold Start Delays

**Cause:** Vercel serverless functions need to "wake up"

**Expected behavior:**
- First request: 3-10 seconds
- Subsequent requests: Fast

**Solutions:**
- Add loading indicators in your app
- Consider Vercel Pro for always-on

---

## ENVIRONMENT VARIABLES REFERENCE

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key | `abc123...` |
| `DEBUG` | Yes | Debug mode | `False` |
| `DATABASE_URL` | Yes | Neon connection string | `postgresql://...` |
| `ALLOWED_HOSTS` | Yes | Allowed domains | `.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | Yes | CORS domains | `https://...` |
| `CSRF_TRUSTED_ORIGINS` | Yes | CSRF domains | `https://...` |
| `EMAIL_HOST_USER` | Optional | Email sender | `your@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Optional | Email app password | `xxxx xxxx xxxx` |

---

## POST-DEPLOYMENT CHECKLIST

### Web Application
- [ ] Login page loads
- [ ] Dashboard shows correct data
- [ ] Consumer management works
- [ ] Meter readings display
- [ ] Bill generation works
- [ ] Payment processing works
- [ ] Reports export to Excel
- [ ] User management accessible (superuser)
- [ ] Login history visible (superuser/admin)

### Security Features
- [ ] HTTPS enforced
- [ ] Login tracking records IP addresses
- [ ] Admin verification requires password
- [ ] Password strength validation works

### API Endpoints
- [ ] `/api/login/` - Returns user info
- [ ] `/api/consumers/` - Returns consumer list
- [ ] `/api/meter-readings/` - Accepts readings
- [ ] `/api/rates/` - Returns current rates

### Android App
- [ ] Update base URL to Vercel domain
- [ ] Test login from app
- [ ] Test consumer list fetch
- [ ] Test meter reading submission
- [ ] Handle cold start delays

---

## COST SUMMARY

### Vercel Free Tier
- Unlimited deployments
- 100 GB bandwidth/month
- Serverless functions (with limits)
- Automatic HTTPS
- GitHub integration

### Neon Free Tier
- 0.5 GB storage
- Auto-suspend after 5 minutes
- Branching support
- Connection pooling

### When to Upgrade
- More than 0.5 GB database
- Need always-on (no cold starts)
- Higher traffic volumes
- Team collaboration features

---

## SUPPORT & RESOURCES

### Documentation
- [Vercel Docs](https://vercel.com/docs)
- [Neon Docs](https://neon.tech/docs)
- [Django Docs](https://docs.djangoproject.com/)

### Project Files
- `ANDROID_APP_VERCEL_SETUP.md` - Mobile app guide
- `DEPLOYMENT_SUMMARY.md` - Configuration summary
- `docs/SYSTEM_ARCHITECTURE.md` - System architecture

---

## CONGRATULATIONS!

Your Balilihan Waterworks Management System is now deployed on Vercel!

### Your Live URLs:
- **Web App:** `https://waterworks-rose.vercel.app`
- **Admin:** `https://waterworks-rose.vercel.app/admin/`
- **API Base:** `https://waterworks-rose.vercel.app/api/`

### Next Steps:
1. Test all features thoroughly
2. Update Android app with new URL
3. Train users on the system
4. Monitor logs for errors
5. Set up regular database backups
6. Present for thesis defense!

---

**System Status:** PRODUCTION READY
**Deployment Platform:** Vercel + Neon PostgreSQL
**Security Level:** Enterprise-Grade

**Good luck with your thesis defense!**
