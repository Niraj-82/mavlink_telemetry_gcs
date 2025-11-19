Cloud GCS – MAVLink Telemetry Dashboard

A cloud-based Ground Control Station (GCS) built using Python FastAPI, WebSockets, and a modern HTML/JS dashboard.
It receives real-time MAVLink telemetry (simulated or from SITL), processes it on the backend, and visualizes live drone data on a clean web interface with a map, charts, and status panels.

This project is designed exactly according to the assignment requirements and shows your understanding of MAVLink, real-time communication, remote connectivity, and full-stack integration.

🚀 What This Project Does

This system acts as a mini Cloud GCS:

Reads MAVLink telemetry (altitude, speed, GPS, battery, etc.)

Processes it using a Python FastAPI backend

Streams real-time updates to the browser using WebSockets

Displays:

Live map (Leaflet)

Altitude & speed charts (Chart.js)

System status cards (mode, battery, link health)

Raw telemetry JSON

You can run it locally or integrate it with real drone telemetry via 4G/LTE + VPN (ZeroTier).

🧠 Why This Matters (Humanized Explanation)

A drone sends constant telemetry while flying—its position, altitude, battery, and dozens of other parameters.
Real GCS tools like Mission Planner, UAVcast-Pro, and AirCast handle this using:

MAVLink protocol

Low-latency networking

Real-time dashboards

I built a simplified cloud version of such a system.

Think of it as:

A lightweight Mission Planner that runs in the browser, powered by Python and WebSockets.

🏗️ Tech Stack Used

This project intentionally uses technologies I'm already comfortable with:

Backend

Python

FastAPI

WebSockets

pymavlink

Frontend

HTML, CSS, JavaScript

Tailwind CSS

Leaflet.js (map)

Chart.js (live charts)

Other

MAVLink simulator

ZeroTier-ready architecture for 4G/LTE remote streaming

Good documentation, clean structure, and demo video-friendly output

📐 Architecture (Simple Overview)
[MAVLink Source: SITL / Drone / Simulator]
                |
          (UDP + MAVLink)
                |
        [FastAPI Backend]
     - Parses MAVLink packets
     - Maintains latest telemetry
     - Broadcasts updates via WebSocket
                |
        (WebSocket + JSON)
                |
        [Web Dashboard UI]
     - Map with live marker
     - Altitude/speed charts
     - Status cards


Telemetry flow:
MAVLink → Backend (UDP) → WebSocket → Browser UI

📦 Project Structure
gcs-mavlink/
├── backend/
│   ├── app.py               # FastAPI app + WebSocket endpoint
│   ├── mavlink_listener.py  # MAVLink listener (UDP)
│   ├── simulator.py         # Optional MAVLink simulator
│   └── requirements.txt
└── frontend/
    ├── index.html
    └── static/
        ├── css/styles.css
        └── js/app.js

🛠️ How to Run the Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload


Backend runs at:

API → http://localhost:8000/api/telemetry

WebSocket → ws://localhost:8000/ws/telemetry

🛰️ Simulated MAVLink Telemetry (for easy demo)

In another terminal:

cd backend
python simulator.py


This generates moving GPS coordinates, changing altitude, battery drain, etc.

🌐 Frontend Dashboard

Just open:

frontend/index.html


You’ll see:

A live map with a moving marker

Altitude & speed charts updating in real time

Status cards

Raw telemetry JSON

🌍 4G/LTE + ZeroTier (UAVcast-Pro style)

To make this a true cloud GCS, telemetry can be forwarded from a drone using:

A field computer (Pi/laptop) connected via 4G/LTE hotspot

A ZeroTier virtual network to bypass NAT/firewalls

MAVLink forwarded to the cloud server’s ZeroTier IP

This mirrors real UAVcast-Pro functionality.
