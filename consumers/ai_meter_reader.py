"""
AI Water Meter Reading with Anti-Cheat Protection
Uses Claude Vision API to read REAL water meters only

Rejects:
- Handwritten numbers
- Printed numbers
- Screen displays
- Drawings/sketches
- Photocopies

@author Jest - CS Thesis 2025
Smart Meter Reading Application for Balilihan Waterworks
"""

import base64
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# ANTHROPIC CLIENT SETUP
# ═══════════════════════════════════════════════════════════════════════════

def get_anthropic_client():
    """Get Anthropic client with API key from settings."""
    try:
        import anthropic
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if not api_key:
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# THE ANTI-CHEAT PROMPT
# ═══════════════════════════════════════════════════════════════════════════

METER_READING_PROMPT = """You are a SECURE water meter reading system for Balilihan Waterworks, Philippines.

══════════════════════════════════════════════════════════════════════════════
SECURITY VERIFICATION - MUST DO FIRST!
══════════════════════════════════════════════════════════════════════════════

Your PRIMARY job is to verify this image shows a REAL PHYSICAL WATER METER.
You must REJECT anything that is not an actual water meter device.

CHARACTERISTICS OF A REAL WATER METER:

Physical Structure (REQUIRED):
- ROUND METAL/PLASTIC HOUSING - circular body, brass/blue/black/gray color
- GLASS OR PLASTIC DOME COVER - protective transparent cover over display
- PIPE CONNECTIONS - visible pipe fittings on the sides
- 3D PHYSICAL DEPTH - display sits INSIDE housing, not flat surface

Display Components (REQUIRED):
- MECHANICAL ODOMETER - 5 rotating number WHEELS (not printed digits)
- RED CIRCULAR DIALS - 3-4 small dials with red triangular pointers
- CENTER STAR/GEAR - rotating flow indicator in the middle
- "m³" MARKING - cubic meter unit indicator

Signs of Authenticity:
- BRAND MARKINGS - text like "Class B", "ISO 4064", manufacturer name
- SERIAL NUMBER - stamped or engraved ID number
- WEATHERING/WEAR - real meters show dirt, scratches, water stains
- OUTDOOR ENVIRONMENT - often surrounded by dirt, pipes, meter box

══════════════════════════════════════════════════════════════════════════════
MUST REJECT - These are NOT real meters:
══════════════════════════════════════════════════════════════════════════════

HANDWRITTEN NUMBERS
- Numbers written with pen/pencil on paper, cardboard, whiteboard
- Uneven spacing, varying line thickness, human writing style
- Flat paper surface without 3D depth

PRINTED NUMBERS
- Laser or inkjet printed digits on paper
- Perfect font-like characters
- Flat printed surface

SCREEN DISPLAYS
- Numbers shown on phone, tablet, computer, TV screen
- Visible pixels, screen bezel, backlight glow
- Digital display characteristics

DRAWINGS OR SKETCHES
- Hand-drawn meter representation
- Artistic rendering, not photographic

PHOTOCOPIES
- Photocopy or scan of a meter photo
- Flat, no depth, possibly grainy

DIGITAL METERS
- LCD/LED electronic displays
- Only accept MECHANICAL odometer meters

PARTIAL OR CROPPED
- Just numbers without meter housing
- Zoomed in so much that meter body isn't visible

══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMAT
══════════════════════════════════════════════════════════════════════════════

IF NOT A REAL WATER METER - Return this JSON:
{
    "success": false,
    "is_real_meter": false,
    "rejection_reason": "Detailed reason why this is not a real meter",
    "detected_as": "handwritten/printed/screen/drawing/photocopy/digital/partial/unknown",
    "what_i_see": "Brief description of what's actually in the image",
    "error": "This system only accepts real water meter devices.",
    "suggestion": "Please take a photo of an actual water meter installed on a pipe."
}

IF VERIFIED AS REAL METER - Then read and return this JSON:
{
    "success": true,
    "is_real_meter": true,
    "meter_verification": {
        "has_round_housing": true,
        "has_glass_cover": true,
        "has_mechanical_odometer": true,
        "has_red_dials": true,
        "has_center_indicator": true,
        "has_pipe_connections": true,
        "has_brand_markings": true,
        "shows_wear_or_dirt": true,
        "verification_confidence": "high/medium"
    },
    "reading": "XXXXX",
    "numeric_value": XXXXX,
    "confidence": "high/medium/low",
    "digits": [
        {"position": 1, "value": X, "status": "clear/transitioning/unclear"},
        {"position": 2, "value": X, "status": "clear/transitioning/unclear"},
        {"position": 3, "value": X, "status": "clear/transitioning/unclear"},
        {"position": 4, "value": X, "status": "clear/transitioning/unclear"},
        {"position": 5, "value": X, "status": "clear/transitioning/unclear"}
    ],
    "issues_detected": ["fog", "rotation", "dirt", "none"],
    "rotation_detected": 0,
    "notes": "Description of meter condition"
}

══════════════════════════════════════════════════════════════════════════════
READING INSTRUCTIONS (Only after verification passes)
══════════════════════════════════════════════════════════════════════════════

1. The main odometer has 5 white boxes with black mechanical wheels
2. Read digits LEFT to RIGHT
3. If image is rotated, look for "m³" to find correct orientation
4. HALF-DIGIT RULE: When wheel shows two numbers, use the BOTTOM one
5. Ignore the small red circular dials (they show decimals)

══════════════════════════════════════════════════════════════════════════════
REMEMBER: You protect a billing system. Be STRICT about verification.
Reject ANYTHING that isn't clearly a real, physical water meter device.
══════════════════════════════════════════════════════════════════════════════"""


