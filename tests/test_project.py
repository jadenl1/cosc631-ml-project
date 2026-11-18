import csv
import joblib
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from src.training.preprocessing import normalize_text, prepare_records
from src.app.predict import load_model, predict


def test_normalization():
    assert normalize_text('  One\n  two  ') == 'One two'
    assert normalize_text(None) == ''


def test_validation_and_duplicates(tmp_path):
    path = tmp_path / 'books.csv'
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['summary', 'genre'])
        writer.writerows([['A book', 'x'], ['a  book', 'x'], ['conflict', 'x'], ['CONFLICT', 'y'], ['', 'x'], ['other', 'x'], ['third', 'y'], ['fourth', 'y']])
    records, report = prepare_records(path)
    assert len(records) == 4
    assert report['duplicate_rows_removed'] == 1
    assert report['conflicting_rows_removed'] == 2
    assert report['missing_rows'] == 1
    path.write_text('title\nbook\n')
    with pytest.raises(ValueError):
        prepare_records(path)


def test_model_and_prediction(tmp_path):
    model = make_pipeline(TfidfVectorizer(), LogisticRegression()).fit(['space alien', 'space planet', 'magic wizard', 'magic dragon'], ['science', 'science', 'fantasy', 'fantasy'])
    path = tmp_path / 'model.joblib'
    joblib.dump(model, path)
    loaded = load_model(path)
    results = predict(loaded, 'space planet')
    assert results[0][0] == 'science'
    assert {label for label, _ in results} == set(loaded.classes_)
    assert sum(prob for _, prob in results) == pytest.approx(1)
    with pytest.raises(ValueError):
        predict(loaded, '  ')
    with pytest.raises(ValueError):
        predict(loaded, None)
