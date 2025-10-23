import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'new_crop_recommendation_model.pkl')
CROP_MAPPING_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'new_crop_mapping.pkl')

model = joblib.load(MODEL_PATH)
crop_mapping = joblib.load(CROP_MAPPING_PATH)

def predict_crop(features):
    prediction = model.predict([features])
    crop_code = int(round(prediction[0]))  # Ensure it's an integer
    crop_name = crop_mapping.get(crop_code, "Unknown")
    return crop_name
