import time
from core.gpio_reader import is_hm_on
from core.hm_counter import HourMeter
from core.storage import load_state, save_state
from core.button_reset import init_button, is_reset_pressed

CAL_FACTOR = 1.019  # hasil kalibrasi lapangan kamu

print("=== Hour Meter Service Started ===")

state = load_state()

hm = HourMeter(
    total_seconds=state["total_seconds"],
    factor=CAL_FACTOR
)

raw = state["raw"]
events = state["events"]

init_button()

while True:
    # ===== RESET =====
    if is_reset_pressed():
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

        before = hm.total_seconds
        bh = int(before // 3600)
        bm = int((before % 3600) // 60)
        bs = int(before % 60)

        events.append({
            "type": "RESET",
            "timestamp": ts,
            "before": {
                "total_seconds": round(before, 2),
                "hms": f"{bh:02}:{bm:02}:{bs:02}",
                "hm": f"{bh}.{bm:02}"
            },
            "after": {
                "total_seconds": 0,
                "hms": "00:00:00",
                "hm": "0.00"
            },
            "source": "GPIO"
        })

        hm.total_seconds = 0

        print(
            f"!!! HM RESET at {ts} | "
            f"BEFORE={bh:02}:{bm:02}:{bs:02} ({bh}.{bm:02})"
        )

    # ===== NORMAL OPERATION =====
    hm_on = is_hm_on()
    hm.tick(hm_on)

    h = int(hm.total_seconds // 3600)
    m = int((hm.total_seconds % 3600) // 60)
    s = int(hm.total_seconds % 60)

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

    time.sleep(0.2)  # loop cepat, waktu tidak tergantung ini
