from adbutils import adb


def screenshots() -> None:
    adb.connect("127.0.0.1:16416")
    d = adb.device()
    running_app = d.app_current()
    if running_app.package != "com.longe.allstarhmt":
        d.app_start("com.longe.allstarhmt")
    current_screent = d.screenshot()
    current_screent.save("./data/allstars_test/get_rewards.png")


if __name__ == "__main__":
    screenshots()
