import time
import getpass

import yaml

# from hydra import compose, initialize
import logfire
from adbutils import AdbDevice, adb
from pydantic import computed_field
import pyautogui
from src.compare import ImageComparison
from src.get_screen import GetScreen
from src.types.config import ConfigModel
from playwright.sync_api import Page
from src.utils.get_serial import ADBDeviceManager
from src.types.output_models import DeviceOutput, ShiftPosition

logfire.configure(
    send_to_logfire=True,
    token="t5yWZMmjyRH5ZVqvJRwwHHfm5L3SgbRjtkk7chW3rjSp",  # noqa: S106
    project_name="auto-click",
    service_name=f"{getpass.getuser()}",
    trace_sample_rate=1.0,
    show_summary=True,
    data_dir=".logfire",
    fast_shutdown=True,
    inspect_arguments=True,
    pydantic_plugin=logfire.PydanticPlugin(record="failure"),
)


class RemoteContoller(ConfigModel):
    @computed_field
    @property
    def serial(self) -> str:
        apps = ADBDeviceManager(host="127.0.0.1", target=self.target).get_correct_serial()
        return apps.serial

    # def connect2adb(self) -> None:
    #     try:
    #         # os.system(f".\\binaries\\adb.exe connect {self.serial}")
    #         commands = ["./binaries/adb.exe", "connect", self.serial]
    #         command_executor = CommandExecutor(commands=commands)
    #         command_executor.run()
    #     except Exception as e:
    #         logfire.error("Error in connecting to adb", error=e)

    def connect2adb(self) -> None:
        adb.connect(addr=self.serial)
        device = adb.device(serial=self.serial)
        logfire.info("Connected to adb", serial=device.serial)
        running_app = device.app_current()
        logfire.info("Running App", **running_app.__dict__)

    def get_device(self) -> DeviceOutput:
        if self.target.startswith("http"):
            return GetScreen.from_remote_window(self.target)
        if self.target.startswith("com"):
            return GetScreen.from_adb_device(self.target, self.serial)
        # this will return screenshot, shift_position; not device.
        return GetScreen.from_exist_window(self.target)

    def click_button(
        self, device: Page | AdbDevice | ShiftPosition, button_center_x: int, button_center_y: int
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
        self.connect2adb()
        while True:
            try:
                device_details = self.get_device()
                for config_dict in self.image_list:
                    # logfire.info("Checking Image", **config_dict.model_dump())
                    button_center_x, button_center_y = ImageComparison(
                        image_cfg=config_dict, screenshot=device_details.screenshot
                    ).find()
                    if button_center_x and button_center_y and self.auto_click is True:
                        self.click_button(
                            device=device_details.device,
                            button_center_x=button_center_x,
                            button_center_y=button_center_y,
                        )
                        time.sleep(config_dict.delay_after_click)
            except Exception as e:
                logfire.error("Error in getting device:", error=e)
                logfire.info("Retrying...", retry_interval=self.random_interval)
                self.connect2adb()

def load_yaml(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as file:
        configs = yaml.safe_load(file)
    return configs


if __name__ == "__main__":
    config_path = "./configs/games/all_stars.yaml"
    configs = load_yaml(config_path=config_path)
    auto_web = RemoteContoller(**configs)
    auto_web.main()

    # configs = load_hydra_config()
    # game_config = configs["games"]
    # auto_web = RemoteContoller(**game_config)
    # auto_web.main()
