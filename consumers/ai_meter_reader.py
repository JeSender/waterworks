"""
AI Water Meter Reading for Android App
Natural conversation style like Claude browser for maximum accuracy

@author Jest - CS Thesis 2025
Smart Meter Reading Application for Balilihan Waterworks
"""

import base64
import json
import hashlib
import time
import re
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
# NATURAL PROMPT - Like talking to Claude in browser
# ═══════════════════════════════════════════════════════════════════════════════

NATURAL_PROMPT = """Look at this water meter image.

This is a MECHANICAL water meter with rotating odometer wheels. Please read the 5-digit BLACK number display.

IMPORTANT - How mechanical meters work:
- Each digit wheel rotates slowly as water flows
- Digits are often BETWEEN two numbers (half-showing two digits)
- When a digit is transitioning (showing parts of two numbers), read the LOWER number
- Example: If wheel shows half "3" and half "4", read it as "3" (not yet fully turned to 4)
- The rightmost digit moves fastest and is most likely to be mid-transition

Read each of the 5 white windows from LEFT to RIGHT:
- Digit 1 (leftmost): What number? (If between numbers, use lower)
- Digit 2: What number?
- Digit 3: What number?
- Digit 4: What number?
- Digit 5 (rightmost): What number? (Often mid-transition)

IGNORE the small RED dials - those are decimal fractions.

Tell me the complete 5-digit reading."""


