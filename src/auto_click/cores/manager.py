from adbutils import adb
from pydantic import Field, BaseModel, model_validator
from adbutils.errors import AdbError

from auto_click.cores.config import DeviceModel


class AppInfo(BaseModel):
    serial: str = Field(..., description="The serial number of the device.")
    package: str = Field(..., description="The package name of the app.")


class ADBDeviceManager(DeviceModel):
    running_apps: list[AppInfo] = Field(
        default=[], description="The list of running apps on the connected devices."
    )

    @model_validator(mode="after")
    def _setup_device(self) -> "ADBDeviceManager":
        adb.connect(addr=f"{self.host}:{self.serial}", timeout=3.0)

        serial_list = []
        for device in adb.device_list():
            if not device.serial.startswith("emulator"):
                serial_list.append(device.serial)

        for serial in serial_list:
            device = adb.device(serial=serial)
            running_app = device.app_current()
            running_details = AppInfo(serial=serial, package=running_app.package)
            self.running_apps.append(running_details)
        return self

    def get_correct_serial(self) -> AppInfo:
        apps = [app for app in self.running_apps if app.package == self.target]
        if len(apps) == 1:
            return apps[0]
        if len(apps) == 0:
            raise AdbError("No devices running the target app were found.")
        raise AdbError("Multiple devices running the target app were found.")


if __name__ == "__main__":
    target = "com.longe.allstarhmt"
    adb_manager = ADBDeviceManager(host="127.0.0.1", serial="16416", target=target)
    result = adb_manager.get_correct_serial()
