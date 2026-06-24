import requests
import time
import random
from pathlib import Path

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1/ingest"
BASE_DIR = Path(__file__).resolve().parent.parent
TEST_DATA_PATH = BASE_DIR / "data" / "KDDTest+.arff"

# Full NSL-KDD Column List
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

def load_test_logs():
    print(f"📂 Reading Test Dataset: {TEST_DATA_PATH}")
    logs = []
    start_reading = False
    if not TEST_DATA_PATH.exists():
        print(f"❌ File not found: {TEST_DATA_PATH}")
        return []

    with open(TEST_DATA_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if start_reading:
                if line and not line.startswith('%'):
                    # Split by comma and strip any extra whitespace/quotes
                    parts = [p.strip().strip("'").strip('"') for p in line.split(',')]
                    logs.append(parts)
            elif line.lower().startswith('@data'):
                start_reading = True
    return logs

def run_simulation():
    logs = load_test_logs()
    if not logs:
        return

    print(f"🚀 Loaded {len(logs)} test cases. Starting stream...")

    while True:
        raw_log = random.choice(logs)
        
        
        log_dict = dict(zip(COLUMNS, raw_log))
        
        # Data Type Casting for the Engine
        try:
            for key in ["duration", "src_bytes", "dst_bytes", "count", "srv_count"]:
                if key in log_dict:
                    log_dict[key] = int(float(log_dict[key])) # float first to handle '0.0'

            # Send to FastAPI
            response = requests.post(API_URL, json=log_dict, timeout=5)
            
            if response.status_code == 200:
                res_data = response.json()
                print(f"✅ [{log_dict.get('protocol_type')}] {log_dict.get('service')} -> Threat: {res_data.get('threat_rating')} | Label: {log_dict.get('label')}")
            else:
                print(f"❌ Server Error: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Stream Error: {e}")

        time.sleep(1) # Speed of the dashboard updates

if __name__ == "__main__":
    run_simulation()
