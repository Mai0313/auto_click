import time
from typing import Union, Optional
import getpass

from PIL import Image
import logfire
from adbutils import AdbDevice
from pydantic import Field, BaseModel
import pyautogui
from src.compare import ImageComparison
from src.get_screen import GetScreen
from playwright.sync_api import Page
from src.types.image_models import ConfigModel
from src.types.output_models import ShiftPosition
from src.utils.command_utils import CommandExecutor

logfire.configure(
    send_to_logfire=True,
    token="t5yWZMmjyRH5ZVqvJRwwHHfm5L3SgbRjtkk7chW3rjSp",
    project_name="auto-click",
    service_name=f"{getpass.getuser()}",
    trace_sample_rate=1.0,
    show_summary=True,
    data_dir=".logfire",
    collect_system_metrics=False,
    fast_shutdown=True,
    inspect_arguments=True,
    pydantic_plugin=logfire.PydanticPlugin(record="failure"),
)


class RemoteContoller(BaseModel):
    target: str = Field(
        ..., description="This field can be either a window title or a URL or cdp url."
    )
    configs: ConfigModel = Field(...)
    serial: Optional[str] = Field(default=None)

    def __init__(self, target: str, configs: ConfigModel):
        super().__init__(target=target, configs=configs)
        self.serial = f"127.0.0.1:{self.configs.adb_port}"
        try:
            # os.system(f".\\binaries\\adb.exe connect {self.serial}")
            commands = ["./binaries/adb.exe", "connect", self.serial]
            command_executor = CommandExecutor(commands=commands)
            command_executor.run()
        except Exception as e:
            logfire.error("Error in connecting to adb: {e}", e=e)

    def get_device(
        self,
    ) -> Union[tuple[bytes, Page], tuple[bytes, AdbDevice], tuple[Image.Image, ShiftPosition]]:
        if self.target.startswith("http"):
            return GetScreen.from_remote_window(self.target)
        elif self.target.startswith("com"):
            return GetScreen.from_adb_device(self.target, self.serial)
        else:
            # this will return screenshot, shift_position; not device.
            return GetScreen.from_exist_window(self.target)

    def click_button(
        self,
        device: Union[Page, AdbDevice, ShiftPosition],
        button_center_x: int,
        button_center_y: int,
    ) -> None:
        if isinstance(device, Page):
            device.mouse.click(x=button_center_x, y=button_center_y)
        elif isinstance(device, AdbDevice):
            device.click(x=button_center_x, y=button_center_y)
        else:
            pyautogui.moveTo(
                x=button_center_x + device.shift_x, y=button_center_y + device.shift_y
            )
            pyautogui.click()

    def main(self) -> None:
        while True:
            screenshot, device = self.get_device()
            for config_dict in self.configs.image_list:
                button_center_x, button_center_y = ImageComparison(
                    image_cfg=config_dict,
                    check_list=self.configs.base_check_list,
                    screenshot=screenshot,
                ).find()
                if button_center_x and button_center_y and self.configs.auto_click is True:
                    self.click_button(
                        device=device,
                        button_center_x=button_center_x,
                        button_center_y=button_center_y,
                    )
                    time.sleep(config_dict.delay_after_click)
            time.sleep(self.configs.global_interval)


if __name__ == "__main__":
    import sys

    from omegaconf import OmegaConf

    # target = "雀魂麻将"  # "http://localhost:9222"
    # config = OmegaConf.load("./configs/mahjong.yaml")
    # config_model = ConfigModel(**config)
    # check_list = [*config_model.base_check_list, *config_model.additional_check_list]
    # config_model.base_check_list = check_list

    args = sys.argv[1]
    target = "com.longe.allstarhmt"
    if args == "cn":
        configs = OmegaConf.load("./configs/games/all_stars_cn.yaml")
    else:
        configs = OmegaConf.load("./configs/games/all_stars.yaml")
    auto_web = RemoteContoller(target=target, configs=configs)
    auto_web.main()
