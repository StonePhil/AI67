from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from core.engine import ShieldEngine
import uvicorn

app = FastAPI()
engine = ShieldEngine()
connections = []

@app.get("/")
async def get():
    with open("index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)

@app.post("/api/v1/ingest")
async def ingest(log: dict):
    threat_level, status = engine.score(log)
    
    payload = {
        "event": log,
        "threat_rating": threat_level,
        "ai_analysis": f"Shield Engine detected {status} signature in {log.get('service', 'unknown')} traffic."
    }
    
    for connection in connections:
        await connection.send_json(payload)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
