"""
ENHANCED AI Water Meter Reading with Anti-Cheat Protection
Improved OCR accuracy with image preprocessing and detailed prompting

Features:
- OpenCV image preprocessing (CLAHE, denoise, sharpen)
- Detailed digit-by-digit reading instructions
- Per-digit confidence scoring
- Handles foggy covers, glare, and poor lighting
- Anti-cheat detection for fake meter images

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

# Import preprocessing module
try:
    from .image_preprocessing import preprocess_meter_image, is_preprocessing_available
    PREPROCESSING_AVAILABLE = is_preprocessing_available()
except ImportError:
    PREPROCESSING_AVAILABLE = False
    def preprocess_meter_image(img, enhanced=False):
        return img, {"applied": False, "reason": "Module not available"}

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


# ═══════════════════════════════════════════════════════════════════════════
# ENHANCED OCR PROMPT - Optimized for mechanical odometer reading
# ═══════════════════════════════════════════════════════════════════════════

METER_READING_PROMPT = """You are an expert water meter reader for Balilihan Waterworks billing system.
Your task is to accurately read a 5-digit mechanical odometer display.

═══════════════════════════════════════════════════════════════════════════════
STEP 1: VERIFY THIS IS A REAL PHYSICAL WATER METER
═══════════════════════════════════════════════════════════════════════════════

A REAL water meter has these characteristics:
✓ Round metal or plastic housing (brass, blue, black, or gray)
✓ Glass or plastic dome cover (may be foggy or dirty)
✓ 5-digit mechanical odometer with rotating number wheels
✓ Small RED circular dials with pointers (IGNORE these for reading)
✓ "m³" marking indicating cubic meters
✓ Pipe connections on the sides
✓ Physical depth - display sits INSIDE housing
✓ Signs of outdoor use: dirt, scratches, water stains

REJECT and return error if you see:
✗ Handwritten numbers on paper
✗ Printed numbers (inkjet/laser)
✗ Phone/tablet/computer screen display
✗ Drawing or sketch
✗ Photocopy of a meter
✗ Digital LCD/LED meter (only mechanical accepted)
✗ Just numbers without the meter housing visible

If NOT a real meter, return:
{"success":false,"is_real_meter":false,"detected_as":"TYPE","rejection_reason":"DESCRIPTION","error":"Only real mechanical water meters accepted","suggestion":"Take a clear photo of the actual water meter"}

═══════════════════════════════════════════════════════════════════════════════
STEP 2: CHECK IMAGE ORIENTATION
═══════════════════════════════════════════════════════════════════════════════

The "m³" symbol should be on the RIGHT side of the digit display.
If the image is rotated:
- Find the "m³" marking
- Mentally rotate the image so "m³" is on the right
- Then read the digits

═══════════════════════════════════════════════════════════════════════════════
STEP 3: LOCATE THE 5-DIGIT ODOMETER
═══════════════════════════════════════════════════════════════════════════════

The main reading display has:
- 5 separate WHITE rectangular windows
- Each window shows ONE BLACK digit (0-9)
- Digits are on ROTATING WHEELS (like a car odometer)
- Windows are arranged in a HORIZONTAL row

IMPORTANT: IGNORE the small RED circular dials!
The red dials show decimal fractions - they are NOT part of the main reading.
Only read the 5 BLACK digits in the WHITE windows.

═══════════════════════════════════════════════════════════════════════════════
STEP 4: READ EACH DIGIT CAREFULLY (LEFT TO RIGHT)
═══════════════════════════════════════════════════════════════════════════════

For EACH of the 5 digit positions, carefully identify the number:

DIGIT IDENTIFICATION GUIDE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 0 - Oval shape, completely closed, no internal lines                       │
│ 1 - Single vertical line, NO top bar, thinnest digit                       │
│ 2 - Curved top, diagonal middle, flat bottom (like a swan neck)            │
│ 3 - Two curved bumps on the right side, open on left                       │
│ 4 - Vertical line + horizontal line + diagonal, OPEN at top                │
│ 5 - Flat top, curves down then right at bottom                             │
│ 6 - Curved top-left, has a CLOSED LOOP at bottom                           │
│ 7 - Flat top bar + diagonal line going down-left, NO bottom bar            │
│ 8 - Two stacked loops, like a snowman                                      │
│ 9 - Has a CLOSED LOOP at top, tail curves down                             │
└─────────────────────────────────────────────────────────────────────────────┘

