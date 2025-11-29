"""
IMPROVED AI Water Meter Reading with Anti-Cheat Protection
Better digit recognition for mechanical odometer wheels

@author Jest - CS Thesis 2025
Smart Meter Reading Application for Balilihan Waterworks
"""

import base64
import json
import hashlib
import time
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# ANTHROPIC CLIENT SETUP
# ═══════════════════════════════════════════════════════════════════════════

_client = None


def get_anthropic_client():
    """Get cached Anthropic client."""
    global _client
    if _client is not None:
        return _client

    try:
        import anthropic
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if not api_key:
            return None
        _client = anthropic.Anthropic(api_key=api_key)
        return _client
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# IMPROVED METER READING PROMPT (Better digit recognition)
# ═══════════════════════════════════════════════════════════════════════════

METER_READING_PROMPT = """You are reading a water meter for Balilihan Waterworks billing system.

## STEP 1: VERIFY REAL METER

Check for: round housing, glass dome, mechanical odometer wheels, red dials, pipes.
If NOT a real meter (handwritten, printed, screen, drawing), return:
{"success":false,"is_real_meter":false,"detected_as":"TYPE","rejection_reason":"REASON"}

## STEP 2: READ DIGITS CAREFULLY

The odometer has 5 WHITE boxes with BLACK numbers on rotating wheels.
Read LEFT to RIGHT, one digit at a time.

CRITICAL RULES:
1. Each wheel shows numbers 0-9
2. Look at the CENTER of each white box for the main digit
3. If a wheel is BETWEEN two numbers (transitioning):
   - Look which number takes MORE space in the window
   - If exactly half, use the LOWER number
4. Numbers on wheels are: 0,1,2,3,4,5,6,7,8,9
5. Be careful with similar-looking digits:
   - 1 vs 7 (1 has no top bar)
   - 6 vs 8 (6 is open at top)
   - 6 vs 0 (6 has tail at bottom)
   - 4 vs 9 (4 has open top)

## STEP 3: VERIFY YOUR READING

After reading all 5 digits, double-check:
- Does each digit look correct?
- Are any digits transitioning (between numbers)?
- Read again to confirm

## STEP 4: CHECK ORIENTATION

If image is rotated, look for "m³" symbol to find correct orientation.
The "m³" should be on the RIGHT side of the digits.

## RESPONSE FORMAT

Return JSON only:
{
  "success": true,
  "is_real_meter": true,
  "reading": "XXXXX",
  "numeric_value": XXXXX,
  "confidence": "high/medium/low",
  "digit_details": [
    {"position": 1, "value": X, "certainty": "clear/transitioning/unclear"},
    {"position": 2, "value": X, "certainty": "clear/transitioning/unclear"},
    {"position": 3, "value": X, "certainty": "clear/transitioning/unclear"},
    {"position": 4, "value": X, "certainty": "clear/transitioning/unclear"},
    {"position": 5, "value": X, "certainty": "clear/transitioning/unclear"}
  ],
  "rotation_applied": 0,
  "notes": "any observations"
}

IMPORTANT: Take your time. Read each digit carefully. Billing depends on accuracy."""


# ═══════════════════════════════════════════════════════════════════════════
# MAIN AI METER READING VIEW
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def read_meter_ai(request):
    """
    AI-powered water meter reading with improved accuracy.

    POST /api/read-meter/
    """
    start_time = time.time()

    try:
        # Check API key
        client = get_anthropic_client()
        if not client:
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'AI service not configured',
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }, status=503)

        # Parse request
        image_data = None
        media_type = "image/jpeg"
        previous_reading = None

        if 'image' in request.FILES:
            image_file = request.FILES['image']
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            media_type = image_file.content_type or 'image/jpeg'
            previous_reading = request.POST.get('previous_reading')

        elif request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                image_data = data.get('image', '')
                media_type = data.get('media_type', 'image/jpeg')
                previous_reading = data.get('previous_reading')

                if image_data.startswith('data:'):
                    parts = image_data.split(',', 1)
                    if len(parts) == 2:
                        image_data = parts[1]

            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'is_real_meter': False,
                    'error': 'Invalid JSON'
                }, status=400)

        if not image_data:
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'No image provided'
            }, status=400)

        # Check cache
        image_hash = hashlib.md5(image_data[:1000].encode()).hexdigest()
        cache_key = f'meter_ai_{image_hash}'

        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return JsonResponse(cached_result)

        # Call Claude AI
        logger.info("Calling Claude AI for meter reading...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": METER_READING_PROMPT
                            }
                        ]
                    }
                ]
            )
        except Exception as api_error:
            logger.error(f"Claude API error: {api_error}")
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'AI service unavailable',
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }, status=503)

        # Parse response
        response_text = response.content[0].text.strip()

        try:
            if response_text.startswith('{'):
                result = json.loads(response_text)
            else:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    result = json.loads(response_text[start_idx:end_idx])
                else:
                    result = {
                        'success': False,
                        'is_real_meter': False,
                        'error': 'No JSON in AI response'
                    }
        except json.JSONDecodeError:
            result = {
                'success': False,
                'is_real_meter': False,
                'error': 'Invalid AI response'
            }

        # Add metadata
        processing_time = int((time.time() - start_time) * 1000)
        result['processing_time_ms'] = processing_time
        result['from_cache'] = False

        # Validation against previous reading
        if result.get('success') and previous_reading:
            try:
                prev = int(previous_reading)
                curr = result.get('numeric_value', 0)

                if curr < prev:
                    result['validation_warning'] = f'Reading decreased: {prev} → {curr}'
                    result['validation_status'] = 'decreased'
                elif curr - prev > 100:
                    result['validation_warning'] = f'High consumption: +{curr - prev} m³'
                    result['validation_status'] = 'high_consumption'
                else:
                    result['validation_status'] = 'normal'
                    result['consumption'] = curr - prev
            except (ValueError, TypeError):
                pass

        # Cache successful results
        if result.get('success'):
            cache.set(cache_key, result, 300)
            logger.info(f"SUCCESS: Reading {result.get('reading')} in {processing_time}ms")
        else:
            logger.info(f"REJECTED/ERROR in {processing_time}ms")

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Error: {e}")
        return JsonResponse({
            'success': False,
            'is_real_meter': False,
            'error': str(e),
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_GET
def ai_health_check(request):
    """Fast health check."""
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)

    if not api_key:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'ANTHROPIC_API_KEY not configured'
        }, status=503)

    client = get_anthropic_client()
    if client:
        return JsonResponse({
            'status': 'healthy',
            'ai_available': True
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'Failed to create client'
        }, status=503)
