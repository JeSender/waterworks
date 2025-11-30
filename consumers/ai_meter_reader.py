"""
HIGHLY ACCURATE AI Water Meter Reading System
Optimized for Balilihan Waterworks - Maximum Accuracy

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
        logger.error("anthropic package not installed")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# HIGHLY ACCURATE METER READING PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

ACCURATE_METER_PROMPT = """You are reading a water meter. ACCURACY IS CRITICAL FOR BILLING.

## STEP 1: VERIFY REAL METER
Check for: metal housing, glass dome, mechanical wheels, red dials, pipes, m³ symbol.
If NOT real (handwritten, printed, screen), return:
{"success":false,"is_real_meter":false,"detected_as":"TYPE","rejection_reason":"REASON"}

## STEP 2: FIND CORRECT ORIENTATION
Find "m³" symbol - it should be on the RIGHT side of digits.
Find "×0.0001" or "H" marking - should be near the dial area.
The digits read LEFT to RIGHT.

## STEP 3: READ EACH DIGIT VERY CAREFULLY

The meter has 5 WHITE rectangular boxes. Each box shows ONE black digit (0-9).

**READ SLOWLY - ONE DIGIT AT A TIME:**

DIGIT 1 (leftmost): Look at the CENTER of the first white box. What number is shown?
DIGIT 2: Look at the CENTER of the second white box. What number is shown?
DIGIT 3: Look at the CENTER of the third white box. What number is shown?
DIGIT 4: Look at the CENTER of the fourth white box. What number is shown?
DIGIT 5 (rightmost): Look at the CENTER of the fifth white box. What number is shown?

**CRITICAL RULES FOR ACCURACY:**

1. FOCUS ON CENTER: Only read the number in the CENTER of each white box
2. IGNORE EDGES: Ignore any partial numbers visible at top/bottom edges
3. TRANSITIONING DIGITS: If a wheel is between two numbers:
   - Look which number takes MORE space (more than 50%)
   - Use that number
   - If exactly 50/50, use the LOWER number

**DIGIT IDENTIFICATION GUIDE:**

- 0: Oval/round shape, completely closed
- 1: Single vertical line, thin, no curves
- 2: Curved top, diagonal middle, flat bottom
- 3: Two curves on right side, open on left
- 4: Angular, open top, vertical line on right
- 5: Flat top, curved bottom
- 6: Curved, closed loop at BOTTOM, open at top
- 7: Flat top line, diagonal stroke down
- 8: Two closed loops, like snowman
- 9: Curved, closed loop at TOP, tail at bottom

**COMMON MISTAKES TO AVOID:**

- 1 vs 7: Check for top horizontal bar (7 has it, 1 doesn't)
- 6 vs 0: Check bottom (6 has curved tail inside, 0 is plain oval)
- 6 vs 8: Check top (6 is open, 8 is closed)
- 5 vs 6: Check top (5 is flat, 6 is curved)
- 2 vs 7: Check curve (2 has curved top, 7 is angular)

## STEP 4: VERIFY YOUR READING

After reading all 5 digits:
1. Read them again from LEFT to RIGHT
2. Say each digit out loud in your mind
3. Check if any digit looks transitioning
4. Confirm your final reading

## RESPONSE FORMAT (JSON only):

{
  "success": true,
  "is_real_meter": true,
  "reading": "XXXXX",
  "numeric_value": XXXXX,
  "confidence": "high/medium/low",
  "digit_details": [
    {"position": 1, "value": X, "status": "clear/transitioning"},
    {"position": 2, "value": X, "status": "clear/transitioning"},
    {"position": 3, "value": X, "status": "clear/transitioning"},
    {"position": 4, "value": X, "status": "clear/transitioning"},
    {"position": 5, "value": X, "status": "clear/transitioning"}
  ],
  "notes": "observations"
}

IMPORTANT: Read each digit individually and carefully. Do not guess. Billing accuracy depends on you."""


@csrf_exempt
@require_POST
def read_meter_ai(request):
    """AI-powered water meter reading with maximum accuracy."""
    start_time = time.time()

    try:
        client = get_anthropic_client()
        if not client:
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'AI service not configured',
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }, status=503)

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
        image_hash = hashlib.md5(image_data[:2000].encode()).hexdigest()
        cache_key = f'meter_v3_{image_hash}'

        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return JsonResponse(cached_result)

        # Call Claude AI with higher token limit for better accuracy
        logger.info("Calling Claude AI for accurate meter reading...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
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
                                "text": ACCURATE_METER_PROMPT
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
                        'error': 'No JSON in response'
                    }
        except json.JSONDecodeError:
            result = {
                'success': False,
                'is_real_meter': False,
                'error': 'Invalid response format'
            }

        # Add metadata
        processing_time = int((time.time() - start_time) * 1000)
        result['processing_time_ms'] = processing_time
        result['from_cache'] = False

        # Validation
        if result.get('success') and previous_reading:
            try:
                prev = int(float(previous_reading))
                curr = result.get('numeric_value', 0)
                consumption = curr - prev

                if curr < prev:
                    result['validation_warning'] = f'Reading decreased: {prev} → {curr}'
                    result['validation_status'] = 'decreased'
                    result['consumption'] = 0
                elif consumption > 200:
                    result['validation_warning'] = f'Very high: {consumption} m³'
                    result['validation_status'] = 'high'
                    result['consumption'] = consumption
                else:
                    result['validation_status'] = 'normal'
                    result['consumption'] = consumption
            except (ValueError, TypeError):
                pass

        # Cache for 5 minutes
        if result.get('success'):
            cache.set(cache_key, result, 300)
            logger.info(f"SUCCESS: {result.get('reading')} in {processing_time}ms")

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Error: {e}")
        return JsonResponse({
            'success': False,
            'is_real_meter': False,
            'error': str(e),
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }, status=500)


@csrf_exempt
@require_GET
def ai_health_check(request):
    """Health check endpoint."""
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)

    if not api_key:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'API key not configured'
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
            'error': 'Client init failed'
        }, status=503)
