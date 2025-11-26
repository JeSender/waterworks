# Quick Command Reference
## Balilihan Waterworks Railway Deployment

---

## 🚀 Initial Setup Commands

### Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Export SQLite Data
```bash
python migrate_to_postgres.py
# Choose option 1
```

### Git Commands
```bash
# Initialize (if needed)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Railway deployment"

# Add GitHub remote (replace USERNAME)
git remote add origin https://github.com/USERNAME/balilihan-waterworks.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## ☁️ Railway CLI Commands

### Install Railway CLI

**Windows (PowerShell):**
```powershell
iwr https://railway.app/install.ps1 | iex
```

**Mac/Linux:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Login and Link
```bash
# Login to Railway
railway login

# Link to your project
cd D:\balilihan_waterworks\waterworks
railway link

# Select your project from list
```

### Common Railway Commands
```bash
# View logs (live)
railway logs --tail

# Access shell
railway shell

# Deploy manually
railway up

# Check status
railway status

# View environment variables
railway variables

# Open project in browser
railway open
```

---

## 📊 Database Migration Commands

### On Railway (after deployment)

```bash
# Access Railway shell
railway shell

# Run migration script
python migrate_to_postgres.py
# Choose option 4 (Full setup)

# Or run steps manually:
python manage.py migrate
python manage.py loaddata data_backup.json
```

### Create Superuser
```bash
railway shell
python manage.py createsuperuser
```

---

## 🔧 Django Management Commands

### On Railway
```bash
railway shell

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Show migrations
python manage.py showmigrations

# Check deployment
python manage.py check --deploy
```

### Database Backup
```bash
railway shell

# Full backup
python manage.py dumpdata --indent 2 > backup.json

# Specific app
python manage.py dumpdata consumers --indent 2 > consumers_backup.json

# Exclude sessions and logs
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > backup.json
```

---

## 🧪 Testing Commands

### Test API with curl

**Login:**
```bash
curl -X POST https://your-app.up.railway.app/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

**Get Consumers:**
```bash
curl -X GET https://your-app.up.railway.app/api/consumers/ \
  -H "Cookie: sessionid=YOUR-SESSION-ID"
```

**Submit Reading:**
```bash
curl -X POST https://your-app.up.railway.app/api/submit-reading/ \
  -H "Content-Type: application/json" \
  -d '{
    "consumer_id": 1,
    "reading": 1250,
    "reading_date": "2025-01-15"
  }'
```

**Get Rates:**
```bash
curl -X GET https://your-app.up.railway.app/api/rates/
```

---

## 🐛 Debugging Commands

### View Railway Logs
```bash
# Live logs
railway logs --tail

# Last 100 lines
railway logs --limit 100

# Specific deployment
railway logs --deployment DEPLOYMENT_ID
```

### Django Debug on Railway
```bash
railway shell

# Check database connection
python manage.py dbshell

# Run Django shell
python manage.py shell

# Check settings
python -c "from django.conf import settings; print(settings.DATABASES)"
```

### PostgreSQL Commands
```bash
railway shell
python manage.py dbshell

-- List all tables
\dt

-- List databases
\l

-- Show table structure
\d consumers_consumer

-- Count records
SELECT COUNT(*) FROM consumers_consumer;

-- Exit
\q
```

---

## 📦 Deployment Workflow

### Update and Deploy
```bash
# Make changes locally

# Test locally
python manage.py runserver

# Commit changes
git add .
git commit -m "Update: description of changes"

# Push to GitHub (Railway auto-deploys)
git push

# Watch deployment
railway logs --tail
```

### Rollback Deployment
```bash
# In Railway dashboard:
# 1. Go to Deployments tab
# 2. Find previous successful deployment
# 3. Click "..." → "Redeploy"
```

---

## 🔐 Environment Variable Commands

### Set Variables via CLI
```bash
# Set single variable
railway variables set SECRET_KEY="your-secret-key"

# Set multiple variables
railway variables set DEBUG=False ALLOWED_HOSTS=".railway.app"

# View all variables
railway variables

# Delete variable
railway variables delete VARIABLE_NAME
```

---

## 📱 Android App Testing

