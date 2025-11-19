# Cloud GCS – MAVLink Telemetry Dashboard

This project implements a **cloud-based Ground Control Station (GCS)** that receives and visualises **MAVLink telemetry** and streams it in real time to a **web dashboard**.

It is designed to match the assignment requirements:

- Uses **MAVLink protocol** for telemetry (via `pymavlink`)
- Backend in **Python (FastAPI)** with **WebSocket** for real-time streaming
- Frontend web dashboard using **HTML, CSS, JavaScript**, **Tailwind**, **Leaflet** (map) and **Chart.js** (charts)
- Simulated MAVLink telemetry via a **Python simulator** or real SITL
- Architecture ready for **4G/LTE + VPN (ZeroTier)** remote connectivity

---

## 1. Architecture Overview

**Core idea:**

1. A **MAVLink source** (ArduPilot SITL, real flight controller, or the included `simulator.py`) sends telemetry via **UDP** to the backend.
2. The **backend** (`FastAPI`) listens for MAVLink messages, decodes them with `pymavlink`, and maintains a shared in-memory telemetry snapshot.
3. The backend exposes:
   - `GET /api/telemetry` – latest telemetry as JSON (REST)
   - `WS /ws/telemetry` – real-time telemetry stream via WebSocket
4. The **frontend dashboard** is a static web app (`frontend/index.html`) that connects via WebSocket, receives telemetry, and renders:
   - Map view with current drone position + path (Leaflet)
   - Charts (altitude vs time, ground speed vs time) using Chart.js
   - Status cards (mode, battery, speed, altitude)
5. For **remote connectivity** over 4G/LTE behind NAT, the MAVLink UDP stream can be forwarded over a **VPN/virtual network** (e.g., ZeroTier) from the field node to the cloud backend, similar to **UAVcast‑Pro**.

> Telemetry flow: **MAVLink (UDP)** → **FastAPI + pymavlink** → **WebSocket** → **Browser dashboard**.

---

## 2. Tech Stack Used (Aligned with Your Skills)

- **Languages**: Python, JavaScript, HTML, CSS
- **Backend / API**:
  - FastAPI
  - WebSocket streaming
- **Frontend / Web**:
  - HTML, CSS, JavaScript
  - Tailwind CSS (CDN)
  - Leaflet (Map visualization)
  - Chart.js (Telemetry charts)
- **Data / Parsing**:
  - MAVLink decoding via `pymavlink`
- **Tools**:
  - Git & GitHub (for version control)
  - Postman / browser for testing endpoints

You can further extend this with a real database (MySQL/PostgreSQL) or React/Next.js if needed, but this version is kept simple and assignment-focused.

---

## 3. Project Structure

```text
gcs-mavlink/
├── backend/
│   ├── app.py              # FastAPI backend + WebSocket
│   ├── mavlink_listener.py # MAVLink UDP listener using pymavlink
│   ├── simulator.py        # (Optional) MAVLink telemetry simulator
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── index.html          # Dashboard UI
    └── static/
        ├── css/
        │   └── styles.css  # Extra styling
        └── js/
            └── app.js      # WebSocket, map, charts logic
```

---

## 4. Backend Setup (FastAPI + MAVLink)

### 4.1. Create and activate a virtual env (recommended)

```bash
cd backend

# Example with venv
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 4.2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `fastapi`
- `uvicorn[standard]`
- `pymavlink`

### 4.3. Start the backend server

```bash
uvicorn app:app --reload
```

- API & WebSocket base URL: `http://localhost:8000`
- Telemetry REST endpoint: `http://localhost:8000/api/telemetry`
- WebSocket endpoint: `ws://localhost:8000/ws/telemetry`

On startup, the backend will also start the **MAVLink listener** (by default on `udp:0.0.0.0:14550`).

---

## 5. MAVLink Telemetry Source

You have two options:

### 5.1. Use ArduPilot SITL (realistic)

- Run SITL and configure it to output MAVLink to `udp:127.0.0.1:14550` or forward to your backend host.
- This simulates a full autopilot stack with real MAVLink messages.

### 5.2. Use the included simulator (quick demo)

The `backend/simulator.py` script sends basic MAVLink messages (heartbeat, sys_status, global_position_int, vfr_hud) to `udpout:127.0.0.1:14550`.

In a second terminal (with venv activated and backend running):

```bash
cd backend
python simulator.py
```

You should see logs like:

```text
[SIM] Sending simulated MAVLink telemetry to udpout:127.0.0.1:14550
```