def extract_reading_from_response(response_text):
    """
    Extract the 5-digit meter reading from Claude's natural response.
    PRIORITY: Try to find reading first. Only reject if clearly not a meter.
    """
    text = response_text.lower()
    original_text = response_text

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 1: TRY TO FIND THE 5-DIGIT READING FIRST (Priority!)
    # ═══════════════════════════════════════════════════════════════════════════

    # Pattern 1: Find explicit "reading is XXXXX" or "reading: XXXXX"
    reading_patterns = [
        r'reading\s*(?:is|:)\s*["\']?(\d{5})["\']?',
        r'complete\s*(?:5-digit\s*)?reading\s*(?:is|:)?\s*["\']?(\d{5})["\']?',
        r'meter\s*read(?:s|ing)?\s*(?:is|:)?\s*["\']?(\d{5})["\']?',
        r'(\d{5})\s*(?:m³|m3|cubic)',
        r'final\s*reading\s*(?:is|:)?\s*(\d{5})',
        r'the\s*reading\s*is\s*(\d{5})',
    ]

    for pattern in reading_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reading = match.group(1)
            logger.info(f"Found reading with pattern: {reading}")
            return reading, int(reading), "high", None, None

    # Pattern 2: Find "Digit X: Y" pattern
    digit_pattern = r'digit\s*(\d)\s*[:\-\(\)]?\s*(\d)'
    matches = re.findall(digit_pattern, text, re.IGNORECASE)
    if len(matches) >= 5:
        digits_dict = {}
        for m in matches:
            pos = int(m[0])
            val = m[1]
            if 1 <= pos <= 5:
                digits_dict[pos] = val
        if all(i in digits_dict for i in range(1, 6)):
            reading = ''.join(digits_dict[i] for i in range(1, 6))
            logger.info(f"Found reading from digit pattern: {reading}")
            return reading, int(reading), "high", None, None

    # Pattern 3: Find individual digits listed with words
    # "first digit: 0", "second digit: 0", etc.
    digit_words = [
        ('first', 1), ('second', 2), ('third', 3), ('fourth', 4), ('fifth', 5),
        ('1st', 1), ('2nd', 2), ('3rd', 3), ('4th', 4), ('5th', 5)
    ]
    digits_found = {}

    for word, pos in digit_words:
        patterns = [
            rf'{word}\s*(?:digit|number|wheel)?\s*[:\-\(\)]?\s*["\']?(\d)["\']?',
            rf'{word}[:\-\s]+(\d)',
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                digits_found[pos] = match.group(1)
                break

    if len(digits_found) >= 5 and all(i in digits_found for i in range(1, 6)):
        reading = ''.join(digits_found[i] for i in range(1, 6))
        logger.info(f"Found reading from word pattern: {reading}")
        return reading, int(reading), "high", None, None

    # Pattern 4: Find "X, X, X, X, X" or "X - X - X - X - X" pattern
    digit_list_patterns = [
        r'(\d)\s*,\s*(\d)\s*,\s*(\d)\s*,\s*(\d)\s*,\s*(\d)',
        r'(\d)\s*-\s*(\d)\s*-\s*(\d)\s*-\s*(\d)\s*-\s*(\d)',
        r'(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)',
    ]
    for pattern in digit_list_patterns:
        match = re.search(pattern, original_text)
        if match:
            reading = ''.join(match.groups())
            logger.info(f"Found reading from list pattern: {reading}")
            return reading, int(reading), "high", None, None

    # Pattern 5: Find any standalone 5-digit number
    five_digit_matches = re.findall(r'\b(\d{5})\b', original_text)
    if five_digit_matches:
        # Prefer the last one (usually the final answer)
        reading = five_digit_matches[-1]
        logger.info(f"Found reading from 5-digit match: {reading}")
        return reading, int(reading), "medium", None, None

    # Pattern 6: Look for "0" mentions (common in meter readings like 00216)
    # Find sequences like "0, 0, 2, 1, 6" even with text between
    zero_pattern = r'0.*?0.*?(\d).*?(\d).*?(\d)'
    match = re.search(zero_pattern, text)
    if match:
        reading = "00" + match.group(1) + match.group(2) + match.group(3)
        logger.info(f"Found reading from zero pattern: {reading}")
        return reading, int(reading), "medium", None, None

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 2: Only check for rejection if NO reading found
    # ═══════════════════════════════════════════════════════════════════════════

    # Only reject if Claude explicitly says it's NOT a real meter
    rejection_phrases = [
        "this is not a real meter",
        "this is not a water meter",
        "not a real water meter",
        "this is handwritten",
        "this is a photo of paper",
        "this appears to be handwritten",
        "i cannot read this",
        "unable to read the meter",
        "this is a drawing",
        "this is a sketch",
        "this is printed",
        "this is a screen",
        "this is not a physical meter"
    ]

    for phrase in rejection_phrases:
        if phrase in text:
            detected_as = "unknown"
            if "handwritten" in text:
                detected_as = "handwritten"
            elif "printed" in text:
                detected_as = "printed"
            elif "screen" in text:
                detected_as = "screen"
            elif "drawing" in text or "sketch" in text:
                detected_as = "drawing"

            logger.info(f"Rejected: {detected_as}")
            return None, None, None, None, detected_as

    # ═══════════════════════════════════════════════════════════════════════════
    # STEP 3: Could not find reading, but don't reject - return error
    # ═══════════════════════════════════════════════════════════════════════════
    logger.warning(f"Could not extract reading from: {text[:200]}")
    return None, None, None, None, "parse_failed"


@csrf_exempt
@require_POST
def read_meter_ai(request):
    """
    AI meter reading with natural conversation style.
    Like using Claude in browser for maximum accuracy.
    """
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
        image_hash = hashlib.md5(image_data[:2000].encode()).hexdigest()
        cache_key = f'meter_mechanical_v3_{image_hash}'

        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return JsonResponse(cached_result)

        # Call Claude AI with natural prompt
        logger.info("Calling Claude AI (natural conversation mode)...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
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
                                "text": NATURAL_PROMPT
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

        # Get Claude's natural response
        response_text = response.content[0].text.strip()
        logger.info(f"Claude response: {response_text[:300]}...")

        # Extract reading from natural response
        reading, numeric_value, confidence, digit_details, error_type = extract_reading_from_response(response_text)

        # Build result
        if reading:
            result = {
                'success': True,
                'is_real_meter': True,
                'reading': reading,
                'numeric_value': numeric_value,
                'confidence': confidence,
                'ai_response': response_text[:500],
            }
        elif error_type in ['handwritten', 'printed', 'screen', 'drawing', 'unknown']:
            result = {
                'success': False,
                'is_real_meter': False,
                'detected_as': error_type,
                'rejection_reason': response_text[:300],
                'error': 'Not a real water meter'
            }
        else:
            # parse_failed - still a real meter, just couldn't extract
            result = {
                'success': False,
                'is_real_meter': True,
                'error': 'Could not extract reading',
                'ai_response': response_text[:500]
            }

        # Add metadata
        processing_time = int((time.time() - start_time) * 1000)
        result['processing_time_ms'] = processing_time
        result['from_cache'] = False

        # Validate against previous reading
        if result.get('success') and previous_reading:
            try:
                prev = int(float(previous_reading))
                curr = result.get('numeric_value', 0)
                consumption = curr - prev

                if curr < prev:
                    result['validation_warning'] = f'Decreased: {prev} → {curr}'
                    result['validation_status'] = 'decreased'
                    result['consumption'] = 0
                elif consumption > 200:
                    result['validation_warning'] = f'High: {consumption} m³'
                    result['validation_status'] = 'high'
                    result['consumption'] = consumption
                else:
                    result['validation_status'] = 'normal'
                    result['consumption'] = consumption
            except (ValueError, TypeError):
                pass

        # Cache successful results
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
            'ai_available': True,
            'mode': 'mechanical_meter_v3'
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'Client init failed'
        }, status=503)
