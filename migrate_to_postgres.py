#!/usr/bin/env python
"""
Database Migration Script: SQLite to PostgreSQL
For Balilihan Waterworks Management System

This script migrates all data from SQLite to PostgreSQL on Railway.

Usage:
    1. First deploy to Railway and get DATABASE_URL
    2. Set DATABASE_URL in environment
    3. Run: python migrate_to_postgres.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waterworks.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from consumers.models import (
    Barangay, Purok, MeterBrand, Consumer, MeterReading,
    Bill, Payment, StaffProfile, UserLoginEvent, SystemSetting
)

def check_database_connection():
    """Check if we can connect to the database."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run Django migrations on PostgreSQL."""
    print("\n📦 Running migrations on PostgreSQL...")
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def export_sqlite_data():
    """
    Export data from SQLite to JSON.
    Run this locally before deploying.
    """
    print("\n💾 Exporting data from SQLite...")

    # Export all data
    apps_to_export = [
        'auth.User',
        'consumers.Barangay',
        'consumers.Purok',
        'consumers.MeterBrand',
        'consumers.SystemSetting',
        'consumers.StaffProfile',
        'consumers.Consumer',
        'consumers.MeterReading',
        'consumers.Bill',
        'consumers.Payment',
        'consumers.UserLoginEvent',
    ]

    try:
        call_command(
            'dumpdata',
            *apps_to_export,
            output='data_backup.json',
            indent=2,
            natural_foreign=True,
            natural_primary=True
        )
        print("✅ Data exported to data_backup.json")
        print("📤 Upload this file to Railway and run import_data()")
        return True
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

def import_postgresql_data():
    """
    Import data from JSON to PostgreSQL.
    Run this on Railway after uploading data_backup.json.
    """
    print("\n📥 Importing data to PostgreSQL...")

    if not os.path.exists('data_backup.json'):
        print("❌ data_backup.json not found!")
        print("Please upload the exported data file first.")
        return False

    try:
        call_command('loaddata', 'data_backup.json', verbosity=2)
        print("✅ Data imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure migrations are run first")
        print("2. Check if data_backup.json is valid JSON")
        print("3. Try importing in smaller chunks if needed")
        return False

def verify_data():
    """Verify that data was imported correctly."""
    print("\n🔍 Verifying imported data...")

    models_to_check = [
        ('Users', User),
        ('Barangays', Barangay),
        ('Puroks', Purok),
        ('Meter Brands', MeterBrand),
        ('Consumers', Consumer),
        ('Meter Readings', MeterReading),
        ('Bills', Bill),
        ('Payments', Payment),
        ('Staff Profiles', StaffProfile),
        ('Login Events', UserLoginEvent),
        ('System Settings', SystemSetting),
    ]

    print("\n📊 Data counts:")
    for name, model in models_to_check:
        count = model.objects.count()
        print(f"  {name}: {count}")

    # Check for superusers
    superuser_count = User.objects.filter(is_superuser=True).count()
    print(f"\n👤 Superusers: {superuser_count}")

    if superuser_count == 0:
        print("⚠️  Warning: No superuser found!")
        print("   Create one with: python manage.py createsuperuser")

def main():
    """Main migration workflow."""
    print("=" * 60)
    print("🚀 Balilihan Waterworks Database Migration Tool")
    print("=" * 60)

    # Check which database we're connected to
    db_engine = connection.settings_dict['ENGINE']
    db_name = connection.settings_dict['NAME']

    print(f"\n📊 Current Database:")
    print(f"   Engine: {db_engine}")
    print(f"   Name: {db_name}")

    if 'sqlite' in db_engine:
        print("\n💡 You're connected to SQLite (local development)")
        print("\nWhat would you like to do?")
        print("1. Export data from SQLite (run this first)")
        print("2. Exit")

        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == '1':
            if export_sqlite_data():
                print("\n✅ Export complete!")
                print("\n📋 Next steps:")
                print("1. Push code to GitHub")
                print("2. Deploy to Railway")
                print("3. Upload data_backup.json to Railway")
                print("4. Run this script again on Railway to import")

    elif 'postgresql' in db_engine:
        print("\n💡 You're connected to PostgreSQL (Railway)")

        if not check_database_connection():
            return

        print("\nWhat would you like to do?")
        print("1. Run migrations only")
        print("2. Import data from data_backup.json")
        print("3. Verify data")
        print("4. Full setup (migrations + import + verify)")
        print("5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '1':
            run_migrations()
        elif choice == '2':
            import_postgresql_data()
        elif choice == '3':
            verify_data()
        elif choice == '4':
            if run_migrations():
                if import_postgresql_data():
                    verify_data()
                    print("\n✅ All done! Your Railway app is ready!")
                    print("\n📋 Final steps:")
                    print("1. Test login at your Railway URL")
                    print("2. Update Android app API base URL")
                    print("3. Test all API endpoints")
    else:
        print("❌ Unknown database engine")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
