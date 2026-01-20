import time
from core.gpio_reader import is_hm_on
from core.hm_counter import HourMeter
from core.storage import load_state, save_state, check_command

print("=== Hour Meter Service Started ===")

state = load_state()
hm = HourMeter(state.get("total_seconds", 0))
raw = state.get("raw", [])
events = state.get("events", [])

while True:
    # ===== cek perintah =====
    cmd = check_command()
    if cmd == "hmreset":
        h = hm.total_seconds // 3600
        m = (hm.total_seconds % 3600) // 60
        s = hm.total_seconds % 60

        events.append({
            "type": "RESET",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "before_hms": f"{h:02}:{m:02}:{s:02}",
            "before_hm": f"{h}.{m:02}"
        })

        hm.total_seconds = 0
        hm.run_seconds = 0

        print("!!! HM RESET EXECUTED !!!")

    # ===== normal HM logic =====
    hm_on = is_hm_on()
    hm.tick(hm_on)

    h = hm.total_seconds // 3600
    m = (hm.total_seconds % 3600) // 60
    s = hm.total_seconds % 60

    raw.append({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": "ON" if hm_on else "OFF",
        "hms": f"{h:02}:{m:02}:{s:02}",
        "hm": f"{h}.{m:02}"
    })

    save_state(hm.total_seconds, raw, events)

    print(
        f"[{time.strftime('%F %T')}] "
        f"HM={'ON' if hm_on else 'OFF'} "
        f"TOTAL={h:02}:{m:02}:{s:02} "
        f"HM_DISPLAY={h}.{m:02}"
    )

    time.sleep(1)