# ═══════════════════════════════════════════════════════════════════════════
# MAIN AI METER READING VIEW
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def read_meter_ai(request):
    """
    AI-powered water meter reading endpoint with Anti-Cheat Protection.

    ONLY reads real water meter devices.
    Rejects handwritten, printed, or displayed numbers.
    Verifies physical meter characteristics.

    POST /api/read-meter/

    Request Body (JSON):
    {
        "image": "base64_encoded_image",
        "media_type": "image/jpeg",  // optional, defaults to image/jpeg
        "previous_reading": 12345    // optional, for validation
    }

    Or multipart/form-data:
    - image: file upload
    - previous_reading: optional integer

    Returns:
    - Success: reading, numeric_value, confidence, meter_verification
    - Failure: rejection_reason, detected_as, suggestion
    """
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
                'suggestion': 'Please contact administrator to configure ANTHROPIC_API_KEY'
            }, status=503)

        # ─────────────────────────────────────────────────────────────
        # PARSE REQUEST
        # ─────────────────────────────────────────────────────────────

        image_data = None
        media_type = "image/jpeg"
        previous_reading = None

        # Handle file upload (multipart/form-data)
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

                # Remove data URL prefix if present (data:image/jpeg;base64,...)
                if image_data.startswith('data:'):
                    parts = image_data.split(',', 1)
                    if len(parts) == 2:
                        # Extract media type from data URL
                        header = parts[0]
                        if 'image/png' in header:
                            media_type = 'image/png'
                        elif 'image/webp' in header:
                            media_type = 'image/webp'
                        image_data = parts[1]

            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'is_real_meter': False,
                    'error': 'Invalid JSON format'
                }, status=400)

        if not image_data:
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'No image provided',
                'suggestion': 'Please include an image in the request'
            }, status=400)

        # Validate base64
        try:
            base64.b64decode(image_data)
        except Exception:
            return JsonResponse({
                'success': False,
                'is_real_meter': False,
                'error': 'Invalid base64 image data'
            }, status=400)

        # ─────────────────────────────────────────────────────────────
        # BUILD PROMPT WITH VALIDATION
        # ─────────────────────────────────────────────────────────────

        prompt = METER_READING_PROMPT

        if previous_reading:
            prompt += f"""

══════════════════════════════════════════════════════════════════════════════
VALIDATION CHECK
══════════════════════════════════════════════════════════════════════════════
Previous meter reading: {previous_reading} m³
- New reading should be >= {previous_reading} (water consumption only increases)
- Flag if reading appears to have decreased
- Flag if consumption is unusually high (>100 m³ difference)"""

        # ─────────────────────────────────────────────────────────────
        # CALL CLAUDE VISION API
        # ─────────────────────────────────────────────────────────────

        logger.info("Sending image to Claude for verification and reading...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
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
                                "text": prompt
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
                'error': 'AI service temporarily unavailable',
                'suggestion': 'Please try again in a moment'
            }, status=503)

        # ─────────────────────────────────────────────────────────────
        # PARSE RESPONSE
        # ─────────────────────────────────────────────────────────────

        response_text = response.content[0].text
        logger.info(f"Claude response received (length: {len(response_text)})")

        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                result = json.loads(response_text[json_start:json_end])
            else:
                logger.error(f"No JSON found in response: {response_text[:200]}")
                result = {
                    'success': False,
                    'is_real_meter': False,
                    'error': 'Could not parse AI response',
                    'raw_response': response_text[:500]
                }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            result = {
                'success': False,
                'is_real_meter': False,
                'error': 'Invalid AI response format'
            }

        # ─────────────────────────────────────────────────────────────
        # LOG RESULT
        # ─────────────────────────────────────────────────────────────

        if result.get('success') and result.get('is_real_meter'):
            logger.info(f"ACCEPTED - Real meter. Reading: {result.get('reading')}, Confidence: {result.get('confidence')}")
        else:
            reason = result.get('rejection_reason', result.get('error', 'Unknown'))
            detected = result.get('detected_as', 'unknown')
            logger.warning(f"REJECTED - {reason} (detected as: {detected})")

        # ─────────────────────────────────────────────────────────────
        # VALIDATION AGAINST PREVIOUS READING
        # ─────────────────────────────────────────────────────────────

        if result.get('success') and previous_reading:
            try:
                prev = int(previous_reading)
                curr = result.get('numeric_value', 0)

                if curr < prev:
                    result['validation_warning'] = f'Reading decreased from {prev} to {curr}'
                    result['validation_status'] = 'decreased'
                elif curr - prev > 100:
                    result['validation_warning'] = f'High consumption: {curr - prev} m³'
                    result['validation_status'] = 'high_consumption'
                else:
                    result['validation_status'] = 'normal'
                    result['consumption'] = curr - prev

            except (ValueError, TypeError):
                pass

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Unexpected error in read_meter_ai: {e}")
        return JsonResponse({
            'success': False,
            'is_real_meter': False,
            'error': 'Server error',
            'suggestion': 'Please try again'
        }, status=500)


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@csrf_exempt
@require_GET
def ai_health_check(request):
    """
    Check if AI meter reading service is available.

    GET /api/ai-health/

    Returns:
    {
        "status": "healthy/unhealthy",
        "ai_available": true/false,
        "api_key_configured": true/false
    }
    """
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)

    if not api_key:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'api_key_configured': False,
            'error': 'ANTHROPIC_API_KEY not configured'
        }, status=503)

    client = get_anthropic_client()
    if not client:
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'api_key_configured': True,
            'error': 'Failed to initialize Anthropic client'
        }, status=503)

    try:
        # Quick test call
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "OK"}]
        )
        return JsonResponse({
            'status': 'healthy',
            'ai_available': True,
            'api_key_configured': True
        })
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'ai_available': False,
            'api_key_configured': True,
            'error': str(e)
        }, status=503)
