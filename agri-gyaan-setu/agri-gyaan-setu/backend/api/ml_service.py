import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'new_crop_recommendation_model.pkl')
CROP_MAPPING_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'new_crop_mapping.pkl')

# Load model and mapping lazily to avoid startup failures in some environments
def _load_model():
    global _MODEL, _MAPPING
    try:
        _MODEL
    except NameError:
        _MODEL = None
    try:
        _MAPPING
    except NameError:
        _MAPPING = None

    if _MODEL is None:
        if os.path.exists(MODEL_PATH):
            _MODEL = joblib.load(MODEL_PATH)
        else:
            _MODEL = None

    if _MAPPING is None:
        if os.path.exists(CROP_MAPPING_PATH):
            _MAPPING = joblib.load(CROP_MAPPING_PATH)
        else:
            _MAPPING = {}

    return _MODEL, _MAPPING


def predict_crop(features):
    """Predict crop name from features.

    The model expects four features: [N, P, K, pH].
    This helper will trim extra features or pad missing ones with 0.
    """
    model, crop_mapping = _load_model()
    # Ensure features is a list
    try:
        f = list(features)
    except Exception:
        f = [0, 0, 0, 0]

    EXPECTED = 4
    if len(f) > EXPECTED:
        # Trim to expected (take first N,P,K,pH)
        f = f[:EXPECTED]
    elif len(f) < EXPECTED:
        # Pad missing values with zeros
        f = f + [0] * (EXPECTED - len(f))

    # Convert to 2D numpy array without feature names
    X = np.array([f], dtype=float)

    if model is None:
        # No model available — return a safe default
        return crop_mapping.get(0, 'Unknown')

    try:
        prediction = model.predict(X)
        # prediction may be numeric code or name depending on model
        raw = prediction[0]
        try:
            crop_code = int(round(float(raw)))
            return crop_mapping.get(crop_code, str(raw))
        except Exception:
            return str(raw)
    except Exception:
        # On any model error, return a fallback
        return crop_mapping.get(0, 'Unknown')
