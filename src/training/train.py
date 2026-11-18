"""Train from a private GCS CSV and publish the fitted pipeline and report."""
import json
import logging
import os
import tempfile
from pathlib import Path

import joblib
from google.cloud import storage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.training.preprocessing import prepare_records


def main():
    logging.basicConfig(level=logging.INFO)
    bucket = storage.Client().bucket(os.environ["BUCKET_NAME"])
    source_name = os.environ.get("DATA_BLOB", "data/raw/data.csv")
    prefix = os.environ.get("OUTPUT_PREFIX", "models/latest").rstrip("/")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        dataset = root / "data.csv"
        bucket.blob(source_name).download_to_filename(str(dataset))
        records, data_report = prepare_records(dataset)
        texts, labels = zip(*records)
        x_train, x_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=43, stratify=labels)
        model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000, strip_accents="unicode", sublinear_tf=True)),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")),
        ])
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        classes = list(model.classes_)
        report = {"dataset": data_report, "split": {"seed": 43, "train": len(x_train), "test": len(x_test)},
                  "accuracy": accuracy_score(y_test, predictions), "macro_f1": f1_score(y_test, predictions, average="macro"),
                  "weighted_f1": f1_score(y_test, predictions, average="weighted"),
                  "labels": classes, "confusion_matrix": confusion_matrix(y_test, predictions, labels=classes).tolist(),
                  "classification_report": classification_report(y_test, predictions, labels=classes, output_dict=True, zero_division=0)}
        model_path = root / "model.joblib"
        report_path = root / "evaluation.json"
        joblib.dump(model, model_path, compress=3)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        bucket.blob(f"{prefix}/model.joblib").upload_from_filename(str(model_path))
        bucket.blob(f"{prefix}/evaluation.json").upload_from_filename(str(report_path), content_type="application/json")
        logging.info("Training complete: %s", json.dumps({k: report[k] for k in ("dataset", "split", "accuracy", "macro_f1", "weighted_f1")}))


if __name__ == "__main__":
    main()
