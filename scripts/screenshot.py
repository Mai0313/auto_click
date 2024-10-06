from adbutils import adb
from pydantic import BaseModel


class Scripts(BaseModel):
    port: int

    def screenshots(self, output_path: str) -> None:
        serial = f"127.0.0.1:{self.port}"
        adb.connect(addr=serial)
        device = adb.device(serial=serial)
        # running_app = device.app_current()
        current_screent = device.screenshot()
        current_screent.save(output_path)


if __name__ == "__main__":
    port = 5557
    output_path = "./data/allstars_test/debug.png"

    scripts = Scripts(port=port)
    scripts.screenshots(output_path=output_path)
