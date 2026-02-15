"""
Trust Score Calculator
Computes a composite trust score (0-100) based on image quality,
product condition, and description quality.
"""


def calculate_trust_score(blur_result, condition_result, description=''):
    """
    Calculate a composite trust score for a product listing.

    Formula:
        trust_score = (image_quality_score * 0.4) +
                      (condition_score * 0.4) +
                      (description_score * 0.2)

    Args:
        blur_result (dict): Output from blur_detector
        condition_result (dict): Output from condition_classifier
        description (str): Product description text

    Returns:
        int: Trust score from 0 to 100
    """
    # ---- 1. Image Quality Score (0-100) ----
    blur_score = blur_result.get('blur_score', 0.0)
    is_blurry = blur_result.get('is_blurry', True)

    if is_blurry:
        # Scale blurry images: 0 to 40 points
        image_quality_score = min(blur_score / 100.0 * 40, 40)
    else:
        # Scale sharp images: 60 to 100 points
        # Clamp blur_score to reasonable range (100 to 1000)
        normalized = min(blur_score, 1000) / 1000.0
        image_quality_score = 60 + (normalized * 40)

    image_quality_score = min(max(image_quality_score, 0), 100)

    # ---- 2. Condition Score (0-100) ----
    condition_label = condition_result.get('label', 'Unknown')
    condition_confidence = condition_result.get('confidence', 0.0)

    condition_base = {
        'Good': 90,
        'Moderate': 60,
        'Damaged': 30,
        'Unknown': 20
    }.get(condition_label, 20)

    # Weight by confidence
    condition_score = condition_base * condition_confidence
    condition_score = min(max(condition_score, 0), 100)

    # ---- 3. Description Quality Score (0-100) ----
    description_score = _evaluate_description(description)

    # ---- Composite Trust Score ----
    trust_score = (
        image_quality_score * 0.40 +
        condition_score * 0.40 +
        description_score * 0.20
    )

    return int(min(max(round(trust_score), 0), 100))


def _evaluate_description(description):
    """
    Evaluate the quality of a product description.

    Scoring criteria:
        - Length (longer = more informative, up to a point)
        - Contains price-relevant keywords
        - Contains condition keywords

    Args:
        description (str): Product description text

    Returns:
        float: Description quality score (0-100)
    """
    if not description or not description.strip():
        return 10  # Minimum score for empty description

    desc_lower = description.lower().strip()
    score = 0

    # Length scoring (max 40 points)
    word_count = len(desc_lower.split())
    if word_count >= 50:
        score += 40
    elif word_count >= 30:
        score += 30
    elif word_count >= 15:
        score += 20
    elif word_count >= 5:
        score += 10
    else:
        score += 5

    # Condition keywords (max 30 points)
    condition_keywords = [
        'new', 'used', 'good condition', 'like new', 'working',
        'functional', 'minor', 'scratch', 'wear', 'defect',
        'excellent', 'perfect', 'broken', 'damaged'
    ]
    condition_matches = sum(1 for kw in condition_keywords if kw in desc_lower)
    score += min(condition_matches * 10, 30)

    # Informative keywords (max 30 points)
    info_keywords = [
        'brand', 'model', 'year', 'size', 'color', 'weight',
        'original', 'warranty', 'receipt', 'purchased', 'month',
        'reason', 'selling', 'includes', 'accessories', 'box'
    ]
    info_matches = sum(1 for kw in info_keywords if kw in desc_lower)
    score += min(info_matches * 10, 30)

    return min(score, 100)


def get_trust_label(trust_score):
    """
    Get a human-readable trust label and color based on the trust score.

    Args:
        trust_score (int): Trust score 0-100

    Returns:
        dict: { 'label': str, 'color': str, 'icon': str }
    """
    if trust_score >= 80:
        return {'label': 'Highly Trusted', 'color': 'success', 'icon': '🟢'}
    elif trust_score >= 60:
        return {'label': 'Trusted', 'color': 'primary', 'icon': '🔵'}
    elif trust_score >= 40:
        return {'label': 'Moderate Trust', 'color': 'warning', 'icon': '🟡'}
    else:
        return {'label': 'Low Trust', 'color': 'danger', 'icon': '🔴'}