### Using ADB and Logcat
```bash
# View Android app logs
adb logcat | grep "WaterworksApp"

# Test API from Android device
adb shell am start -a android.intent.action.VIEW -d "https://your-app.up.railway.app/api/login/"
```

---

## 🔍 Health Checks

### Check App Status
```bash
# Test if app is responding
curl -I https://your-app.up.railway.app/

# Check API endpoint
curl https://your-app.up.railway.app/api/rates/

# Check admin
curl https://your-app.up.railway.app/admin/
```

### Monitor Resource Usage
In Railway dashboard:
- CPU usage
- Memory usage
- Network traffic
- Build times

---

## 💾 Backup and Restore

### Backup Database
```bash
railway shell

# Create backup with timestamp
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 > backup_$(date +%Y%m%d_%H%M%S).json
```

### Restore Database
```bash
railway shell

# Load data from backup
python manage.py loaddata backup_20250115_120000.json
```

---

## 🧹 Cleanup Commands

### Clear Django Cache
```bash
railway shell
python manage.py clearsessions
```

### Remove Old Static Files
```bash
railway shell
python manage.py collectstatic --clear --noinput
```

---

## 📊 Statistics Commands

### Get Data Counts
```bash
railway shell
python manage.py shell

# Then in Python shell:
from django.contrib.auth.models import User
from consumers.models import Consumer, Bill, Payment, MeterReading

print(f"Users: {User.objects.count()}")
print(f"Consumers: {Consumer.objects.count()}")
print(f"Bills: {Bill.objects.count()}")
print(f"Payments: {Payment.objects.count()}")
print(f"Readings: {MeterReading.objects.count()}")
```

---

## 🚨 Emergency Commands

### Force Redeploy
```bash
railway up --detach
```

### Restart Service
```bash
railway restart
```

### Check for Migrations
```bash
railway shell
python manage.py showmigrations
python manage.py migrate --plan
```

---

## 📖 Help Commands

### Railway Help
```bash
railway --help
railway logs --help
railway variables --help
```

### Django Help
```bash
python manage.py --help
python manage.py migrate --help
python manage.py collectstatic --help
```

---

## 🎯 Quick Deployment Checklist

```bash
# 1. Export data locally
python migrate_to_postgres.py

# 2. Push to GitHub
git add . && git commit -m "Deploy to Railway" && git push

# 3. Set environment variables in Railway dashboard
# SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS

# 4. Upload and import data
railway shell
python migrate_to_postgres.py  # Option 4

# 5. Test deployment
curl https://your-app.up.railway.app/
```

---

## 📞 Common URLs

Replace `your-app-name` with your actual Railway app name:

- **Web App:** `https://your-app-name.up.railway.app/`
- **Login:** `https://your-app-name.up.railway.app/login/`
- **Admin:** `https://your-app-name.up.railway.app/admin/`
- **API Login:** `https://your-app-name.up.railway.app/api/login/`
- **API Consumers:** `https://your-app-name.up.railway.app/api/consumers/`
- **API Submit:** `https://your-app-name.up.railway.app/api/submit-reading/`
- **API Rates:** `https://your-app-name.up.railway.app/api/rates/`

---

## 💡 Pro Tips

### Alias for Railway CLI
```bash
# Add to ~/.bashrc or ~/.zshrc
alias rl='railway'
alias rll='railway logs --tail'
alias rls='railway shell'
```

### Quick Test Script
```bash
#!/bin/bash
echo "Testing Balilihan Waterworks API..."
BASE_URL="https://your-app-name.up.railway.app"

echo "1. Testing login endpoint..."
curl -X POST $BASE_URL/api/login/ -H "Content-Type: application/json" -d '{"username":"test","password":"test"}'

echo "\n2. Testing rates endpoint..."
curl $BASE_URL/api/rates/

echo "\n3. Testing admin page..."
curl -I $BASE_URL/admin/

echo "\nTests complete!"
```

---

## 🔗 Useful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app/
- **Django Docs:** https://docs.djangoproject.com/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Quick Reference Version:** 1.0
**Last Updated:** January 2025
**For:** Balilihan Waterworks Management System
