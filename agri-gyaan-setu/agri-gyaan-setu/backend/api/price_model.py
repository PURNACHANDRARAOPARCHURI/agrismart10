import os
import pickle
import csv
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent / 'ml_models'
MODEL_PATH = MODEL_DIR / 'price_model.pkl'

def _ensure_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

def _load_dataset(csv_path):
    # Very small CSV loader: expects at least columns 'Month' and 'Price' or similar.
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def _detect_price_column(rows, sample_size=200):
    if not rows:
        return None
    # Collect candidate columns
    cols = list(rows[0].keys())
    scores = {c: 0 for c in cols}
    checked = 0
    for r in rows[:sample_size]:
        checked += 1
        for c in cols:
            v = r.get(c, '')
            try:
                float(v)
                scores[c] += 1
            except Exception:
                pass
    # Prefer columns whose name contains 'price'
    price_candidates = [c for c in cols if 'price' in c.lower()]
    if price_candidates:
        # pick candidate with highest numeric score
        best = max(price_candidates, key=lambda c: scores.get(c, 0))
        return best
    # otherwise pick column with highest numeric parse rate
    best = max(cols, key=lambda c: scores.get(c, 0))
    if scores.get(best, 0) >= max(1, checked // 4):
        return best
    return None

def train_and_save_model(csv_path):
    """Train a simple linear regression on the provided CSV and save it.

    The function tries to use scikit-learn LinearRegression. If scikit-learn
    isn't available, it will fall back to a trivial mean predictor.
    The CSV is expected to have a 'Price' column (numeric). We'll train a
    single-feature regression using the row index as the time feature.
    This is intentionally simple; replace with ARIMA or more advanced models
    for production.
    """
    _ensure_model_dir()

    try:
        from sklearn.linear_model import LinearRegression
        import numpy as np
    except Exception:
        # fallback: save a simple dict with mean
        rows = _load_dataset(csv_path)
        prices = []
        for r in rows:
            v = r.get('Price') or r.get('price') or r.get('PRICE')
            try:
                prices.append(float(v))
            except Exception:
                continue
        mean_price = sum(prices) / len(prices) if prices else 0.0
        model_obj = {'type': 'mean', 'mean': mean_price}
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_obj, f)
        return model_obj

    # Use sklearn path
    rows = _load_dataset(csv_path)
    price_col = _detect_price_column(rows)
    prices = []
    if price_col:
        for r in rows:
            v = r.get(price_col)
            try:
                prices.append(float(v))
            except Exception:
                continue
    else:
        # fallback to common names
        for r in rows:
            v = r.get('Price') or r.get('price') or r.get('PRICE')
            try:
                prices.append(float(v))
            except Exception:
                continue

    if len(prices) < 2:
        model_obj = {'type': 'mean', 'mean': sum(prices) / len(prices) if prices else 0.0}
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_obj, f)
        return model_obj

    X = [[i] for i in range(len(prices))]
    y = prices

    lr = LinearRegression()
    lr.fit(X, y)

    model_obj = {'type': 'linear', 'model': lr, 'train_len': len(prices)}
    with open(MODEL_PATH, 'wb') as f:
        # Use pickle for the sklearn model
        pickle.dump(model_obj, f)
    return model_obj

def load_model():
    if not MODEL_PATH.exists():
        return None
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def predict_next_months(n_months=6, start_index=None):
    """Return a list of n_months predicted prices.

    If a trained sklearn linear model is present, we predict forward using
    consecutive integer indices. If the model object contains 'train_len',
    predictions will start from that index (so forecasts continue from the
    end of the training data). If a mean model is present, return the mean
    repeated.
    """
    model_obj = load_model()
    if model_obj is None:
        return [0.0] * n_months

    if model_obj.get('type') == 'mean':
        m = float(model_obj.get('mean', 0.0))
        return [m for _ in range(n_months)]

    if model_obj.get('type') == 'linear':
        lr = model_obj['model']
        train_len = model_obj.get('train_len')
        if start_index is None:
            start = int(train_len) if train_len is not None else 0
        else:
            start = int(start_index)

        X_future = [[start + i] for i in range(n_months)]
        try:
            preds = lr.predict(X_future)
            return [float(p) for p in preds]
        except Exception:
            return [0.0] * n_months
