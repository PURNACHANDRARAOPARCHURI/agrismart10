from django.test import TestCase
from api import price_model
from pathlib import Path


class PriceModelTest(TestCase):
    def test_train_and_predict(self):
        base = Path(__file__).resolve().parents[3]
        dataset = base / 'frontend' / 'assets' / 'dataset1.csv'
        # Train model (should not raise)
        m = price_model.train_and_save_model(str(dataset))
        self.assertIn('type', m)

        loaded = price_model.load_model()
        self.assertIsNotNone(loaded)

        preds = price_model.predict_next_months(6)
        self.assertEqual(len(preds), 6)
        # Predictions should be numeric
        for p in preds:
            self.assertIsInstance(p, float)