The backend logs will show it connecting and parsing MAVLink messages.

---

## 6. Frontend Dashboard

The frontend is a simple static HTML/JS app that uses your **HTML/CSS/JS + Tailwind + Chart.js + Leaflet** skills.

### 6.1. Open the dashboard

For local testing, you can simply open the HTML file in your browser:

```text
gcs-mavlink/frontend/index.html
```

- Make sure the backend is running on `http://localhost:8000`.
- The page will connect to `ws://localhost:8000/ws/telemetry`.
- You should see:
  - **Connection status** (Connected / Disconnected)
  - **Map** with drone marker and trail path
  - **Cards** showing battery, mode, speed, altitude
  - **Charts** updating in real time

If you want, you can also serve `frontend/` via a simple HTTP server (e.g., `python -m http.server`), but it’s not mandatory for the demo.

---

## 7. 4G/LTE + VPN (ZeroTier) – Network Layer Design

This project is designed to match the networking approach of tools like **UAVcast‑Pro**:

1. **Field node (on the drone side)**:
   - Raspberry Pi / companion computer / laptop
   - Connects to the internet via **4G/LTE modem** or **WiFi hotspot**
   - Runs MAVLink forwarder (or directly outputs SITL telemetry)
2. **VPN / virtual network (ZeroTier)**:
   - Create a ZeroTier network and join:
     - Field node
     - Cloud GCS backend server
   - Both nodes obtain stable virtual IPs (e.g., `10.147.x.x`)
   - MAVLink UDP stream is sent from field node → `CLOUD_ZT_IP:14550`
   - This **bypasses carrier-grade NAT and firewalls**, similar to UAVcast‑Pro
3. **Cloud GCS backend**:
   - Same `app.py` + `mavlink_listener.py` code, now listening on the ZeroTier interface.
   - No code changes are needed; only the `connection_string` in `start_mavlink_listener()` may need to be adjusted if you change ports.

This demonstrates your understanding of **remote telemetry feeds over mobile networks + VPN/virtual network** as requested in the assignment.

---

## 8. Low-Latency Streaming (AirCast Inspiration)

AirCast uses ultra-low-latency video + telemetry (WebRTC / BLAST) over 4G/LTE.

In this implementation:

- **Telemetry** is streamed via **WebSocket**, which is already low-latency and efficient enough for real-time UI updates.
- You can extend this by adding a **WebRTC video panel**:
  - Field node captures video (webcam / camera / RTSP)
  - Sends to the cloud/frontend using WebRTC (with a small signaling server in FastAPI)
  - Frontend displays it in a `<video>` element

The current code focuses on demonstrating **real-time telemetry streaming** clearly, which is the core part of the assignment, and documents how video streaming would integrate into the same architecture.

---

## 9. How This Matches the Assignment

- ✅ **MAVLink protocol** used via `pymavlink` (both for listener and optional simulator)
- ✅ **Simulated telemetry data flow** (altitude, speed, GPS, battery, mode) using MAVLink message sets
- ✅ **Frontend dashboard**:
  - Real-time updates via WebSocket
  - Charts, status panels, map view
- ✅ **Network/streaming technologies**:
  - Telemetry over UDP → WebSocket
  - Design ready for 4G/LTE + ZeroTier VPN to traverse NAT/firewalls
  - Discussion & extension path for low-latency video (AirCast-style)
- ✅ **Clean code + documentation** (Python + JS, separated frontend/backend, README with setup & architecture)

---

## 10. Demo Flow (for 1–2 Minute Video)

You can use this as your video script outline:

1. **Intro** (10–15s)
   - “This is my cloud-based GCS built with Python FastAPI and a web dashboard. It receives MAVLink telemetry and visualises it in real time.”
2. **Backend & MAVLink** (20–30s)
   - Show terminal running `uvicorn app:app --reload`
   - Show telemetries being received (via logs or Postman hitting `/api/telemetry`)
   - (Optional) Show `simulator.py` sending MAVLink messages
3. **Dashboard** (40–60s)
   - Show `index.html`
   - Point at:
     - Connection status changing to “Connected”
     - Map marker moving and path trail
     - Altitude/speed charts updating
     - Battery and mode changing
4. **Networking explanation** (10–15s)
   - Briefly mention: “In a real deployment, the same UDP MAVLink stream would be forwarded over 4G/LTE and ZeroTier, similar to UAVcast‑Pro, and we can add WebRTC video streaming inspired by AirCast for low-latency video.”

This covers both **implementation** and **architecture understanding**, as required by the assignment.
