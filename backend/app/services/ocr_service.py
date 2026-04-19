"""
OCR extraction service for image-based claim ingestion.
"""

from __future__ import annotations

import re

import numpy as np
from app.services.image_enhancement_agent import enhance_image_for_ocr

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None


def _clean_extracted_text(text: str) -> str:
    """Normalize OCR output into clean readable text."""
    if not text:
        return ""
    # Keep printable ASCII, normalize whitespace/newlines.
    cleaned = re.sub(r"[^\x20-\x7E\n\t]", " ", text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{2,}", "\n", cleaned)
    return cleaned.strip()


def _preprocess_for_ocr(image_bgr: np.ndarray) -> np.ndarray:
    """Apply OCR-friendly preprocessing."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    # Adaptive threshold handles social-media screenshots better.
    adaptive = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    # Morphological opening removes tiny noise speckles.
    kernel = np.ones((1, 1), np.uint8)
    opened = cv2.morphologyEx(adaptive, cv2.MORPH_OPEN, kernel)
    return opened


def _score_ocr_text(text: str) -> float:
    """Heuristic OCR quality score to choose the better extraction path."""
    if not text:
        return 0.0
    text = str(text).strip()
    if not text:
        return 0.0
    alnum_ratio = sum(ch.isalnum() for ch in text) / max(1, len(text))
    word_count = len(re.findall(r"[A-Za-z0-9]{2,}", text))
    return float((alnum_ratio * 0.7) + (min(word_count, 40) / 40.0) * 0.3)


def _run_ocr_best_of_paths(image_bgr: np.ndarray) -> str:
    """
    Run OCR on baseline + enhanced paths and keep the better deterministic output.
    """
    baseline = _clean_extracted_text(
        pytesseract.image_to_string(_preprocess_for_ocr(image_bgr), config="--oem 3 --psm 6")
    )
    enhanced_bgr = enhance_image_for_ocr(image_bgr)
    enhanced = _clean_extracted_text(
        pytesseract.image_to_string(_preprocess_for_ocr(enhanced_bgr), config="--oem 3 --psm 6")
    )
    return enhanced if _score_ocr_text(enhanced) >= _score_ocr_text(baseline) else baseline


def extract_text_from_image(image_path: str) -> str:
    """
    Extract clean text from an image path.
    """
    if cv2 is None or pytesseract is None:
        raise RuntimeError("OCR dependencies missing. Install pytesseract and opencv-python.")
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Unable to read image from path")
    return _run_ocr_best_of_paths(image)


def extract_text_from_bytes(image_bytes: bytes) -> str:
    """
    Extract clean text from raw image bytes.
    """
    if cv2 is None or pytesseract is None:
        raise RuntimeError("OCR dependencies missing. Install pytesseract and opencv-python.")
    if not image_bytes:
        return ""
    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode uploaded image bytes")
    return _run_ocr_best_of_paths(image)
