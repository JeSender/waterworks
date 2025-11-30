"""
MAXIMUM ACCURACY AI Water Meter Reading System
Uses Claude's best model with extended thinking for browser-like performance

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
# SIMPLE, NATURAL PROMPT (Like talking to Claude in browser)
# ═══════════════════════════════════════════════════════════════════════════════

METER_PROMPT = """Look at this water meter image carefully.

First, verify this is a real physical water meter (not a photo of paper, screen, or drawing).

If it's a real meter, read the 5-digit display. The meter has 5 white boxes showing black numbers on rotating wheels. Read from left to right.

Important tips:
- Focus on the CENTER of each digit window
- If a digit is between two numbers, use the one taking more space
- Ignore the small red dials (those are decimals)
- Common confusions: 1 vs 7 (check for top bar), 6 vs 8 (check if top is open)

Return your answer as JSON:
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
  "notes": "any observations"
}

If NOT a real meter:
{"success": false, "is_real_meter": false, "detected_as": "type", "rejection_reason": "reason"}"""


@csrf_exempt
@require_POST
def read_meter_ai(request):
    """
    AI-powered water meter reading using Claude's best vision model.
    Optimized for maximum accuracy like browser experience.
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
        cache_key = f'meter_v4_{image_hash}'

        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return JsonResponse(cached_result)

        # Call Claude AI - Using claude-sonnet-4-20250514 (best for vision tasks)
        logger.info("Calling Claude AI (Sonnet 4) for meter reading...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,  # Allow for extended thinking
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000  # Let Claude think before answering
                },
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
                                "text": METER_PROMPT
                            }
                        ]
                    }
                ],
                temperature=1  # Required for extended thinking
            )
        except Exception as api_error:
            error_str = str(api_error)
            logger.error(f"Claude API error: {error_str}")

            # If extended thinking fails, try without it
            if "thinking" in error_str.lower() or "budget" in error_str.lower():
                logger.info("Retrying without extended thinking...")
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
                                        "text": METER_PROMPT
                                    }
                                ]
                            }
                        ]
                    )
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    return JsonResponse({
                        'success': False,
                        'is_real_meter': False,
                        'error': 'AI service unavailable',
                        'processing_time_ms': int((time.time() - start_time) * 1000)
                    }, status=503)
            else:
                return JsonResponse({
                    'success': False,
                    'is_real_meter': False,
                    'error': 'AI service unavailable',
                    'processing_time_ms': int((time.time() - start_time) * 1000)
                }, status=503)

        # Extract response text (handle extended thinking response format)
        response_text = ""
        thinking_text = ""

        for block in response.content:
            if block.type == "thinking":
                thinking_text = block.thinking
                logger.info(f"Claude thinking: {thinking_text[:200]}...")
            elif block.type == "text":
                response_text = block.text.strip()

        # Parse JSON response
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
                        'error': 'No JSON in response',
                        'raw_response': response_text[:500]
                    }
        except json.JSONDecodeError:
            result = {
                'success': False,
                'is_real_meter': False,
                'error': 'Invalid response format',
                'raw_response': response_text[:500]
            }

        # Add metadata
        processing_time = int((time.time() - start_time) * 1000)
        result['processing_time_ms'] = processing_time
        result['from_cache'] = False
        result['model'] = 'claude-sonnet-4-20250514'
        result['extended_thinking'] = bool(thinking_text)

        # Validation against previous reading
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

        # Cache successful results
        if result.get('success'):
            cache.set(cache_key, result, 300)
            logger.info(f"SUCCESS: {result.get('reading')} (confidence: {result.get('confidence')}) in {processing_time}ms")

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
            'model': 'claude-sonnet-4-20250514',
            'features': ['vision', 'extended_thinking']
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'Client init failed'
        }, status=503)
