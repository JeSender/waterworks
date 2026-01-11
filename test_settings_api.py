#!/usr/bin/env python
"""
Test script for Settings API endpoints
Run with: python test_settings_api.py
"""

import requests
import json
from datetime import datetime, timedelta

# API Base URL (change to your Render URL in production)
BASE_URL = "http://127.0.0.1:8000"  # Local development
# BASE_URL = "https://your-app.onrender.com"  # Production

def test_get_settings():
    """Test GET /api/settings/ endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Get Full Settings")
    print("="*60)

    url = f"{BASE_URL}/api/settings/"
    print(f"GET {url}")

    response = requests.get(url)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Settings retrieved:")
        print(json.dumps(data, indent=2))

        # Return updated_at for next test
        return data.get('updated_at')
    else:
        print(f"\n❌ FAILED: {response.text}")
        return None


def test_check_version_first_time():
    """Test GET /api/settings/check-version/ without last_updated (first sync)"""
    print("\n" + "="*60)
    print("TEST 2: Check Version (First Sync - No Last Updated)")
    print("="*60)

    url = f"{BASE_URL}/api/settings/check-version/"
    print(f"GET {url}")

    response = requests.get(url)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(json.dumps(data, indent=2))

        if data.get('settings_changed'):
            print("\n💡 Result: Settings changed (expected for first sync)")
        else:
            print("\n⚠️ Warning: Expected settings_changed = true for first sync")
    else:
        print(f"\n❌ FAILED: {response.text}")


def test_check_version_with_old_timestamp():
    """Test GET /api/settings/check-version/ with old timestamp (should show changed)"""
    print("\n" + "="*60)
    print("TEST 3: Check Version (With Old Timestamp)")
    print("="*60)

    # Use yesterday's date
    old_timestamp = (datetime.now() - timedelta(days=1)).isoformat()

    url = f"{BASE_URL}/api/settings/check-version/?last_updated={old_timestamp}"
    print(f"GET {url}")
    print(f"Last Updated: {old_timestamp}")

    response = requests.get(url)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(json.dumps(data, indent=2))

        if data.get('settings_changed'):
            print("\n💡 Result: Settings have changed (expected)")
        else:
            print("\n⚠️ Result: Settings haven't changed")
    else:
        print(f"\n❌ FAILED: {response.text}")


def test_check_version_with_current_timestamp(updated_at):
    """Test GET /api/settings/check-version/ with current timestamp (should show no change)"""
    print("\n" + "="*60)
    print("TEST 4: Check Version (With Current Timestamp)")
    print("="*60)

    if not updated_at:
        print("⚠️ Skipping: No updated_at from previous test")
        return

    url = f"{BASE_URL}/api/settings/check-version/?last_updated={updated_at}"
    print(f"GET {url}")
    print(f"Last Updated: {updated_at}")

    response = requests.get(url)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(json.dumps(data, indent=2))

        if not data.get('settings_changed'):
            print("\n💡 Result: Settings haven't changed (expected)")
        else:
            print("\n⚠️ Result: Settings have changed (unexpected)")
    else:
        print(f"\n❌ FAILED: {response.text}")


def test_check_version_post():
    """Test POST /api/settings/check-version/ with JSON body"""
    print("\n" + "="*60)
    print("TEST 5: Check Version (POST with JSON Body)")
    print("="*60)

    url = f"{BASE_URL}/api/settings/check-version/"

    # Use yesterday's date
    old_timestamp = (datetime.now() - timedelta(days=1)).isoformat() + "Z"

    payload = {
        "last_updated": old_timestamp
    }

    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(
        url,
        json=payload,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(json.dumps(data, indent=2))

        if data.get('settings_changed'):
            print("\n💡 Result: Settings have changed")
        else:
            print("\n⚠️ Result: Settings haven't changed")
    else:
        print(f"\n❌ FAILED: {response.text}")


def main():
    print("\n" + "🚀" * 30)
    print("TESTING SETTINGS API ENDPOINTS")
    print("🚀" * 30)

    try:
        # Test 1: Get full settings
        updated_at = test_get_settings()

        # Test 2: Check version first time (no last_updated)
        test_check_version_first_time()

        # Test 3: Check version with old timestamp
        test_check_version_with_old_timestamp()

        # Test 4: Check version with current timestamp
        test_check_version_with_current_timestamp(updated_at)

        # Test 5: Check version via POST
        test_check_version_post()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        print("\n📱 Android Implementation:")
        print("   1. Read ANDROID_REALTIME_SETTINGS_GUIDE.md")
        print("   2. Use prompts from CLAUDE_ANDROID_PROMPTS.md")
        print("   3. Implement step by step in Android Studio")
        print("\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print(f"   Make sure Django is running at {BASE_URL}")
        print("   Run: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
