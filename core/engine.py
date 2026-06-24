import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "artifacts" / "model.pkl"
PREP_PATH = BASE_DIR / "artifacts" / "preprocessor.pkl"

class ShieldEngine:
    def __init__(self):
        # Load the artifacts
        self.model = joblib.load(MODEL_PATH)
        self.prep = joblib.load(PREP_PATH)
        # The exact 8 features used during training
        self.feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count', 
                             'protocol_type', 'service', 'flag']

    def score(self, log_data: dict):
        try:
            # 1. Convert single dict to a DataFrame (1 row)
            df = pd.DataFrame([log_data])
            
            # 2. Filter to only the 8 features the model knows
            df_filtered = df[self.feature_cols]
            
            # 3. Transform using the saved preprocessor
            X_transformed = self.prep.transform(df_filtered)
            
            # 4. Get the anomaly score
            raw_score = self.model.decision_function(X_transformed)[0]
            
            # 5. Map to 0-5 threat level
            if raw_score > 0.1: threat = 0
            elif raw_score > 0.05: threat = 1
            elif raw_score > 0: threat = 2
            elif raw_score > -0.05: threat = 3
            elif raw_score > -0.1: threat = 4
            else: threat = 5
            
            return threat, "ANOMALY" if raw_score < 0 else "BASELINE"
        
        except Exception as e:
            # This will now print the specific error to your terminal for debugging
            print(f"🚨 Engine Error: {e}")
            return 2, "ERR"
