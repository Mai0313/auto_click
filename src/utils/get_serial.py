from adbutils import adb
from pydantic import Field, BaseModel, computed_field


class AppInfo(BaseModel):
    serial: str
    package: str


class ADBDeviceManager(BaseModel):
    host: str = Field(default="127.0.0.1")
    target: str = Field(default="com.longe.allstarhmt", description="The game you wanna afk.")

    @computed_field
    @property
    def avaliable_devices(self) -> list[int]:
        mumu_player = [16384, 16416]
        # ld_player = [5555, 5557]
        avaliable_devices = [*mumu_player]
        return avaliable_devices

    @computed_field
    @property
    def serials(self) -> list[str]:
        for avaliable_device in self.avaliable_devices:
            adb.connect(addr=f"{self.host}:{avaliable_device}", timeout=3.0)
        devices = adb.device_list()
        serials = []
        for device in devices:
            if device.serial.startswith("emulator"):
                continue
            serials.append(device.serial)
        return serials

    @computed_field
    @property
    def running_apps(self) -> list[AppInfo]:
        running_apps = []
        for serial in self.serials:
            device = adb.device(serial=serial)
            running_app = device.app_current()
            running_details = AppInfo(**{"serial": serial, "package": running_app.package})
            running_apps.append(running_details)
        return running_apps

    def get_correct_serial(self) -> AppInfo:
        apps = [
            running_app for running_app in self.running_apps if running_app.package == self.target
        ]
        if len(apps) > 1 or len(apps) == 0:
            raise Exception("Multiple or no devices found")
        return apps[0]


if __name__ == "__main__":
    target = "com.longe.allstarhmt"
    apps = ADBDeviceManager(host="127.0.0.1", target=target).get_correct_serial()
