import joblib
from pathlib import Path
from django.conf import settings

_model = None
_vectorizer = None


def load_model():
    global _model, _vectorizer
    if not _model:
        model_path = Path(settings.BASE_DIR) / 'hate_speech_model/training/models/model.pkl'
        model_data = joblib.load(model_path)
        _model = model_data['model']
        _vectorizer = model_data['vectorizer']
    return _model, _vectorizer
