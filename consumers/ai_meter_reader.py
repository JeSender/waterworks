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

First, is this a real physical water meter? (Not a photo of paper, screen, or handwritten numbers)

If it's a real meter, please read the 5-digit display carefully. The meter has 5 white boxes with black numbers on rotating wheels.

Look at each digit one by one, from left to right:
- Digit 1 (leftmost): What number do you see?
- Digit 2: What number?
- Digit 3: What number?
- Digit 4: What number?
- Digit 5 (rightmost): What number?

If any digit is between two numbers (transitioning), use the number that takes more space in the window.

Ignore the small red dials - those are decimals.

Tell me the complete 5-digit reading."""


def extract_reading_from_response(response_text):
    """
    Extract the 5-digit meter reading from Claude's natural response.
    Returns (reading_string, numeric_value, confidence, digit_details, notes)
    """
    text = response_text.lower()

    # Check if Claude says it's not a real meter
    not_real_phrases = [
        "not a real meter", "not a real water meter",
        "handwritten", "written on paper", "printed",
        "screen", "display", "drawing", "sketch",
        "cannot read", "can't read", "unable to read",
        "not a meter", "isn't a meter", "is not a meter"
    ]

    for phrase in not_real_phrases:
        if phrase in text:
            # Try to determine what it is
            detected_as = "unknown"
            if "handwritten" in text or "written" in text:
                detected_as = "handwritten"
            elif "printed" in text:
                detected_as = "printed"
            elif "screen" in text or "display" in text:
                detected_as = "screen"
            elif "drawing" in text or "sketch" in text:
                detected_as = "drawing"

            return None, None, None, None, detected_as

    # Try to find 5 consecutive digits (the reading)
    # Pattern: 5 digits together like "00216" or "00 216" or "0 0 2 1 6"

    # First try: Find explicit "reading is XXXXX" or "reading: XXXXX"
    reading_patterns = [
        r'reading\s*(?:is|:)\s*["\']?(\d{5})["\']?',
        r'meter\s*read(?:s|ing)?\s*["\']?(\d{5})["\']?',
        r'(\d{5})\s*(?:m³|cubic|meters)',
        r'complete.*?reading.*?(\d{5})',
        r'final.*?reading.*?(\d{5})',
    ]

    for pattern in reading_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reading = match.group(1)
            return reading, int(reading), "high", None, None

    # Second try: Find "X, X, X, X, X" pattern (digits listed)
    digit_list_pattern = r'(\d)\s*[,\-\s]\s*(\d)\s*[,\-\s]\s*(\d)\s*[,\-\s]\s*(\d)\s*[,\-\s]\s*(\d)'
    match = re.search(digit_list_pattern, response_text)
    if match:
        reading = ''.join(match.groups())
        return reading, int(reading), "high", None, None

    # Third try: Look for individual digit mentions
    # "first digit: 0", "second digit: 0", etc.
    digit_words = ['first', 'second', 'third', 'fourth', 'fifth']
    digits_found = []

    for word in digit_words:
        pattern = rf'{word}\s*(?:digit|number|wheel)?\s*[:\-]?\s*(\d)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            digits_found.append(match.group(1))

    if len(digits_found) == 5:
        reading = ''.join(digits_found)
        return reading, int(reading), "high", None, None

    # Fourth try: Look for "Digit 1: X" pattern
    digit_num_pattern = r'digit\s*(\d)\s*[:\-]?\s*(\d)'
    matches = re.findall(digit_num_pattern, text, re.IGNORECASE)
    if len(matches) >= 5:
        digits_dict = {int(m[0]): m[1] for m in matches}
        if all(i in digits_dict for i in range(1, 6)):
            reading = ''.join(digits_dict[i] for i in range(1, 6))
            return reading, int(reading), "high", None, None

    # Fifth try: Find any 5-digit number in the response
    five_digit_matches = re.findall(r'\b(\d{5})\b', response_text)
    if five_digit_matches:
        # Take the last one (usually the final answer)
        reading = five_digit_matches[-1]
        return reading, int(reading), "medium", None, None

    # Sixth try: Look for digits mentioned with positions
    position_pattern = r'position\s*(\d)[:\s]*(\d)'
    matches = re.findall(position_pattern, text, re.IGNORECASE)
    if len(matches) >= 5:
        digits_dict = {int(m[0]): m[1] for m in matches}
        if all(i in digits_dict for i in range(1, 6)):
            reading = ''.join(digits_dict[i] for i in range(1, 6))
            return reading, int(reading), "high", None, None

    # Could not extract reading
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
        cache_key = f'meter_natural_{image_hash}'

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
                max_tokens=1024,  # Allow Claude to explain
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
        logger.info(f"Claude response: {response_text[:200]}...")

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
                'ai_response': response_text[:500],  # Include part of Claude's explanation
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
            result = {
                'success': False,
                'is_real_meter': True,
                'error': 'Could not extract reading from response',
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
            'mode': 'natural_conversation'
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'Client init failed'
        }, status=503)
