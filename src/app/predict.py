"""Load the trusted, project-built model and produce labeled probabilities."""

import joblib


def load_model(path):
    model = joblib.load(path)
    if not hasattr(model, "predict_proba") or not hasattr(model, "classes_"):
        raise ValueError("Invalid classification model")
    return model


def predict(model, text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter a book summary.")
    probabilities = model.predict_proba([text.strip()])[0]
    return sorted(
        zip(model.classes_, map(float, probabilities)),
        key=lambda item: item[1],
        reverse=True,
    )[:3]
