import pandas as pd
import joblib
import os
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Setup paths relative to this script
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "KDDTrain+.arff"
ARTIFACT_DIR = BASE_DIR / "artifacts"

# Standard NSL-KDD Column Names
COLUMNS = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes",
    "land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted",
    "num_root","num_file_creations","num_shells","num_access_files",
    "num_outbound_cmds","is_host_login","is_guest_login","count",
    "srv_count","serror_rate","srv_serror_rate","rerror_rate",
    "srv_rerror_rate","same_srv_rate","diff_srv_rate","srv_diff_host_rate",
    "dst_host_count","dst_host_srv_count","dst_host_same_srv_rate",
    "dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate",
    "dst_host_srv_serror_rate","dst_host_rerror_rate",
    "dst_host_srv_rerror_rate","label","difficulty"
]

def train_shield():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    if not DATA_PATH.exists():
        print(f"❌ Error: {DATA_PATH} not found.")
        return

    print(f"📂 Manually parsing ARFF file: {DATA_PATH}")
    
    # Robust ARFF parsing: Find where @data starts and read as CSV
    data_lines = []
    start_reading = False
    with open(DATA_PATH, 'r') as f:
        for line in f:
            if start_reading:
                if line.strip(): # Skip empty lines
                    data_lines.append(line.strip())
            elif line.lower().startswith('@data'):
                start_reading = True

    # Convert lines to DataFrame
    from io import StringIO
    csv_content = "\n".join(data_lines)
    df = pd.read_csv(StringIO(csv_content), names=COLUMNS)

    # 1. Feature Selection
    num_features = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count']
    cat_features = ['protocol_type', 'service', 'flag']
    
    print("⚙️ Transforming Categorical Features & Scaling Numerics...")
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
    ])

    X = df[num_features + cat_features]
    preprocessor.fit(X)
    X_transformed = preprocessor.transform(X)

    print(f"🧠 Training Isolation Forest on {X_transformed.shape[0]} samples...")
    # Unsupervised detection: contamination is the estimated % of attacks in the data
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42, n_jobs=-1)
    model.fit(X_transformed)

    # 2. Persist Engine Artifacts
    joblib.dump(model, ARTIFACT_DIR / 'model.pkl')
    joblib.dump(preprocessor, ARTIFACT_DIR / 'preprocessor.pkl')
    
    print(f"✅ Success! Engine artifacts saved to {ARTIFACT_DIR}")
    print(f"Engine Feature Dimension: {X_transformed.shape[1]} inputs mapped.")

if __name__ == "__main__":
    train_shield()
