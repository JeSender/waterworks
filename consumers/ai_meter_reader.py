"""
FAST AI Water Meter Reading with Anti-Cheat Protection
Uses Claude Vision API to read REAL water meters only

SPEED OPTIMIZATIONS:
- Shorter prompt (faster AI response)
- Response caching (instant for same image)
- Max 300 tokens response
- Optimized JSON parsing
- Cached Anthropic client

Target: < 2 seconds server processing

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
# ANTHROPIC CLIENT SETUP (Cached for speed)
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
# FAST ANTI-CHEAT PROMPT (Shorter = Faster Response)
# ═══════════════════════════════════════════════════════════════════════════

FAST_PROMPT = """Read this water meter image. FIRST verify it's a REAL physical meter.

REAL METER has: round metal housing, glass dome cover, 5 mechanical digit wheels, red circular dials, center star indicator, pipe connections, brand markings, physical wear/dirt.

REJECT if you see: handwritten numbers on paper, printed numbers, phone/tablet/screen display, drawing/sketch, photocopy, digital LCD display, or partial image without meter housing.

If NOT a real meter, return:
{"success":false,"is_real_meter":false,"detected_as":"handwritten/printed/screen/drawing/photocopy/digital/partial","rejection_reason":"what you see","error":"Only real meters accepted","suggestion":"Take photo of actual water meter"}

If REAL meter, read the 5 mechanical digit wheels left-to-right. If digit is between two numbers (half-digit), use the bottom one. Ignore red dials.

Return:
{"success":true,"is_real_meter":true,"reading":"XXXXX","numeric_value":N,"confidence":"high/medium/low","notes":"any issues"}

JSON only, no other text."""


# ═══════════════════════════════════════════════════════════════════════════
# FAST AI METER READING VIEW
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def read_meter_ai(request):
    """
    FAST AI-powered water meter reading with Anti-Cheat.
    Target: < 2 seconds server processing.

    POST /api/read-meter/

    Body (JSON): {"image": "base64...", "previous_reading": 123}
    Or multipart: image file + previous_reading
    """
    start_time = time.time()

    try:
        # ─────────────────────────────────────────────────────────────
        # CHECK API KEY
        # ─────────────────────────────────────────────────────────────

        client = get_anthropic_client()
        if not client:
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'AI service not configured',
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }, status=503)

        # ─────────────────────────────────────────────────────────────
        # PARSE REQUEST
        # ─────────────────────────────────────────────────────────────

        image_data = None
        media_type = "image/jpeg"
        previous_reading = None

        # Handle file upload
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            media_type = image_file.content_type or 'image/jpeg'
            previous_reading = request.POST.get('previous_reading')

        # Handle JSON body
        elif request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                image_data = data.get('image', '')
                media_type = data.get('media_type', 'image/jpeg')
                previous_reading = data.get('previous_reading')

                # Remove data URL prefix
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

        # ─────────────────────────────────────────────────────────────
        # CHECK CACHE (Instant if found)
        # ─────────────────────────────────────────────────────────────

        # Use first 500 chars of base64 for quick hash
        image_hash = hashlib.md5(image_data[:500].encode()).hexdigest()
        cache_key = f'meter_ai_{image_hash}'

        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            logger.info(f"⚡ CACHE HIT: {cached_result['processing_time_ms']}ms")
            return JsonResponse(cached_result)

        # ─────────────────────────────────────────────────────────────
        # CALL CLAUDE AI (Fast settings)
        # ─────────────────────────────────────────────────────────────

        logger.info("⚡ Calling Claude AI...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,  # Short response = faster
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
                                "text": FAST_PROMPT
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

        # ─────────────────────────────────────────────────────────────
        # PARSE RESPONSE (Fast)
        # ─────────────────────────────────────────────────────────────

        response_text = response.content[0].text.strip()

        try:
            # Direct parse first (fastest)
            if response_text.startswith('{'):
                result = json.loads(response_text)
            else:
                # Find JSON in response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start >= 0 and end > start:
                    result = json.loads(response_text[start:end])
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

        # ─────────────────────────────────────────────────────────────
        # ADD METADATA
        # ─────────────────────────────────────────────────────────────

        processing_time = int((time.time() - start_time) * 1000)
        result['processing_time_ms'] = processing_time
        result['from_cache'] = False

        # ─────────────────────────────────────────────────────────────
        # VALIDATION (Optional)
        # ─────────────────────────────────────────────────────────────

        if result.get('success') and previous_reading:
            try:
                prev = int(previous_reading)
                curr = result.get('numeric_value', 0)

                if curr < prev:
                    result['validation_warning'] = f'Decreased: {prev} → {curr}'
                    result['validation_status'] = 'decreased'
                elif curr - prev > 100:
                    result['validation_warning'] = f'High: +{curr - prev} m³'
                    result['validation_status'] = 'high_consumption'
                else:
                    result['validation_status'] = 'normal'
                    result['consumption'] = curr - prev
            except (ValueError, TypeError):
                pass

        # ─────────────────────────────────────────────────────────────
        # CACHE & LOG
        # ─────────────────────────────────────────────────────────────

        if result.get('success'):
            cache.set(cache_key, result, 300)  # Cache 5 minutes
            logger.info(f"⚡ SUCCESS: {result.get('reading')} in {processing_time}ms")
        elif not result.get('is_real_meter'):
            logger.info(f"⚡ REJECTED: {result.get('detected_as')} in {processing_time}ms")
        else:
            logger.warning(f"⚡ ERROR in {processing_time}ms")

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
# FAST HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_GET
def ai_health_check(request):
    """
    Fast health check - no AI call needed.
    GET /api/ai-health/
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)

    if not api_key:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'error': 'ANTHROPIC_API_KEY not configured'
        }, status=503)

    # Just check if client can be created (no API call)
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
