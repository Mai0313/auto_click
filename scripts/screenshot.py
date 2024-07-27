from adbutils import adb
from pydantic import BaseModel
from src.types.config import ConfigModel


class Scripts(BaseModel):
    configs: ConfigModel

    def screenshots(self) -> None:
        serial = f"127.0.0.1:{self.configs.adb_port}"
        adb.connect(serial)
        d = adb.device(serial=serial)
        running_app = d.app_current()
        if running_app.package != "com.longe.allstarhmt":
            d.app_start("com.longe.allstarhmt")
        current_screent = d.screenshot()
        current_screent.save("./data/allstars_test/debug.png")


if __name__ == "__main__":
    from omegaconf import OmegaConf

    configs = OmegaConf.load("./configs/all_stars_cn.yaml")
    scripts = Scripts(configs=configs)
    scripts.screenshots()
