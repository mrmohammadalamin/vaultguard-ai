from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from database.models import init_db, SessionLocal, AuditLog
from engine.state_machine import StateMachine

app = FastAPI(title="VaultGuard AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

# Global state machine instance for simulation
sm = StateMachine(manager.broadcast)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Sync current state machine state on new connection
    state = sm.states[sm.current_state_idx] if sm.current_state_idx < len(sm.states) else "COMPLETE"
    if not sm.running and sm.current_state_idx == 0:
        state = "IDLE"
    progress = int((sm.current_state_idx / (len(sm.states) - 1)) * 100) if sm.current_state_idx < len(sm.states) else 100
    
    await websocket.send_text(json.dumps({
        "type": "state_update",
        "data": {"state": state, "progress": progress}
    }))
    
    # Sync historical logs
    for log in sm.logs:
        await websocket.send_text(json.dumps({
            "type": "log",
            "data": log
        }))
        
    # Sync pending approval if paused
    if sm.is_paused and sm.pending_approval:
        decision = sm.governance.inspect_and_decide(sm.pending_approval)
        await websocket.send_text(json.dumps({
            "type": "approval_required",
            "data": {
                "action": sm.pending_approval,
                "risk": decision.risk_level.value,
                "reason": decision.reason
            }
        }))

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("action") == "start_goal":
                await sm.start()
            elif payload.get("action") == "approve":
                await sm.approve()
            elif payload.get("action") == "reject":
                await sm.reject()

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/audit")
def get_audit_logs():
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).all()
        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "goal": log.goal,
                "agent": log.agent,
                "action": log.action,
                "policy_decision": log.policy_decision,
                "approval_event": log.approval_event,
                "retry_count": log.retry_count,
                "execution_time_ms": log.execution_time_ms,
                "final_status": log.final_status
            }
            for log in logs
        ]
    finally:
        db.close()
