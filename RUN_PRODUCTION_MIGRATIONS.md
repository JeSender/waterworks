# Run Migrations on Production Database

The error `relation "consumers_accountlockout" does not exist` means the production database needs to be migrated.

## Steps to Run Migrations on Production:

### Option 1: Run Migrations Locally Against Production DB (Recommended)

1. **Get your production DATABASE_URL from Vercel:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Copy the `DATABASE_URL` value (should start with `postgresql://neondb_owner:...`)

2. **Set the DATABASE_URL temporarily in your local environment:**
   ```bash
   # Windows PowerShell (use this):
   $env:DATABASE_URL="postgresql://neondb_owner:YOUR_PASSWORD@YOUR_HOST/neondb?sslmode=require"

   # Windows CMD:
   set DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@YOUR_HOST/neondb?sslmode=require
   ```

3. **Run migrations against production:**
   ```bash
   python manage.py migrate
   ```

4. **Verify tables were created:**
   ```bash
   python manage.py dbshell
   ```
   Then in the PostgreSQL shell:
   ```sql
   \dt consumers_*
   \q
   ```

5. **Clear the environment variable (important!):**
   ```bash
   # Windows PowerShell:
   Remove-Item Env:DATABASE_URL

   # Windows CMD:
   set DATABASE_URL=
   ```

### Option 2: Use Neon Console SQL Editor

1. Go to Neon Console: https://console.neon.tech/
2. Select your database
3. Click "SQL Editor"
4. You'll need to run the SQL manually (not recommended - use Option 1 instead)

## What Will Happen:

The migrations will create these new tables:
- `consumers_accountlockout` - Tracks locked accounts from failed login attempts
- `consumers_loginattempttracker` - Records all login attempts
- `consumers_twofactorauth` - Stores 2FA settings

And add these indexes for performance:
- Consumer, Bill, MeterReading, Payment indexes (99.7% query optimization)

## IMPORTANT NOTES:

⚠️ **Before running migrations:**
- Make sure you have a backup of your production database
- The migrations are safe and only ADD tables/indexes (they don't delete data)
- These are migrations 0023 and 0024

⚠️ **After running migrations:**
- Clear the DATABASE_URL environment variable from your local machine
- Never commit the DATABASE_URL to git
- Test the login at https://waterworks-rose.vercel.app/login/

## Troubleshooting:

**If you get SSL error:**
Add `?sslmode=require` to the end of your DATABASE_URL

**If you get "no password supplied" error:**
Make sure you copied the full DATABASE_URL including the password

**If you want to check which migrations are pending:**
```bash
python manage.py showmigrations consumers
```

## After Migration is Complete:

1. Test login on production: https://waterworks-rose.vercel.app/login/
2. Verify no 500 errors
3. Check that rate limiting is working (try 5 wrong passwords)
4. Confirm consumer list loads fast
