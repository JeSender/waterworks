# 🚀 Local Testing Guide for Balilihan Waterworks Management System

## 📋 Prerequisites

- ✅ Python 3.12 installed
- ✅ pip package manager
- ✅ Virtual environment (recommended)
- ✅ Git (for version control)

## 🔧 Step-by-Step Setup Instructions

### 1️⃣ **Navigate to Project Directory**

```bash
cd C:\balilihan_waterworks\waterworks
```

### 2️⃣ **Activate Virtual Environment**

If you don't have a virtual environment yet, create one:
```bash
python -m venv venv
```

Activate it:
```bash
# Windows Command Prompt
venv\Scripts\activate

# Windows PowerShell
venv\Scripts\Activate.ps1

# Git Bash
source venv/Scripts/activate
```

You should see `(venv)` in your terminal prompt.

### 3️⃣ **Install Dependencies**

```bash
pip install -r requirements.txt
```

This will install:
- Django 5.2.7
- PostgreSQL adapter (psycopg2-binary)
- WhiteNoise (static files)
- openpyxl (Excel exports)
- django-cors-headers (API support)
- python-decouple (environment variables)
- gunicorn (production server)
- python-dateutil, pytz (date utilities)

### 4️⃣ **Environment Configuration**

The `.env` file has been created for you with local development settings:

```env
SECRET_KEY=django-insecure-local-dev-key-change-in-production-xyz123abc456
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.100.9
```

**✅ No changes needed** - This configuration works for local testing!

### 5️⃣ **Database Setup**

The project will automatically use **SQLite** for local development (no PostgreSQL needed locally).

#### Apply Database Migrations:

```bash
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying consumers.0001_initial... OK
  ...
  (11 migrations total)
```

### 6️⃣ **Create Superuser (Admin Account)**

```bash
python manage.py createsuperuser
```

Follow the prompts:
```
Username: admin
Email address: admin@balilihan.gov.ph
Password: ********
Password (again): ********
```

### 7️⃣ **Collect Static Files**

```bash
python manage.py collectstatic --noinput
```

This collects all CSS, JavaScript, and image files into the `staticfiles/` directory.

### 8️⃣ **Run Development Server**

```bash
python manage.py runserver
```

Or specify a custom port:
```bash
python manage.py runserver 8080
```

Or bind to all network interfaces (for mobile testing):
```bash
python manage.py runserver 0.0.0.0:8000
```

Expected output:
```
Django version 5.2.7, using settings 'waterworks.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## 🌐 Access the Application

### **Main URLs:**

1. **Dashboard/Home**: http://127.0.0.1:8000/home/
2. **Admin Panel**: http://127.0.0.1:8000/admin/
3. **Login**: http://127.0.0.1:8000/
4. **Consumer Management**: http://127.0.0.1:8000/consumers/
5. **Meter Readings**: http://127.0.0.1:8000/meter-readings/
6. **Bill Inquiry**: http://127.0.0.1:8000/inquire/
7. **Reports**: http://127.0.0.1:8000/reports/

### **API Endpoints (for Android App):**

1. **Login API**: http://127.0.0.1:8000/api/login/
2. **Submit Reading**: http://127.0.0.1:8000/api/submit-reading/
3. **Create Reading**: http://127.0.0.1:8000/api/create-reading/
4. **Consumers API**: http://127.0.0.1:8000/api/consumers/

## 📱 Testing on Mobile Device (Same Network)

1. **Find your computer's IP address:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.100.9)

2. **Run server on all interfaces:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Access from mobile:**
   ```
   http://192.168.100.9:8000/home/
   ```

## 🎨 What You'll See

### ✨ **Professional Dashboard Features:**
- Beautiful purple-blue gradient background
- Glass-morphism cards with blur effects
- 3 metric cards (Connected/Disconnected/Delinquent) with color gradients
- Animated counters that count up from 0
- Payment status doughnut chart
- Recent collections grid
- Report generation with month/year selectors
- Smooth hover animations and transitions
- Fully responsive design

## 🔑 Login Credentials

After creating a superuser, you can log in with:
- **Username**: admin (or whatever you created)
- **Password**: (your password)

## 📊 Sample Data (Optional)

To create sample data for testing, you can use the Django admin panel:

1. Go to http://127.0.0.1:8000/admin/
2. Add **Barangays** (e.g., Poblacion, Magsija, Candasig)
3. Add **Puroks** under each Barangay
4. Add **Meter Brands** (e.g., Zenner, Elster, Sensus)
5. Add **Consumers** with their details
6. Add **Meter Readings**
7. System will auto-generate **Bills**
8. Record **Payments**

## 🛠️ Common Commands

### **Database Management:**
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (SQLite)
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### **Static Files:**
```bash
# Collect static files
python manage.py collectstatic

