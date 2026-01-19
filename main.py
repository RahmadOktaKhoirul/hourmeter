import time
from core.gpio_reader import is_hm_on
from core.hm_counter import HourMeter
from core.storage import load_state, save_state

state = load_state()
hm = HourMeter(state["total_seconds"])
raw = state.get("raw", [])

while True:
    on = is_hm_on()
    hm.tick(on)

    raw.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hm": on
    })

    save_state(hm.total_seconds, raw)
    print(f"HM={'ON' if on else 'OFF'} TOTAL={hm.total_seconds}s")

    time.sleep(1)
