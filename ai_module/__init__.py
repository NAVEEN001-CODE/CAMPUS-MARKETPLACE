"""
AI Module for Campus Marketplace
Provides image analysis, condition classification, feedback, and trust scoring.
"""

from .blur_detector import detect_blur
from .condition_classifier import classify_condition
from .feedback_generator import generate_feedback
from .trust_scorer import calculate_trust_score


def analyze_product_image(image_path, description=''):
    """
    Perform complete AI analysis on a product image.

    Args:
        image_path (str): Path to the uploaded product image
        description (str): Product description text

    Returns:
        dict: Complete analysis results including blur, condition, feedback, trust score
    """
    # Step 1: Blur Detection
    blur_result = detect_blur(image_path)

    # Step 2: Condition Classification using MobileNetV2
    condition_result = classify_condition(image_path)

    # Step 3: Generate Feedback Text
    feedback = generate_feedback(blur_result, condition_result)

    # Step 4: Calculate Trust Score
    trust_score = calculate_trust_score(blur_result, condition_result, description)

    return {
        'blur_score': blur_result['blur_score'],
        'is_blurry': blur_result['is_blurry'],
        'condition_label': condition_result['label'],
        'condition_confidence': condition_result['confidence'],
        'feedback_text': feedback,
        'trust_score': trust_score
    }
