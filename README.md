🛡️ AI67: Air-Gapped SOC Intelligence (v2.5)

AI67 is a high-performance, real-time cyber threat detection platform
designed for zero-trust environments. By combining unsupervised machine learning
(Isolation Forest) with mathematical forensic explainability (SHAP), AI67
identifies and interprets network anomalies without ever sending data to the
cloud.

Python FastAPI Scikit-Learn Security

🚀 Core Capabilities

  - Unsupervised Anomaly Detection: Utilizes an Isolation Forest trained on the
    NSL-KDD dataset (125,000+ samples) to detect "unseen" attack vectors.
  - Forensic Explainability (SHAP): On-demand SHAP (Shapley Additive
    Explanations) integration translates complex ML weights into human-readable
    triage notes.
  - Real-Time SOC Matrix: A low-latency dashboard powered by WebSockets,
    featuring a master-detail "squish" layout for rapid incident response.
  - Local-First Architecture: 100% air-gapped. No external API calls
    (OpenAI/Anthropic) are required for detection or explanation.
  - Adversarial Simulation: Includes a high-fidelity simulator that streams
    real-world test cases from the KDDTest+ dataset.

🏗️ Technical Architecture

The Pipeline

1.  Ingestion: Raw network telemetry (JSON) is posted to the /api/v1/ingest
    endpoint.
2.  Preprocessing: A stateless ColumnTransformer scales numerical data and
    one-hot encodes categorical features (Protocol, Service, Flags).
3.  Inference: The Isolation Forest calculates a decision score.
4.  Broadcast: The event, threat rating (0-5), and metadata are pushed to the
    frontend via WebSockets.
5.  Triage: Upon selection, the backend invokes the SHAP TreeExplainer to
    provide a forensic breakdown of the anomaly drivers.

Tech Stack

  - Backend: FastAPI (Asynchronous Gateway), Scikit-Learn (ML Core), SHAP
    (Explainability).
  - Frontend: Tailwind CSS (UI), Lucide (Icons), Vanilla JS (WebSocket
    Management).
  - Data Handling: Pandas, Joblib, SciPy (ARFF Parsing).

📦 Installation & Setup

1. Clone & Environment

git clone https://github.com/your-repo/ai-shield.git
cd ai-shield
pip install -r requirements.txt

2. Data Preparation

Download the NSL-KDD dataset and place the .arff files in the data/ directory.

  - data/KDDTrain+.arff
  - data/KDDTest+.arff

3. Training the Engine

Train the model locally on the 125k sample dataset:

python3 scripts/train.py

This generates artifacts/model.pkl and artifacts/preprocessor.pkl.

🚦 Quick Start

1.  Launch the Gateway:

    python3 main.py

2.  Access the Dashboard: Navigate to http://localhost:8000. Ensure the "Live
    Socket Bound" indicator is active.

3.  Stream Test Data: In a separate terminal, start the adversarial simulator:

    python3 scripts/generate_test.py

🖥️ Dashboard Features

Master-Detail View

Clicking any log in the scrollable stream "squishes" the list to reveal a
Forensic Analysis panel. This panel displays:

  - Identity Matrix: Service, Protocol, and Connection Flags.
  - SHAP Analysis: Natural language explanation of why the AI flagged the
    traffic (e.g., "Suspicious surge in source bytes detected").
  - Response Protocol: V2 placeholder for active defense actions (Ban IP,
    Quarantine, etc.).

Multi-Level Filtering

The client-side filter allows analysts to toggle visibility for specific threat
levels (0-5) without interrupting the background ingestion stream.

📊 Threat Gradient Scale

| Level    | Classification      | Description                                                               |
| :------- | :------------------ | :------------------------------------------------------------------------ |
| **L0-1** | **Safe / Info**     | Standard baseline traffic; matches historical patterns.                   |
| **L2-3** | **Warn / Alert**    | Minor behavioral drift; potential probe or misconfiguration.              |
| **L4-5** | **High / Critical** | Significant structural anomaly; consistent with DoS, R2L, or U2R attacks. |

🗺️ Roadmap

  - v2.5 (Current): SHAP Explainability & SOC UI Refinement.
  - v2.7: Active Response Hooks (Local iptables integration for automated
    banning).
  - v3.0: Local LLM Triage (Ollama integration for generating full incident
    reports).
  - v3.5: Federated Learning (Privacy-preserving model updates across multiple
    nodes).

🛡️ Security Disclaimer

AI67 is a forensic tool designed for authorized security monitoring. Ensure
compliance with local privacy laws and organizational policies regarding network
traffic inspection.