CRITICAL CONFUSION PAIRS TO WATCH:
• 1 vs 7: The "1" has NO top horizontal bar. The "7" HAS a top bar.
• 1 vs 2: The "1" is just a vertical line. The "2" curves at top.
• 2 vs 7: The "2" has a curved top AND flat bottom. The "7" has straight diagonal.
• 6 vs 8: The "6" is open at top-right. The "8" is closed all around.
• 6 vs 0: The "6" has a tail curving into bottom loop. The "0" is just an oval.
• 4 vs 9: The "4" is open at top. The "9" has a closed loop at top.

═══════════════════════════════════════════════════════════════════════════════
STEP 5: HANDLE TRANSITIONING DIGITS
═══════════════════════════════════════════════════════════════════════════════

When a wheel is BETWEEN two numbers (transitioning):
- The wheel rotates from LOWER number to HIGHER number
- Example: transitioning from 3 to 4

RULE: Use the digit that occupies MORE than 50% of the window.
- If the lower number takes more space → use the LOWER number
- If the higher number takes more space → use the HIGHER number
- If exactly 50/50 → use the LOWER number

Mark transitioning digits with status "transitioning" in your response.

═══════════════════════════════════════════════════════════════════════════════
STEP 6: DOUBLE-CHECK YOUR READING
═══════════════════════════════════════════════════════════════════════════════

Before responding:
1. Count that you have exactly 5 digits
2. Re-read each digit from left to right
3. Check for any transitioning digits
4. Verify the reading makes sense (leading zeros are normal)

═══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMAT (JSON ONLY - NO OTHER TEXT)
═══════════════════════════════════════════════════════════════════════════════

{
  "success": true,
  "is_real_meter": true,
  "reading": "XXXXX",
  "numeric_value": XXXXX,
  "confidence": "high/medium/low",
  "digit_details": [
    {"position": 1, "value": X, "confidence": "high/medium/low", "status": "clear/transitioning"},
    {"position": 2, "value": X, "confidence": "high/medium/low", "status": "clear/transitioning"},
    {"position": 3, "value": X, "confidence": "high/medium/low", "status": "clear/transitioning"},
    {"position": 4, "value": X, "confidence": "high/medium/low", "status": "clear/transitioning"},
    {"position": 5, "value": X, "confidence": "high/medium/low", "status": "clear/transitioning"}
  ],
  "image_quality": "good/foggy/dirty/glare/dark",
  "notes": "Any observations about difficult digits or image quality issues"
}

CONFIDENCE LEVELS:
- "high": Digit is clearly visible and unambiguous
- "medium": Digit is readable but slightly unclear (foggy/dirty glass)
- "low": Digit is difficult to read, best guess provided

