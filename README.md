# Balilihan Waterworks Management System

A comprehensive water utility management system with web portal, mobile app integration, and enterprise-grade security features.

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-purple.svg)](https://railway.app/)

---

## 🎯 Project Overview

**Type:** Water Utility Management System
**Technology Stack:** Django (Backend) + PostgreSQL (Database) + Android (Mobile)
**Deployment:** Railway.app (Cloud Platform)
**Security Level:** Enterprise-Grade

---

## ✨ Features

### Core Functionality
- **Consumer Management** - CRUD operations for water consumers
- **Meter Reading** - Web and mobile meter reading submission
- **Automated Billing** - Generate bills from confirmed readings
- **Payment Processing** - Track payments with OR generation
- **Reports & Analytics** - Revenue, delinquency, and summary reports

### Security Features
- **Enhanced Login Tracking** - IP address, device, and session tracking
- **Admin Verification** - Two-step authentication for sensitive operations
- **Role-Based Access Control** - Superuser, Admin, Field Staff roles
- **Password Strength Validation** - Enforce strong password policies
- **Login History Dashboard** - Monitor all access attempts
- **Audit Trail** - Complete activity logging

### Mobile Integration
- **Android App API** - RESTful API for mobile app
- **CORS Enabled** - Cross-origin support for mobile
- **Session Management** - Secure mobile authentication
- **Real-time Sync** - Data sync between web and mobile

---

## 🚀 Quick Start

### Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/balilihan-waterworks.git
   cd balilihan-waterworks
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access Application**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin/

---

## ☁️ Railway Deployment

### Prerequisites
- GitHub account
- Railway.app account (sign up for free)
- Your project code ready

### Deployment Steps

See **[RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)** for complete step-by-step instructions.

**Quick Overview:**
1. Push code to GitHub
2. Create Railway project from GitHub repo
3. Add PostgreSQL database
4. Set environment variables
5. Deploy automatically
6. Migrate data from SQLite to PostgreSQL
7. Test and verify

---

## 📁 Project Structure

```
balilihan_waterworks/
├── consumers/              # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # Business logic (2300+ lines)
│   ├── decorators.py      # Security decorators
│   ├── urls.py            # URL routing
│   ├── forms.py           # Django forms
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, images
├── waterworks/            # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # Main URL config
│   └── wsgi.py            # WSGI config
├── requirements.txt       # Python dependencies
├── Procfile              # Railway start command
├── runtime.txt           # Python version
├── railway.json          # Railway configuration
├── .gitignore            # Git ignore rules
├── migrate_to_postgres.py # Database migration script
└── README.md             # This file
```

---

## 🗄️ Database Models

- **Consumer** - Water consumer information
- **Bill** - Monthly water bills
- **Payment** - Payment records with OR
- **MeterReading** - Meter readings (web + mobile)
- **UserLoginEvent** - Login tracking with security info
- **Barangay** - Area management
- **Purok** - Sub-area management
- **StaffProfile** - Staff assignments
- **SystemSetting** - Water rates configuration

---

## 🔐 User Roles

| Role | Access Level | Capabilities |
|------|--------------|--------------|
| **Superuser** | Full System | User management, system settings, all features |
| **Admin** | Elevated | Reports, login history, consumer management |
| **Field Staff** | Standard | Meter readings for assigned barangay |
| **Regular User** | Basic | Login only |

---

## 🌐 API Endpoints

### Authentication
- `POST /api/login/` - Mobile login with tracking

### Data Access
- `GET /api/consumers/` - Get consumers for assigned barangay
- `POST /api/submit-reading/` - Submit meter reading
- `GET /api/rates/` - Get current water rates

### Response Format
```json
{
  "status": "success",
  "token": "session-key",
  "barangay": "Centro",
  "user": {
    "username": "fieldstaff1",
    "full_name": "Juan Dela Cruz"
  }
}
```

---

## 🔧 Environment Variables

Required variables for Railway deployment:

```bash
# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# Hosts
ALLOWED_HOSTS=.railway.app,.up.railway.app

# CORS (for Android app)
CORS_ALLOWED_ORIGINS=https://your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app

# Database (auto-set by Railway)
DATABASE_URL=postgresql://...
```

---

## 📱 Android App Integration

1. Update base URL in your Android app:
   ```java
   String BASE_URL = "https://your-app-name.up.railway.app";
   ```

2. Update all API endpoints to use HTTPS

3. Test connectivity:
   - Login API
   - Consumer list
   - Meter reading submission

See **[ANDROID_APP_CHANGES_REQUIRED.md](ANDROID_APP_CHANGES_REQUIRED.md)** for details.

---

## 🧪 Testing

### Run Tests
```bash
python manage.py test consumers
```

### Manual Testing Checklist
- [ ] Login with different user roles
- [ ] Consumer CRUD operations
- [ ] Meter reading submission
- [ ] Bill generation
- [ ] Payment processing
- [ ] Report generation
- [ ] API endpoints
- [ ] Security features

---

## 📊 Reports

### Available Reports
1. **Revenue Report** - All payments for a period
2. **Delinquency Report** - Unpaid bills
3. **Payment Summary** - Consumer payment totals

### Export Formats
- Excel (.xlsx) with formatting
- CSV for data processing

---

## 🛡️ Security Features

### Authentication & Authorization
- Session-based authentication
- Role-based access control
- Admin verification for sensitive operations
- Password strength validation

### Tracking & Monitoring
- IP address logging
- Device/browser tracking
- Login method tracking (web/mobile)
- Failed login attempt monitoring
- Session duration tracking

### Data Protection
- HTTPS enforced in production
- Secure cookie settings
- CSRF protection
- XSS protection
- SQL injection prevention (Django ORM)

---

## 📖 Documentation

- **[RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Changes and configuration summary
- **[FINAL_IMPLEMENTATION_SUMMARY.md](FINAL_IMPLEMENTATION_SUMMARY.md)** - Feature overview
- **[SECURITY_FEATURES_THESIS_DEFENSE.md](SECURITY_FEATURES_THESIS_DEFENSE.md)** - Security documentation
- **[ANDROID_APP_CHANGES_REQUIRED.md](ANDROID_APP_CHANGES_REQUIRED.md)** - Mobile app guide

---

## 🔧 Maintenance

### View Logs (Railway)
```bash
railway logs --tail
```

### Database Backup
```bash
railway shell
python manage.py dumpdata --indent 2 > backup.json
```

### Update Application
```bash
git add .
git commit -m "Update: description"
git push  # Railway auto-deploys
```

---

## 🚨 Troubleshooting

### Common Issues

**Build Fails on Railway**
- Check `requirements.txt` syntax
- View build logs in Railway dashboard
- Ensure Python 3.11 compatibility

**Static Files Not Loading**
```bash
railway shell
python manage.py collectstatic --noinput
```

**Database Connection Error**
- Ensure PostgreSQL is linked in Railway
- Verify `DATABASE_URL` variable exists

**CORS Errors from Mobile**
- Add Railway domain to `CORS_ALLOWED_ORIGINS`
- Check `corsheaders` in `INSTALLED_APPS`

See **RAILWAY_DEPLOYMENT_GUIDE.md** for more troubleshooting.

---

## 💰 Cost (Railway.app)

### Free Tier
- **$5 credit per month**
- 500 hours execution time
- 100 GB bandwidth
- Perfect for testing and demos

### Upgrade When Needed
- Hobby plan: $5/month
- Unlimited execution time
- More resources

---

## 🎓 For Thesis Defense

### Demo Preparation
1. Ensure Railway app is running
2. Test all features beforehand
3. Prepare live demo script
4. Have backup screenshots/video
5. Test from multiple devices

### Key Highlights
- Cloud-based deployment
- Enterprise-grade security
- Mobile integration
- Real-time data sync
- Scalable architecture

---

## 📞 Support

### Project Documentation
- See `/docs` folder for detailed guides
- Check `DEPLOYMENT_SUMMARY.md` for changes
- Read `SECURITY_FEATURES_THESIS_DEFENSE.md` for security details

### Railway Resources
- [Railway Documentation](https://docs.railway.app/)
- [Django on Railway Guide](https://docs.railway.app/guides/django)

---

## 📜 License

This project is developed for educational purposes as part of a thesis/research project.

---

## 🙏 Acknowledgments

- Django Framework
- Railway.app Platform
- PostgreSQL Database
- WhiteNoise (Static Files)
- OpenPyXL (Excel Export)

---

## 📈 Project Statistics

- **Total Code:** ~2,500 lines Python + templates
- **Database Models:** 11
- **Web Views:** 40+ functions
- **API Endpoints:** 4
- **Security Features:** 8 major implementations
- **User Roles:** 4 levels
- **Templates:** 15+ HTML pages

---

## ✅ Status

**Development:** ✅ Complete
**Testing:** ✅ Verified
**Documentation:** ✅ Complete
**Deployment:** ✅ Production Ready
**Security:** 🔒 Enterprise-Grade
**Thesis Defense:** 🎓 Ready

---

**System Status:** 🟢 **PRODUCTION READY**
**Platform:** ☁️ **Railway.app**
**Last Updated:** January 2025

---

*Developed for Balilihan Waterworks Management*
*Built with Django • Deployed on Railway • Secured for Production*
