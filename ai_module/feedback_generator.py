"""
Feedback Text Generator
Generates human-readable feedback based on blur detection and condition analysis results.
"""


def generate_feedback(blur_result, condition_result):
    """
    Generate automatic feedback text for a product listing based on
    AI analysis results.

    Args:
        blur_result (dict): Output from blur_detector.detect_blur()
        condition_result (dict): Output from condition_classifier.classify_condition()

    Returns:
        str: Multi-line feedback text with suggestions and observations
    """
    feedback_parts = []

    # ---- Image Quality Feedback ----
    quality = blur_result.get('quality_label', 'Unknown')
    blur_score = blur_result.get('blur_score', 0)

    if quality == 'Sharp':
        feedback_parts.append(
            "📸 **Excellent image quality!** Your photo is clear and sharp. "
            "This helps buyers see the product details clearly."
        )
    elif quality == 'Acceptable':
        feedback_parts.append(
            "📸 **Acceptable image quality.** The photo is reasonably clear. "
            "For better results, try uploading in natural lighting with a steady hand."
        )
    elif quality == 'Blurry':
        feedback_parts.append(
            "⚠️ **Image appears blurry.** We recommend re-uploading a clearer photo. "
            "Tips: Use good lighting, hold your camera steady, and avoid zooming in too much."
        )
    else:
        feedback_parts.append(
            "❓ **Could not assess image quality.** Please ensure the image is properly uploaded."
        )

    # ---- Condition Feedback ----
    condition = condition_result.get('label', 'Unknown')
    confidence = condition_result.get('confidence', 0)
    top_pred = condition_result.get('top_prediction', '')

    if condition == 'Good':
        feedback_parts.append(
            "✅ **Product condition: Good.** The item appears to be in good condition "
            f"(confidence: {confidence:.0%}). This should attract interested buyers!"
        )
    elif condition == 'Moderate':
        feedback_parts.append(
            "🔶 **Product condition: Moderate.** The item shows some signs of use "
            f"(confidence: {confidence:.0%}). Consider mentioning any wear or defects "
            "in your description to set accurate buyer expectations."
        )
    elif condition == 'Damaged':
        feedback_parts.append(
            "🔴 **Product condition: Needs attention.** The image suggests the item "
            f"may have visible wear or damage (confidence: {confidence:.0%}). "
            "Please describe any defects honestly. Transparency builds trust!"
        )
    else:
        feedback_parts.append(
            "❓ **Condition could not be determined.** Please ensure the product is "
            "clearly visible in the image."
        )

    # ---- Object Recognition Info ----
    if top_pred and top_pred not in ('Unknown', 'Error'):
        feedback_parts.append(
            f"🔍 **Detected item type:** {top_pred}. "
            "Make sure your title and category match the actual product."
        )

    # ---- General Tips ----
    tips = []
    if blur_result.get('is_blurry', False):
        tips.append("Re-upload a clearer photo for a higher trust score")
    if condition in ('Moderate', 'Damaged'):
        tips.append("Add details about product condition in your description")
    if confidence < 0.5:
        tips.append("Try a well-lit photo with the product centered in frame")

    if tips:
        feedback_parts.append("💡 **Tips to improve your listing:**")
        for tip in tips:
            feedback_parts.append(f"  • {tip}")

    return "\n\n".join(feedback_parts)
