import math
import time

from pymavlink import mavutil


def main():
    master = mavutil.mavlink_connection("udpout:127.0.0.1:14550")

    print("[SIM] Sending simulated MAVLink telemetry to udpout:127.0.0.1:14550")

    start_time = time.time()
    radius_m = 50.0

    base_lat = 19.0760
    base_lon = 72.8777
    base_alt = 10.0

    while True:
        t = time.time() - start_time

        angle = t * 0.05
        dx = radius_m * math.cos(angle)
        dy = radius_m * math.sin(angle)

        dlat = dy / 111_320.0
        dlon = dx / (111_320.0 * math.cos(math.radians(base_lat)))

        lat = base_lat + dlat
        lon = base_lon + dlon
        alt = base_alt + 5 * math.sin(angle)

        groundspeed = 5 + 2 * math.sin(angle * 0.7)
        heading = (angle * 57.3) % 360

        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            0, 0, 0,
        )

        battery_remaining = 100 - int(t / 10) % 100
        master.mav.sys_status_send(
            0, 0, 0,
            0,
            0,
            0,
            battery_remaining,
            0,
            0,
            0, 0, 0, 0,
        )

        master.mav.global_position_int_send(
            int((time.time() - start_time) * 1000),
            int(lat * 1e7),
            int(lon * 1e7),
            int((alt + 50) * 1000),
            int(alt * 1000),
            0,
            0,
            int(groundspeed * 100),
            int(heading * 100),
        )

        master.mav.vfr_hud_send(
            groundspeed,
            groundspeed,
            int(heading),
            0,
            alt,
            0,
        )

        time.sleep(0.2)


if __name__ == "__main__":
    main()