# Clear cache and recollect
python manage.py collectstatic --clear --noinput
```

### **Django Shell (for testing):**
```bash
python manage.py shell
```

```python
# Example: Check consumer count
from consumers.models import Consumer
print(f"Total consumers: {Consumer.objects.count()}")

# Check connected consumers
connected = Consumer.objects.filter(is_active=True).count()
print(f"Connected: {connected}")
```

## 🐛 Troubleshooting

### **Port Already in Use:**
```bash
# Use a different port
python manage.py runserver 8080
```

### **Static Files Not Loading:**
```bash
# Recollect static files
python manage.py collectstatic --clear --noinput
```

### **Database Errors:**
```bash
# Delete database and start fresh
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### **Module Not Found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### **Template Not Found:**
```bash
# Check that you're in the correct directory
cd C:\balilihan_waterworks\waterworks

# Verify templates exist
dir consumers\templates\consumers
```

## 📁 Project Structure

```
waterworks/
├── consumers/              # Main Django app
│   ├── migrations/         # Database migrations (11 files)
│   ├── templates/          # HTML templates (28 files)
│   │   └── consumers/
│   │       ├── base.html              # Base template
│   │       ├── home.html              # Dashboard
│   │       ├── inquire.html           # Bill inquiry
│   │       ├── consumer_list.html     # Consumer list
│   │       └── ...
│   ├── static/             # Static files (CSS, images)
│   │   └── consumers/
│   │       ├── style.css
│   │       └── images/
│   ├── models.py           # 10 database models
│   ├── views.py            # 44 view functions
│   ├── urls.py             # 40 URL patterns
│   └── admin.py            # Admin configuration
├── waterworks/             # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # Root URL config
│   └── wsgi.py             # WSGI config
├── staticfiles/            # Collected static files (129 files)
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (local)
├── db.sqlite3              # SQLite database (auto-created)
└── LOCAL_TESTING_GUIDE.md  # This file
```

## ✅ Verification Checklist

Before testing, verify:
- [ ] Virtual environment activated `(venv)` in prompt
- [ ] Dependencies installed `pip list | findstr Django`
- [ ] Migrations applied (no warnings when running server)
- [ ] Superuser created (can login to /admin/)
- [ ] Static files collected (129 files in staticfiles/)
- [ ] Server running without errors
- [ ] Can access http://127.0.0.1:8000/home/
- [ ] Dashboard displays with purple gradient and cards
- [ ] Can login with credentials
- [ ] All navigation links work

## 🎓 For Thesis Testing

### **Demo Scenarios:**

1. **Consumer Management:**
   - Add new consumer
   - Update consumer details
   - View consumer list with filters

2. **Meter Reading:**
   - Submit meter readings
   - View reading history
   - Confirm readings

3. **Billing:**
   - Auto-generated bills after readings
   - View bill details
   - Check delinquent accounts

4. **Payment Processing:**
   - Record payments via Bill Inquiry
   - Check payment receipts
   - View payment history

5. **Reports:**
   - Generate monthly delinquent report (Excel)
   - View connected/disconnected consumers
   - Check collections summary

6. **Dashboard Metrics:**
   - Real-time consumer counts
   - Payment status chart
   - Recent collections

## 🚀 Next Steps After Local Testing

Once local testing is complete:
1. All changes are already on GitHub
2. Railway automatically deploys from GitHub
3. Access production at: https://your-app.up.railway.app

## 📞 Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Verify all dependencies are installed
3. Ensure virtual environment is activated
4. Check Django version: `python -m django --version`

---

**✨ Your project is ready for local testing!**

**Last Updated:** November 20, 2025
**Django Version:** 5.2.7
**Python Version:** 3.12
**Status:** ✅ Production-Ready
