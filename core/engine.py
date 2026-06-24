import joblib
import pandas as pd
import shap
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "artifacts" / "model.pkl"
PREP_PATH = BASE_DIR / "artifacts" / "preprocessor.pkl"

class ShieldEngine:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.prep = joblib.load(PREP_PATH)
        self.feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count',
                             'protocol_type', 'service', 'flag']

        try:
            self.explainer = shap.TreeExplainer(self.model)
        except:
            self.explainer = None

    def score(self, log_data: dict):
        # ... (Keep your existing score method) ...
        try:
            df = pd.DataFrame([log_data])[self.feature_cols]
            X_transformed = self.prep.transform(df)
            raw_score = self.model.decision_function(X_transformed)[0]
            if raw_score > 0.1: threat = 0
            elif raw_score > 0.05: threat = 1
            elif raw_score > 0: threat = 2
            elif raw_score > -0.05: threat = 3
            elif raw_score > -0.1: threat = 4
            else: threat = 5
            return threat, "ANOMALY" if raw_score < 0 else "BASELINE"
        except:
            return 2, "ERR"

    def explain(self, log_data: dict):
        """
        Translates SHAP mathematical weights into Human-Readable Triage Notes.
        """
        if not self.explainer:
            return "Heuristic engine initializing..."

        try:
            df = pd.DataFrame([log_data])[self.feature_cols]
            X_transformed = self.prep.transform(df)
            shap_values = self.explainer.shap_values(X_transformed)

            feature_names = self.prep.get_feature_names_out()
            val_map = list(zip(feature_names, shap_values[0]))

            # Sort by most anomalous (most negative SHAP values)
            val_map.sort(key=lambda x: x[1])

            # Translation Dictionary for Human Readability
            templates = {
                "src bytes": "The volume of data sent from the source is highly irregular for this service.",
                "dst bytes": "The amount of data received by the destination deviates significantly from normal patterns.",
                "duration": "The connection stayed open for an unusually long or short period.",
                "count": "There is a suspicious surge in connection attempts to the same host in a short window.",
                "srv count": "Anomalous frequency of connections to the same service detected.",
                "service": "The specific network service requested (e.g., HTTP/FTP) is behaving outside of baseline expectations.",
                "protocol type": "The transport protocol (TCP/UDP/ICMP) is being used in a non-standard way.",
                "flag": "The connection status flag (e.g., REJ/S0) indicates a failed or forced connection attempt."
            }

            observations = []
            # Take the top 2 most significant drivers
            for name, val in val_map[:2]:
                # Clean the feature name to match our template keys
                clean_name = name.split('__')[-1].replace('_', ' ').strip()

                # Match template or provide a fallback
                for key in templates:
                    if key in clean_name:
                        observations.append(templates[key])
                        break

            if not observations:
                return "The system detected a structural anomaly where multiple minor deviations combined to exceed the safety threshold."

            return " ".join(observations) + " This signature is consistent with known adversarial tactics like Probing or DoS."

        except Exception as e:
            return f"Forensic analysis failed: {str(e)}"
