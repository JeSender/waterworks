"""
Image Preprocessing Module for Water Meter OCR
Enhances meter images for better digit recognition

Features:
- Grayscale conversion
- CLAHE contrast enhancement (handles foggy covers)
- Denoising (reduces dirt/scratches)
- Sharpening (makes digits clearer)
- Glare reduction

@author Jest - CS Thesis 2025
Smart Meter Reading Application for Balilihan Waterworks
"""

import base64
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

# Check if OpenCV is available
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not installed. Image preprocessing disabled. Run: pip install opencv-python-headless")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not installed. Run: pip install Pillow")


class MeterImagePreprocessor:
    """
    Preprocesses water meter images to improve OCR accuracy.

    Handles common issues:
    - Foggy/dirty glass covers
    - Poor lighting and glare
    - Low contrast digits
    - Noise from scratches/dirt
    """

    def __init__(self):
        self.preprocessing_applied = False
        self.preprocessing_steps = []

    def preprocess(self, image_base64: str) -> tuple:
        """
        Preprocess a base64 encoded image for better OCR.

        Args:
            image_base64: Base64 encoded image string

        Returns:
            tuple: (processed_base64, preprocessing_info)
        """
        if not OPENCV_AVAILABLE or not PIL_AVAILABLE:
            logger.warning("Preprocessing skipped - OpenCV or Pillow not available")
            return image_base64, {"applied": False, "reason": "Dependencies not available"}

        try:
            # Decode base64 to image
            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("Failed to decode image")
                return image_base64, {"applied": False, "reason": "Failed to decode image"}

            original_shape = img.shape
            self.preprocessing_steps = []

            # Step 1: Resize if too large (max 1920px on longest side)
            img = self._resize_if_needed(img)

            # Step 2: Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.preprocessing_steps.append("grayscale")

            # Step 3: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # Great for handling foggy/dirty covers
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            self.preprocessing_steps.append("clahe_contrast")

            # Step 4: Denoise to reduce dirt/scratches
            denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)
            self.preprocessing_steps.append("denoise")

            # Step 5: Sharpen to make digits clearer
            sharpened = self._sharpen(denoised)
            self.preprocessing_steps.append("sharpen")

            # Step 6: Normalize brightness
            normalized = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX)
            self.preprocessing_steps.append("normalize")

            # Convert back to BGR for consistent output
            final = cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)

            # Encode back to base64
            _, buffer = cv2.imencode('.jpg', final, [cv2.IMWRITE_JPEG_QUALITY, 92])
            processed_base64 = base64.b64encode(buffer).decode('utf-8')

            self.preprocessing_applied = True

            preprocessing_info = {
                "applied": True,
                "steps": self.preprocessing_steps,
                "original_size": f"{original_shape[1]}x{original_shape[0]}",
                "processed_size": f"{final.shape[1]}x{final.shape[0]}"
            }

            logger.info(f"Preprocessing complete: {self.preprocessing_steps}")
            return processed_base64, preprocessing_info

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return image_base64, {"applied": False, "reason": str(e)}

    def _resize_if_needed(self, img, max_size: int = 1920):
        """Resize image if larger than max_size."""
        height, width = img.shape[:2]

        if width <= max_size and height <= max_size:
            return img

        scale = min(max_size / width, max_size / height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        self.preprocessing_steps.append(f"resize_{new_width}x{new_height}")
        return resized

    def _sharpen(self, img):
        """Apply unsharp masking for sharpening."""
        # Create Gaussian blur
        blurred = cv2.GaussianBlur(img, (0, 0), 3)
        # Unsharp mask: original + (original - blurred) * amount
        sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
        return sharpened

    def enhance_for_digits(self, image_base64: str) -> tuple:
        """
        Enhanced preprocessing specifically for digit recognition.
        More aggressive processing for difficult images.

        Args:
            image_base64: Base64 encoded image string

        Returns:
            tuple: (processed_base64, preprocessing_info)
        """
        if not OPENCV_AVAILABLE or not PIL_AVAILABLE:
            return image_base64, {"applied": False, "reason": "Dependencies not available"}

        try:
            # Decode base64 to image
            image_bytes = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return image_base64, {"applied": False, "reason": "Failed to decode image"}

            self.preprocessing_steps = []

            # Resize
            img = self._resize_if_needed(img)

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.preprocessing_steps.append("grayscale")

            # Strong CLAHE for foggy covers
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            self.preprocessing_steps.append("strong_clahe")

            # Bilateral filter - preserves edges while smoothing
            bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
            self.preprocessing_steps.append("bilateral_filter")

            # Morphological operations to clean up
            kernel = np.ones((2, 2), np.uint8)
            morph = cv2.morphologyEx(bilateral, cv2.MORPH_CLOSE, kernel)
            self.preprocessing_steps.append("morphology")

            # Adaptive thresholding for better digit separation
            # Don't apply full threshold - just enhance contrast
            enhanced_contrast = cv2.convertScaleAbs(morph, alpha=1.3, beta=10)
            self.preprocessing_steps.append("contrast_boost")

            # Final sharpen
            sharpened = self._sharpen(enhanced_contrast)
            self.preprocessing_steps.append("sharpen")

            # Convert back to BGR
            final = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

            # Encode to base64
            _, buffer = cv2.imencode('.jpg', final, [cv2.IMWRITE_JPEG_QUALITY, 92])
            processed_base64 = base64.b64encode(buffer).decode('utf-8')

            preprocessing_info = {
                "applied": True,
                "mode": "enhanced_digits",
                "steps": self.preprocessing_steps
            }

            logger.info(f"Enhanced preprocessing complete: {self.preprocessing_steps}")
            return processed_base64, preprocessing_info

        except Exception as e:
            logger.error(f"Enhanced preprocessing failed: {e}")
            return image_base64, {"applied": False, "reason": str(e)}


def preprocess_meter_image(image_base64: str, enhanced: bool = False) -> tuple:
    """
    Convenience function for preprocessing meter images.

    Args:
        image_base64: Base64 encoded image
        enhanced: Use enhanced digit mode (more aggressive)

    Returns:
        tuple: (processed_base64, preprocessing_info)
    """
    preprocessor = MeterImagePreprocessor()

    if enhanced:
        return preprocessor.enhance_for_digits(image_base64)
    else:
        return preprocessor.preprocess(image_base64)


def is_preprocessing_available() -> bool:
    """Check if preprocessing dependencies are available."""
    return OPENCV_AVAILABLE and PIL_AVAILABLE
