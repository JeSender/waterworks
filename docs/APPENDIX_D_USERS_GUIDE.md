# APPENDIX D: User's Guide

## Smart Meter Reading Application - Balilihan Waterworks

This guide provides detailed steps to set up and deploy the Smart Meter Reading Application in Balilihan, developed using the **Laravel framework** and **MySQL database**.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [System Requirements](#2-system-requirements)
3. [Setting Up the Environment](#3-setting-up-the-environment)
4. [Deploying the Application](#4-deploying-the-application)
5. [Configuring the Database](#5-configuring-the-database)
6. [Running the Application](#6-running-the-application)
7. [Troubleshooting](#7-troubleshooting)
8. [Support](#8-support)

---

## 1. Prerequisites

Before proceeding, ensure you have the following:

| Requirement | Description |
|-------------|-------------|
| **Source Code** | Complete project files for the Smart Meter Reading Application |
| **Access to a Server** | Local server or live hosting server (Apache or Nginx) |
| **Domain or IP Address** | Required for live deployment |
| **Technical Knowledge** | Familiarity with PHP, Laravel, and MySQL is recommended |

---

## 2. System Requirements

### 2.1 Hardware Requirements

| Component | Minimum Specification |
|-----------|----------------------|
| **Processor** | Intel Core i3 or higher |
| **RAM** | 4GB or more |
| **Storage** | 120GB HDD or larger |

### 2.2 Software Requirements

| Software | Version/Specification |
|----------|----------------------|
| **Operating System** | Windows 7 or newer |
| **Web Server** | Apache (XAMPP, WAMP) or Nginx |
| **PHP** | Version 8.0 or higher |
| **Composer** | Dependency manager for PHP |
| **Database** | MySQL 5.7 or higher |

---

## 3. Setting Up the Environment

### 3.1 Server Setup

#### Local Deployment

1. Install **XAMPP** or **WAMP** for Apache
2. Ensure PHP and MySQL modules are enabled
3. Start Apache and MySQL services from the control panel

#### Live Server Deployment

1. Prepare a VPS or shared hosting with PHP 8.0+ and MySQL support
2. Install Apache or Nginx as the web server
3. Configure SSL certificate for secure connections (recommended)

### 3.2 Installing Required Software

#### Install Composer

1. Download Composer from: https://getcomposer.org/
2. Run the installer and follow the setup wizard
3. Verify installation by running:

```cmd
composer --version
```

#### Install Laravel (if not included in the source code)

```cmd
composer global require laravel/installer
```

---

## 4. Deploying the Application

### 4.1 Extract the Source Code

1. Download the Smart Meter Reading Application source code (ZIP or via Git)
2. Extract the project files into the server's document root:

| Environment | Directory Path |
|-------------|----------------|
| **XAMPP** | `C:/xampp/htdocs/smart-meter-app/` |
| **WAMP** | `C:/wamp64/www/smart-meter-app/` |
| **Live Server** | `/var/www/html/smart-meter-app/` |

### 4.2 Install Dependencies

1. Open Command Prompt or Terminal
2. Navigate to the project directory:

```cmd
cd C:/xampp/htdocs/smart-meter-app
```

3. Run Composer to install required PHP packages:

```cmd
composer install
```

### 4.3 Set Up the Environment File

1. Locate the `.env.example` file in the project root
2. Duplicate and rename it to `.env`:

```cmd
copy .env.example .env
```

3. Open the `.env` file and configure the following settings:

```env
APP_NAME="Smart Meter Reading Application"
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=smr_balilihan
DB_USERNAME=root
DB_PASSWORD=your_password
```

4. Generate the application key:

```cmd
php artisan key:generate
```

---

## 5. Configuring the Database

### 5.1 Create the Database

1. Open **phpMyAdmin** or any MySQL management tool
2. Create a new database matching the name in your `.env` file

```sql
CREATE DATABASE smr_balilihan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5.2 Run Migrations

Execute the following command in the terminal to create database tables:

```cmd
php artisan migrate
```

### 5.3 Seed the Database (Optional)

If seeders are available for initial data:

```cmd
php artisan db:seed
```

To run both migrations and seeders together:

```cmd
php artisan migrate --seed
```

---

## 6. Running the Application

### 6.1 Local Server

1. Start Apache and MySQL in XAMPP or WAMP Control Panel
2. Run the Laravel development server:

```cmd
php artisan serve
```

3. Open your browser and navigate to:

```
http://127.0.0.1:8000
```

### 6.2 Live Server

#### Apache Configuration

1. Set the document root to the `public` directory of the Laravel project
2. Configure VirtualHost in `httpd.conf` or create a new file in `sites-available`:

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /var/www/html/smart-meter-app/public

    <Directory /var/www/html/smart-meter-app/public>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

3. Enable the site and restart Apache:

```bash
sudo a2ensite your-domain.conf
sudo systemctl restart apache2
```

#### Nginx Configuration

1. Create a server block configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html/smart-meter-app/public;

    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

2. Restart Nginx:

```bash
sudo systemctl restart nginx
```

3. Access the application using your assigned domain or IP address

---

## 7. Troubleshooting

### 7.1 Common Issues

#### Permission Denied Errors

**Problem:** Unable to write to storage or cache directories

**Solution:** Set proper permissions for the `storage` and `bootstrap/cache` directories:

```bash
# Linux/macOS
chmod -R 775 storage
chmod -R 775 bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache
```

```cmd
# Windows (Run as Administrator)
icacls storage /grant Everyone:F /T
icacls bootstrap\cache /grant Everyone:F /T
```

---

#### Missing Encryption Key

**Problem:** `No application encryption key has been specified`

**Solution:** Generate a new application key:

```cmd
php artisan key:generate
```

---

#### 500 Internal Server Error

**Problem:** Application returns a 500 error page

**Solution:**
1. Check server error logs:
   - Apache: `/var/log/apache2/error.log`
   - Nginx: `/var/log/nginx/error.log`
   - Laravel: `storage/logs/laravel.log`

2. Ensure the `.env` file is configured correctly

3. Verify file permissions on storage directories

4. Clear application cache:

```cmd
php artisan config:clear
php artisan cache:clear
php artisan view:clear
```

---

#### Database Connection Error

**Problem:** `SQLSTATE[HY000] [2002] Connection refused`

**Solution:**
1. Verify database credentials in the `.env` file
2. Ensure MySQL server is running:

```cmd
# Windows (XAMPP)
Check XAMPP Control Panel - MySQL should show "Running"

# Linux
sudo systemctl status mysql
sudo systemctl start mysql
```

3. Test database connection:

```cmd
php artisan tinker
>>> DB::connection()->getPdo();
```

---

#### Composer Memory Limit Error

**Problem:** `Allowed memory size exhausted`

**Solution:** Increase PHP memory limit:

```cmd
php -d memory_limit=-1 composer install
```

---

#### Route Not Found (404 Error)

**Problem:** Pages return 404 errors

**Solution:**
1. Ensure `mod_rewrite` is enabled (Apache)
2. Verify `.htaccess` file exists in `public` directory
3. Clear route cache:

```cmd
php artisan route:clear
php artisan route:cache
```

---

## 8. Support

### Documentation Resources

For additional assistance, refer to the following resources:

| Resource | URL |
|----------|-----|
| **Laravel Documentation** | https://laravel.com/docs |
| **PHP Documentation** | https://www.php.net/docs.php |
| **MySQL Documentation** | https://dev.mysql.com/doc/ |
| **Composer Documentation** | https://getcomposer.org/doc/ |

### Contact

For technical assistance specific to this application, contact the development team or system administrator.

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Install dependencies | `composer install` |
| Generate app key | `php artisan key:generate` |
| Run migrations | `php artisan migrate` |
| Seed database | `php artisan db:seed` |
| Start development server | `php artisan serve` |
| Clear all cache | `php artisan optimize:clear` |
| Create storage link | `php artisan storage:link` |
| Check Laravel version | `php artisan --version` |

---

**End of Appendix D: User's Guide**
