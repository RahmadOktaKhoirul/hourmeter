from datetime import datetime
from core.storage import send_command

def reset_hourmeter():
    send_command("hmreset")
    print(
        "HM reset requested at",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    reset_hourmeter()
