import logfire
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
    def available_devices(self) -> list[int]:
        mumu_player = [16384, 16416]
        # ld_player = [5555, 5557]
        available_devices = [*mumu_player]
        return available_devices

    @computed_field
    @property
    def serials(self) -> list[str]:
        for available_device in self.available_devices:
            adb.connect(addr=f"{self.host}:{available_device}", timeout=3.0)
        devices = adb.device_list()
        serials = []
        for device in devices:
            if device.serial.startswith("emulator"):
                continue
            serials.append(device.serial)
        logfire.info("Available devices", serials=serials)
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
        logfire.info("Running apps", running_apps=running_apps)
        return running_apps

    def get_correct_serial(self) -> AppInfo:
        apps = [r_app for r_app in self.running_apps if r_app.package == self.target]
        if len(apps) > 1 or len(apps) == 0:
            raise Exception("Multiple or no devices found")
        app = next(iter(apps))
        logfire.info("Correct device found", serial=app.serial, package=app.package)
        return app


if __name__ == "__main__":
    target = "com.longe.allstarhmt"
    apps = ADBDeviceManager(host="127.0.0.1", target=target).get_correct_serial()
