import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "artifacts" / "model.pkl"
PREP_PATH = BASE_DIR / "artifacts" / "preprocessor.pkl"

class ShieldEngine:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.prep = joblib.load(PREP_PATH)

    def score(self, log_data: dict):
        try:
            # Transform raw dictionary to model-ready vector
            X = self.prep.transform(log_data)
            # IsolationForest: negative scores are anomalies
            raw_score = self.model.decision_function(X)[0]
            
            # Map to 0-5 threat level
            if raw_score > 0.1: threat = 0      # Very normal
            elif raw_score > 0.05: threat = 1   # Baseline
            elif raw_score > 0: threat = 2      # Minor drift
            elif raw_score > -0.05: threat = 3  # Warning
            elif raw_score > -0.1: threat = 4   # High Risk
            else: threat = 5                    # Critical Anomaly
            
            return threat, "ANOMALY" if raw_score < 0 else "BASELINE"
        except Exception as e:
            print(f"Engine Error: {e}")
            return 2, "PARSE_ERR"
