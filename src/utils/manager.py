from adbutils import adb
from pydantic import Field, BaseModel, model_validator
from adbutils.errors import AdbError


class AppInfo(BaseModel):
    serial: str = Field(..., description="The serial number of the device.")
    package: str = Field(..., description="The package name of the app.")


class ADBDeviceManager(BaseModel):
    host: str = Field(default="127.0.0.1")
    ports: list[str] = Field(
        ...,
        description="The list of ports to connect to; defaults to ['16384', '16416'], 16384 and 16416 are for MuMu Player, 5555 and 5557 are for LD Player.",
    )
    target: str = Field(default="com.longe.allstarhmt", description="The game you wanna afk.")

    serials: list[str] = Field(
        default=[], description="The list of serial numbers for connected devices."
    )
    running_apps: list[AppInfo] = Field(
        default=[], description="The list of running apps on the connected devices."
    )

    @model_validator(mode="after")
    def _setup_device(self) -> "ADBDeviceManager":
        """Retrieves a list of serial numbers for connected devices.

        Returns:
            A list of serial numbers for connected devices.
        """
        for port in self.ports:
            adb.connect(addr=f"{self.host}:{port}", timeout=3.0)

        for device in adb.device_list():
            if not device.serial.startswith("emulator"):
                self.serials.append(device.serial)

        for serial in self.serials:
            device = adb.device(serial=serial)
            running_app = device.app_current()
            running_details = AppInfo(serial=serial, package=running_app.package)
            self.running_apps.append(running_details)
        return self

    def get_correct_serial(self) -> AppInfo:
        """Retrieves the correct serial for the target application.

        This method filters the running applications to find those that match the target package.
        It returns the application if exactly one match is found. If no matches are found, it raises
        a ValueError indicating that no devices running the target app were found. If multiple matches
        are found, it raises a ValueError indicating that multiple devices running the target app were found.

        Returns:
            AppInfo: The application information of the target app.

        Raises:
            ValueError: If no devices or multiple devices running the target app are found.
        """
        apps = [app for app in self.running_apps if app.package == self.target]
        if len(apps) == 1:
            return apps[0]
        if len(apps) == 0:
            raise AdbError("No devices running the target app were found.")
        raise AdbError("Multiple devices running the target app were found.")


if __name__ == "__main__":
    target = "com.longe.allstarhmt"
    adb_manager = ADBDeviceManager(host="127.0.0.1", ports=["16384", "16416"], target=target)
    result = adb_manager.get_correct_serial()
