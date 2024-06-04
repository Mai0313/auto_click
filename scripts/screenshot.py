from adbutils import adb
from pydantic import BaseModel
import autorootcwd
from src.types.simulator import SimulatorSettings
from src.utils.config_utils import load_config


class Scripts(BaseModel):
    settings: SimulatorSettings

    def screenshots(self) -> None:
        serial = f"127.0.0.1:{self.settings.adb_port}"
        adb.connect(serial)
        d = adb.device(serial=serial)
        running_app = d.app_current()
        if running_app.package != "com.longe.allstarhmt":
            d.app_start("com.longe.allstarhmt")
        current_screent = d.screenshot()
        current_screent.save("./data/allstars_test/debug.png")


if __name__ == "__main__":
    settings = load_config("./configs/simulator.yaml")
    scripts = Scripts(settings=settings)
    scripts.screenshots()
