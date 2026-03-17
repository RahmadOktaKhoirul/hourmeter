import time
from core.gpio_reader import is_hm_on
from core.hm_counter import HourMeter
from core.storage import load_state, save_state, save_session
from core.button_reset import init_button, is_reset_pressed

# ==========================
# OLED INIT (SAFE MODE)
# ==========================
try:
    from oled_display import OLEDDisplay
    oled = OLEDDisplay()
    oled.boot_sequence()
    oled_enabled = True
except Exception as e:
    print("OLED NOT AVAILABLE:", e)
    oled_enabled = False

# ==========================
# CONFIG
# ==========================
CAL_FACTOR = 1.0023

print("=== Hour Meter Service Started ===")

# ==========================
# LOAD STATE
# ==========================
state = load_state()

hm = HourMeter(
    total_seconds=state["total_seconds"],
    factor=CAL_FACTOR
)

raw = state["raw"]
events = state["events"]

init_button()

last_display = 0
_session_on_ts = None      # timestamp saat HM mulai ON
_session_on_hm = 0.0       # nilai HM saat mulai ON
_prev_hm_on = False        # state HM sebelumnya

# ==========================
# MAIN LOOP
# ==========================
while True:

    # ===== RESET =====
    if is_reset_pressed():
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

        before = hm.total_seconds
        bh = int(before // 3600)
        bm = int((before % 3600) // 60)
        bs = int(before % 60)

        # Tutup sesi ON yang sedang berjalan sebelum reset
        if _session_on_ts is not None:
            dur = round(before - _session_on_hm, 2)
            dur_h = int(dur // 3600)
            dur_m = int((dur % 3600) // 60)
            dur_s = int(dur % 60)
            save_session({
                "type": "ON_SESSION",
                "on_ts": _session_on_ts,
                "off_ts": ts,
                "hm_on": round(_session_on_hm, 2),
                "hm_off": round(before, 2),
                "duration_seconds": dur,
                "duration_hms": f"{dur_h:02}:{dur_m:02}:{dur_s:02}",
                "closed_by": "RESET"
            })
            _session_on_ts = None

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
        print(f"!!! HM RESET at {ts}")

    # ===== NORMAL OPERATION =====
    hm_on = is_hm_on()
    hm.tick(hm_on)

    # ===== TRACKING SESI ON/OFF =====
    if hm_on and not _prev_hm_on:
        # Transisi OFF -> ON: catat waktu & nilai HM mulai
        _session_on_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        _session_on_hm = hm.total_seconds
        print(f">>> HM ON at {_session_on_ts} (HM={_session_on_hm:.2f}s)")

    elif not hm_on and _prev_hm_on:
        # Transisi ON -> OFF: simpan sesi
        off_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        dur = round(hm.total_seconds - _session_on_hm, 2)
        dur_h = int(dur // 3600)
        dur_m = int((dur % 3600) // 60)
        dur_s = int(dur % 60)
        save_session({
            "type": "ON_SESSION",
            "on_ts": _session_on_ts,
            "off_ts": off_ts,
            "hm_on": round(_session_on_hm, 2),
            "hm_off": round(hm.total_seconds, 2),
            "duration_seconds": dur,
            "duration_hms": f"{dur_h:02}:{dur_m:02}:{dur_s:02}",
            "closed_by": "OFF"
        })
        _session_on_ts = None
        print(f">>> HM OFF at {off_ts} | durasi={dur_h:02}:{dur_m:02}:{dur_s:02}")

    _prev_hm_on = hm_on

    h = int(hm.total_seconds // 3600)
    m = int((hm.total_seconds % 3600) // 60)
    s = int(hm.total_seconds % 60)

    raw.append({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": "ON" if hm_on else "OFF",
        "hms": f"{h:02}:{m:02}:{s:02}",
        "hm": f"{h}.{m:02}",
        "total_seconds": round(hm.total_seconds, 2)
    })

    save_state(hm.total_seconds, raw, events)

    print(
        f"[{time.strftime('%F %T')}] "
        f"HM={'ON' if hm_on else 'OFF'} "
        f"TOTAL={h:02}:{m:02}:{s:02}"
    )

    # ===== OLED UPDATE =====
    if oled_enabled and time.time() - last_display > 0.2:
        try:
            oled.update(
                f"{h}.{m:02}",
                f"{h:02}:{m:02}:{s:02}",
                hm_on
            )
        except Exception as e:
            print("OLED ERROR:", e)
            oled_enabled = False

        last_display = time.time()

    time.sleep(0.2)
