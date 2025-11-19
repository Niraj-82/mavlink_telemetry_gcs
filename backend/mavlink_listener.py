import time
from typing import Dict, Any

try:
    from pymavlink import mavutil
except ImportError:
    mavutil = None

_latest_state: Dict[str, Any] = {
    "timestamp": time.time(),
    "lat": 19.0760,
    "lon": 72.8777,
    "altitude_m": 0.0,
    "ground_speed_ms": 0.0,
    "heading_deg": 0.0,
    "battery_percent": 100,
    "mode": "STANDBY",
    "system_status": "INIT",
    "link_status": "NO_DATA_YET",
}


def get_latest_state() -> Dict[str, Any]:
    return _latest_state


def _update_from_msg(msg):
    global _latest_state

    msg_type = msg.get_type()

    if msg_type == "GLOBAL_POSITION_INT":
        _latest_state["lat"] = msg.lat / 1e7
        _latest_state["lon"] = msg.lon / 1e7
        _latest_state["altitude_m"] = msg.relative_alt / 1000.0
        _latest_state["heading_deg"] = msg.hdg / 100.0

    elif msg_type == "VFR_HUD":
        _latest_state["ground_speed_ms"] = msg.groundspeed
        _latest_state["heading_deg"] = msg.heading

    elif msg_type == "SYS_STATUS":
        _latest_state["battery_percent"] = msg.battery_remaining

    elif msg_type == "HEARTBEAT":
        _latest_state["system_status"] = str(msg.system_status)
        _latest_state["mode"] = str(msg.custom_mode)

    _latest_state["timestamp"] = time.time()
    _latest_state["link_status"] = "OK"


def start_mavlink_listener(connection_string: str = "udp:0.0.0.0:14550"):
    global _latest_state

    if mavutil is None:
        print("[WARN] pymavlink not installed. Using static telemetry data only.")
        while True:
            _latest_state["timestamp"] = time.time()
            time.sleep(1.0)

    print(f"[INFO] Connecting to MAVLink source: {connection_string}")
    master = mavutil.mavlink_connection(connection_string)

    print("[INFO] Waiting for MAVLink heartbeat...")
    master.wait_heartbeat()
    print("[INFO] Heartbeat received. MAVLink link is up.")

    while True:
        try:
            msg = master.recv_match(blocking=True, timeout=5)
        except Exception as exc:
            print(f"[WARN] Error receiving MAVLink message: {exc}")
            continue

        if msg is None:
            continue

        try:
            _update_from_msg(msg)
        except Exception as exc:
            print(f"[WARN] Failed to parse MAVLink message {msg.get_type()}: {exc}")
