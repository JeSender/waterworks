#!/usr/bin/env python
"""
Quick API Test Script for Android App Integration
Run this to verify your API returns all required fields
"""

import requests
import json

# ========== CONFIGURATION ==========
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "your_username"  # ← CHANGE THIS
PASSWORD = "your_password"  # ← CHANGE THIS

# ===================================


def test_api():
    """Test the meter reading API endpoint"""

    print("=" * 60)
    print("ANDROID APP API INTEGRATION TEST")
    print("=" * 60)

    # Step 1: Login
    print("\n📝 Step 1: Testing Login...")
    print(f"   URL: {BASE_URL}/api/login/")

    try:
        login_response = requests.post(
            f"{BASE_URL}/api/login/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10
        )

        if login_response.status_code == 200:
            print("   ✅ Login successful!")
            session_cookie = login_response.cookies.get("sessionid")
            if not session_cookie:
                print("   ⚠️  Warning: No session cookie received")
                return False
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed! Is the server running?")
        print(f"   Try: python manage.py runserver")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Step 2: Get Consumers
    print("\n📝 Step 2: Testing Get Consumers...")
    print(f"   URL: {BASE_URL}/api/consumers/")

    try:
        consumers_response = requests.get(
            f"{BASE_URL}/api/consumers/",
            cookies={"sessionid": session_cookie},
            timeout=10
        )

        if consumers_response.status_code == 200:
            consumers = consumers_response.json()
            print(f"   ✅ Found {len(consumers)} consumers")

            if consumers:
                print(f"\n   📋 First Consumer:")
                first = consumers[0]
                print(f"      ID: {first.get('id')}")
                print(f"      Account: {first.get('account_number')}")
                print(f"      Name: {first.get('name')}")
                print(f"      Latest Reading: {first.get('latest_confirmed_reading')}")
            else:
                print("   ⚠️  No consumers found in database")
                print("   Add test consumer first!")
                return False
        else:
            print(f"   ❌ Failed: {consumers_response.status_code}")
            print(f"   Response: {consumers_response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Step 3: Submit Reading
    print("\n📝 Step 3: Testing Submit Meter Reading...")
    print(f"   URL: {BASE_URL}/api/meter-readings/")

    if consumers:
        consumer = consumers[0]
        previous = consumer['latest_confirmed_reading']
        new_reading = previous + 25  # Add 25 cubic meters

        reading_data = {
            "consumer_id": consumer['id'],
            "reading": new_reading,
            "reading_date": "2025-01-15"
        }

        print(f"\n   📤 Sending:")
        print(f"      Consumer ID: {reading_data['consumer_id']}")
        print(f"      New Reading: {reading_data['reading']}")
        print(f"      Date: {reading_data['reading_date']}")

        try:
            reading_response = requests.post(
                f"{BASE_URL}/api/meter-readings/",
                json=reading_data,
                cookies={"sessionid": session_cookie},
                timeout=10
            )

            if reading_response.status_code == 200:
                result = reading_response.json()
                print("\n   ✅ Reading submitted successfully!")

                print("\n" + "=" * 60)
                print("📄 BILL DETAILS RESPONSE:")
                print("=" * 60)
                print(json.dumps(result, indent=2))

                # Verify all required fields
                print("\n" + "=" * 60)
                print("🔍 FIELD VALIDATION:")
                print("=" * 60)

                required_fields = [
                    'status',
                    'message',
                    'consumer_name',
                    'account_number',
                    'reading_date',
                    'previous_reading',
                    'current_reading',
                    'consumption',
                    'rate',
                    'total_amount',
                    'field_staff_name'
                ]

                all_present = True
                for field in required_fields:
                    if field in result:
                        value = result[field]
                        print(f"   ✅ {field:20s} = {value}")
                    else:
                        print(f"   ❌ {field:20s} = MISSING!")
                        all_present = False

                print("=" * 60)

                if all_present:
                    print("\n🎉 SUCCESS! ALL 11 REQUIRED FIELDS PRESENT!")
                    print("\n✅ Your API is ready for Android app integration")

                    # Verify calculation
                    prev = result.get('previous_reading', 0)
                    curr = result.get('current_reading', 0)
                    cons = result.get('consumption', 0)
                    rate = result.get('rate', 0)
                    total = result.get('total_amount', 0)

                    expected_cons = curr - prev
                    print(f"\n📊 Bill Calculation Check:")
                    print(f"   Previous: {prev} m³")
                    print(f"   Current: {curr} m³")
                    print(f"   Consumption: {cons} m³ (Expected: {expected_cons})")
                    print(f"   Rate: ₱{rate}/m³")
                    print(f"   Total Amount: ₱{total}")

                    if cons == expected_cons:
                        print(f"   ✅ Consumption calculation correct!")
                    else:
                        print(f"   ⚠️  Consumption mismatch!")

                    return True
                else:
                    print("\n❌ FAILED! Some required fields are missing")
                    print("   Check the implementation")
                    return False

            else:
                print(f"\n   ❌ Failed: {reading_response.status_code}")
                print(f"   Response: {reading_response.text}")
                return False

        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            return False

    return False


if __name__ == "__main__":
    print("\n🚀 Starting API Test...")
    print(f"Server: {BASE_URL}")
    print(f"Username: {USERNAME}")
    print("-" * 60)

    if USERNAME == "your_username" or PASSWORD == "your_password":
        print("\n⚠️  WARNING: Please update USERNAME and PASSWORD in this script!")
        print("   Edit the CONFIGURATION section at the top of this file")
    else:
        success = test_api()

        print("\n" + "=" * 60)
        if success:
            print("✅ TEST PASSED - API IS WORKING CORRECTLY")
            print("\nNext steps:")
            print("1. Test with Android app")
            print("2. Deploy to production")
        else:
            print("❌ TEST FAILED - PLEASE FIX ISSUES ABOVE")
            print("\nCheck:")
            print("1. Server is running (python manage.py runserver)")
            print("2. Username/password are correct")
            print("3. Database has test consumers")
            print("4. SystemSetting is configured")
        print("=" * 60)