═══════════════════════════════════════════════════════════════════════════════
REMEMBER: This reading will be used for BILLING. Accuracy is critical!
Take your time. Read each digit carefully. When in doubt, choose lower confidence.
═══════════════════════════════════════════════════════════════════════════════"""


# ═══════════════════════════════════════════════════════════════════════════
# MAIN API ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def read_meter_ai(request):
    """
    AI-powered water meter reading with image preprocessing.

    POST /api/read-meter/

    Request:
        - image: Base64 encoded image or file upload
        - media_type: Image MIME type (default: image/jpeg)
        - previous_reading: Optional previous reading for validation
        - preprocess: Enable image preprocessing (default: true)
        - enhanced_preprocess: Use aggressive preprocessing (default: false)

    Response:
        - success: Whether reading was successful
        - is_real_meter: Whether image shows a real meter
        - reading: 5-digit string reading
        - numeric_value: Integer value
        - confidence: Overall confidence level
        - digit_details: Per-digit breakdown
        - preprocessing_applied: Whether preprocessing was used
        - processing_time_ms: Total processing time
    """
    start_time = time.time()

    try:
        # Check API client
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
        do_preprocess = True
        enhanced_preprocess = False

        if 'image' in request.FILES:
            image_file = request.FILES['image']
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            media_type = image_file.content_type or 'image/jpeg'
            previous_reading = request.POST.get('previous_reading')
            do_preprocess = request.POST.get('preprocess', 'true').lower() == 'true'
            enhanced_preprocess = request.POST.get('enhanced_preprocess', 'false').lower() == 'true'

        elif request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                image_data = data.get('image', '')
                media_type = data.get('media_type', 'image/jpeg')
                previous_reading = data.get('previous_reading')
                do_preprocess = data.get('preprocess', True)
                enhanced_preprocess = data.get('enhanced_preprocess', False)

                # Remove data URL prefix if present
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

        # Check cache (use original image hash for cache key)
        image_hash = hashlib.md5(image_data[:2000].encode()).hexdigest()
        cache_key = f'meter_ai_v2_{image_hash}'

        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            logger.info(f"Cache hit: {cached_result.get('reading')} in {cached_result['processing_time_ms']}ms")
            return JsonResponse(cached_result)

        # Apply image preprocessing
        preprocessing_info = {"applied": False}
        processed_image = image_data

        if do_preprocess and PREPROCESSING_AVAILABLE:
            preprocess_start = time.time()
            processed_image, preprocessing_info = preprocess_meter_image(
                image_data,
                enhanced=enhanced_preprocess
            )
            preprocess_time = int((time.time() - preprocess_start) * 1000)
            preprocessing_info['time_ms'] = preprocess_time
            logger.info(f"Preprocessing took {preprocess_time}ms: {preprocessing_info}")

        # Call Claude Vision API
        logger.info("Calling Claude AI for meter reading...")
        ai_start = time.time()

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
                                    "data": processed_image
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
            ai_time = int((time.time() - ai_start) * 1000)
            logger.info(f"Claude API responded in {ai_time}ms")

        except Exception as api_error:
            logger.error(f"Claude API error: {api_error}")
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'AI service unavailable',
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }, status=503)

        # Parse AI response
        response_text = response.content[0].text.strip()

        try:
            if response_text.startswith('{'):
                result = json.loads(response_text)
            else:
                # Find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    result = json.loads(response_text[start_idx:end_idx])
                else:
                    result = {
                        'success': False,
                        'is_real_meter': False,
                        'error': 'No JSON in AI response',
                        'raw_response': response_text[:500]
                    }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, response: {response_text[:200]}")
            result = {
                'success': False,
                'is_real_meter': False,
                'error': 'Invalid AI response format'
            }

        # Add metadata
        processing_time = int((time.time() - start_time) * 1000)
        result['processing_time_ms'] = processing_time
        result['from_cache'] = False
        result['preprocessing'] = preprocessing_info

        # Validate against previous reading
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
            cache.set(cache_key, result, 300)  # 5 minute cache
            logger.info(f"SUCCESS: Reading {result.get('reading')} (confidence: {result.get('confidence')}) in {processing_time}ms")
        elif not result.get('is_real_meter', True):
            logger.info(f"REJECTED: {result.get('detected_as')} - {result.get('rejection_reason')}")
        else:
            logger.warning(f"ERROR: {result.get('error')} in {processing_time}ms")

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return JsonResponse({
            'success': False,
            'is_real_meter': False,
            'error': str(e),
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_GET
def ai_health_check(request):
    """
    Health check for AI meter reading service.

    GET /api/ai-health/

    Returns service status and available features.
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)

    if not api_key:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'preprocessing_available': PREPROCESSING_AVAILABLE,
            'error': 'ANTHROPIC_API_KEY not configured'
        }, status=503)

    client = get_anthropic_client()
    if client:
        return JsonResponse({
            'status': 'healthy',
            'ai_available': True,
            'preprocessing_available': PREPROCESSING_AVAILABLE,
            'features': {
                'image_preprocessing': PREPROCESSING_AVAILABLE,
                'clahe_enhancement': PREPROCESSING_AVAILABLE,
                'denoising': PREPROCESSING_AVAILABLE,
                'caching': True,
                'validation': True
            }
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'preprocessing_available': PREPROCESSING_AVAILABLE,
            'error': 'Failed to create AI client'
        }, status=503)
