"""
Blur Detection Module
Uses OpenCV Laplacian variance to measure image sharpness.
"""

import cv2
import numpy as np


def detect_blur(image_path, threshold=100.0):
    """
    Detect if an image is blurry using the Laplacian variance method.

    The Laplacian operator highlights regions of rapid intensity change.
    A well-focused image has high variance in its Laplacian, while a
    blurry image has low variance.

    Args:
        image_path (str): Path to the image file
        threshold (float): Blur threshold — below this value, image is considered blurry

    Returns:
        dict: {
            'blur_score': float,   # Laplacian variance (higher = sharper)
            'is_blurry': bool,     # True if blur_score < threshold
            'quality_label': str   # 'Sharp', 'Acceptable', or 'Blurry'
        }
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {
                'blur_score': 0.0,
                'is_blurry': True,
                'quality_label': 'Unreadable'
            }

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Resize for consistent analysis (avoid very large images skewing results)
        gray = cv2.resize(gray, (500, 500))

        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())

        # Classify quality
        if blur_score >= threshold * 1.5:
            quality_label = 'Sharp'
        elif blur_score >= threshold:
            quality_label = 'Acceptable'
        else:
            quality_label = 'Blurry'

        return {
            'blur_score': round(blur_score, 2),
            'is_blurry': blur_score < threshold,
            'quality_label': quality_label
        }

    except Exception as e:
        print(f"[Blur Detection Error] {e}")
        return {
            'blur_score': 0.0,
            'is_blurry': True,
            'quality_label': 'Error'
        }
