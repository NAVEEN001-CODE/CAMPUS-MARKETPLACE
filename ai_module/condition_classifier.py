"""
Product Condition Classifier using MobileNetV2
Uses a pre-trained MobileNetV2 model to analyze product images and
classify their visible condition as Good, Moderate, or Damaged.
"""

import numpy as np
import cv2
from PIL import Image

# Lazy-load TensorFlow to avoid slow startup
_model = None


def _get_model():
    """Lazy-load MobileNetV2 model (downloads ~14MB on first use)."""
    global _model
    if _model is None:
        from tensorflow.keras.applications import MobileNetV2
        _model = MobileNetV2(weights='imagenet', include_top=True)
    return _model


def _preprocess_image(image_path):
    """Preprocess image for MobileNetV2 input (224x224, normalized)."""
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array


def _analyze_image_features(image_path):
    """
    Analyze low-level image features for condition assessment.
    Uses edge density, color uniformity, and brightness distribution.
    """
    image = cv2.imread(image_path)
    if image is None:
        return {'edge_density': 0, 'brightness': 0, 'saturation': 0}

    image = cv2.resize(image, (224, 224))

    # Edge density — damaged items often have irregular edges/scratches
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0)) / edges.size

    # Brightness analysis
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    brightness = float(np.mean(hsv[:, :, 2]))

    # Saturation — faded/old items tend to have lower saturation
    saturation = float(np.mean(hsv[:, :, 1]))

    # Color uniformity — standard deviation of hue
    hue_std = float(np.std(hsv[:, :, 0]))

    return {
        'edge_density': round(edge_density, 4),
        'brightness': round(brightness, 2),
        'saturation': round(saturation, 2),
        'hue_std': round(hue_std, 2)
    }


def classify_condition(image_path):
    """
    Classify product condition using MobileNetV2 predictions combined
    with image feature analysis.

    The model identifies what the object is (via ImageNet classes), and
    the image features (edges, brightness, saturation) help determine
    the condition of the item.

    Args:
        image_path (str): Path to the product image

    Returns:
        dict: {
            'label': str,          # 'Good', 'Moderate', or 'Damaged'
            'confidence': float,   # Confidence score 0.0 - 1.0
            'top_prediction': str, # What MobileNetV2 thinks the object is
            'features': dict       # Raw feature values for documentation
        }
    """
    try:
        from tensorflow.keras.applications.mobilenet_v2 import decode_predictions

        # Step 1: Get MobileNetV2 predictions (object recognition)
        model = _get_model()
        img_array = _preprocess_image(image_path)
        predictions = model.predict(img_array, verbose=0)
        decoded = decode_predictions(predictions, top=3)[0]
        top_prediction = decoded[0][1]  # Human-readable label
        top_confidence = float(decoded[0][2])

        # Step 2: Analyze image features
        features = _analyze_image_features(image_path)

        # Step 3: Condition scoring algorithm
        # High saturation + good brightness + moderate edges = Good condition
        # Low saturation or extreme edges = signs of damage/wear
        condition_score = 0.0

        # Brightness score (ideal: 80-180)
        if 80 <= features['brightness'] <= 180:
            condition_score += 35
        elif 50 <= features['brightness'] <= 200:
            condition_score += 20
        else:
            condition_score += 5

        # Saturation score (higher = more vibrant = typically better condition)
        if features['saturation'] >= 80:
            condition_score += 30
        elif features['saturation'] >= 40:
            condition_score += 20
        else:
            condition_score += 5

        # Edge density score (moderate edges = defined product shape)
        if 0.05 <= features['edge_density'] <= 0.25:
            condition_score += 25  # Clean edges, well-maintained
        elif features['edge_density'] < 0.05:
            condition_score += 15  # Too smooth — possibly blurry
        else:
            condition_score += 5   # Too many edges — scratches/damage

        # Model confidence bonus
        condition_score += top_confidence * 10

        # Classify
        if condition_score >= 70:
            label = 'Good'
        elif condition_score >= 45:
            label = 'Moderate'
        else:
            label = 'Damaged'

        confidence = min(condition_score / 100.0, 1.0)

        return {
            'label': label,
            'confidence': round(confidence, 2),
            'top_prediction': top_prediction.replace('_', ' ').title(),
            'features': features
        }

    except Exception as e:
        print(f"[Condition Classifier Error] {e}")
        # Fallback to feature-only analysis
        try:
            features = _analyze_image_features(image_path)
            score = (features['brightness'] / 255 * 40) + \
                    (features['saturation'] / 255 * 40) + \
                    (max(0, 0.3 - features['edge_density']) / 0.3 * 20)
            if score >= 60:
                label = 'Good'
            elif score >= 35:
                label = 'Moderate'
            else:
                label = 'Damaged'
            return {
                'label': label,
                'confidence': round(score / 100, 2),
                'top_prediction': 'Unknown',
                'features': features
            }
        except:
            return {
                'label': 'Unknown',
                'confidence': 0.0,
                'top_prediction': 'Error',
                'features': {}
            }
