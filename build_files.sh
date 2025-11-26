#!/bin/bash

# Build script for Vercel deployment

echo "=== Vercel Build Script ==="

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
echo "Creating staticfiles directory..."
mkdir -p staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# List collected static files for debugging
echo "Static files collected:"
ls -la staticfiles/ 2>/dev/null || echo "No staticfiles directory"

echo "=== Build completed successfully! ==="
