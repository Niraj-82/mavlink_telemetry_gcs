import asyncio
import threading
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mavlink_listener import start_mavlink_listener, get_latest_state

app = FastAPI(title="Cloud GCS (MAVLink) Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

telemetry_history: List[Dict[str, Any]] = []
MAX_HISTORY = 1000

alert_config = {
    "battery_low_threshold": 20,
    "altitude_max": 100,
    "speed_max": 20,
    "enabled": True
}

active_alerts = []


def check_alerts(state: Dict[str, Any]):
    if not alert_config["enabled"]:
        return

    alerts = []

    if state.get("battery_percent", 100) < alert_config["battery_low_threshold"]:
        alerts.append({
            "type": "BATTERY_LOW",
            "severity": "HIGH",
            "message": f"Battery at {state['battery_percent']}%",
            "timestamp": datetime.now().isoformat()
        })

    if state.get("altitude_m", 0) > alert_config["altitude_max"]:
        alerts.append({
            "type": "ALTITUDE_EXCEEDED",
            "severity": "MEDIUM",
            "message": f"Altitude {state['altitude_m']:.1f}m exceeds limit",
            "timestamp": datetime.now().isoformat()
        })

    if state.get("ground_speed_ms", 0) > alert_config["speed_max"]:
        alerts.append({
            "type": "SPEED_EXCEEDED",
            "severity": "LOW",
            "message": f"Speed {state['ground_speed_ms']:.1f}m/s exceeds limit",
            "timestamp": datetime.now().isoformat()
        })

    if alerts:
        active_alerts.extend(alerts)
        if len(active_alerts) > 50:
            del active_alerts[:-50]


@app.on_event("startup")
def startup_event():
    listener_thread = threading.Thread(target=start_mavlink_listener, daemon=True)
    listener_thread.start()


@app.get("/")
async def root():
    return {
        "service": "Cloud GCS MAVLink Backend",
        "version": "1.0.0",
        "endpoints": {
            "telemetry": "/api/telemetry",
            "history": "/api/telemetry/history",
            "alerts": "/api/alerts",
            "websocket": "/ws/telemetry"
        }
    }


@app.get("/api/telemetry")
async def get_telemetry():
    state = get_latest_state()
    return JSONResponse(state)


@app.get("/api/telemetry/history")
async def get_telemetry_history(limit: int = 100):
    return JSONResponse({
        "count": len(telemetry_history),
        "data": telemetry_history[-limit:]
    })


@app.get("/api/alerts")
async def get_alerts():
    return JSONResponse({
        "config": alert_config,
        "active_alerts": active_alerts[-20:]
    })


@app.post("/api/alerts/config")
async def update_alert_config(config: dict):
    alert_config.update(config)
    return JSONResponse({
        "status": "success",
        "config": alert_config
    })


@app.post("/api/alerts/clear")
async def clear_alerts():
    active_alerts.clear()
    return JSONResponse({"status": "success", "message": "Alerts cleared"})


@app.get("/api/stats")
async def get_stats():
    if not telemetry_history:
        return JSONResponse({
            "message": "No flight data available"
        })

    altitudes = [t.get("altitude_m", 0) for t in telemetry_history]
    speeds = [t.get("ground_speed_ms", 0) for t in telemetry_history]

    return JSONResponse({
        "flight_duration_seconds": len(telemetry_history) * 0.2,
        "max_altitude": max(altitudes) if altitudes else 0,
        "avg_altitude": sum(altitudes) / len(altitudes) if altitudes else 0,
        "max_speed": max(speeds) if speeds else 0,
        "avg_speed": sum(speeds) / len(speeds) if speeds else 0,
        "data_points": len(telemetry_history)
    })


@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            state = get_latest_state()

            telemetry_history.append(dict(state))
            if len(telemetry_history) > MAX_HISTORY:
                telemetry_history.pop(0)

            check_alerts(state)

            await websocket.send_json({
                "telemetry": state,
                "alerts": active_alerts[-5:] if active_alerts else []
            })

            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
