"""
Image Enhancement Agent for OCR.

Enhances noisy screenshot/social-media images before OCR to improve text quality.
Deterministic, side-effect free, and optimized for CPU execution.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


def _estimate_blur(gray: np.ndarray) -> float:
    """Variance of Laplacian as a blur sharpness proxy (higher is sharper)."""
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _estimate_contrast(gray: np.ndarray) -> float:
    """Std-dev intensity as a simple contrast proxy."""
    return float(np.std(gray))


def _estimate_brightness(gray: np.ndarray) -> float:
    """Average brightness (0-255)."""
    return float(np.mean(gray))


def _deskew(gray: np.ndarray) -> np.ndarray:
    """
    Deskew text by estimating dominant angle from thresholded foreground pixels.
    Returns original image when skew estimation is unreliable.
    """
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 100:
        return gray

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.35:
        return gray

    h, w = gray.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def _adaptive_enhance(gray: np.ndarray) -> np.ndarray:
    """
    Enhance image based on observed quality:
    - CLAHE for contrast
    - Denoise
    - Optional sharpening for blurred images
    - Optional gamma lift for very dark images
    """
    blur = _estimate_blur(gray)
    contrast = _estimate_contrast(gray)
    brightness = _estimate_brightness(gray)

    clip_limit = 2.6 if contrast < 45 else 2.1
    tile_size = (8, 8)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    enhanced = clahe.apply(gray)

    enhanced = cv2.bilateralFilter(enhanced, d=7, sigmaColor=35, sigmaSpace=35)

    if blur < 95:
        gauss = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=1.3)
        enhanced = cv2.addWeighted(enhanced, 1.55, gauss, -0.55, 0)

    if brightness < 90:
        gamma = 0.82
        table = np.array(
            [((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)],
            dtype=np.uint8,
        )
        enhanced = cv2.LUT(enhanced, table)

    return enhanced


def enhance_image_for_ocr(image_bgr: np.ndarray) -> np.ndarray:
    """
    Main Image Enhancement Agent entrypoint.

    Returns enhanced BGR image for downstream OCR preprocessing.
    """
    if cv2 is None:
        raise RuntimeError("OpenCV is required for image enhancement.")
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Invalid input image for enhancement.")

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    deskewed = _deskew(gray)
    enhanced_gray = _adaptive_enhance(deskewed)
    return cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)

