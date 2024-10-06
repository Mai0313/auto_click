from adbutils import adb
from pydantic import Field, BaseModel, computed_field


class AppInfo(BaseModel):
    serial: str = Field(..., description="The serial number of the device.")
    package: str = Field(..., description="The package name of the app.")


class ADBDeviceManager(BaseModel):
    """Class for managing ADB devices and retrieving device information.

    Attributes:
        host (str): The host IP address.
        target (str): The target app package name.

    Methods:
        available_devices: Returns a list of available devices.
        serials: Retrieves a list of serial numbers for connected devices.
        running_apps: Retrieves the running apps on the connected devices.
        get_correct_serial: Returns the correct serial number for the target app.

    Raises:
        Exception: If multiple or no matching apps are found.
    """

    host: str = Field(default="127.0.0.1")
    target: str = Field(default="com.longe.allstarhmt", description="The game you wanna afk.")

    @computed_field
    @property
    def available_devices(self) -> list[int]:
        """Returns a list of available devices.

        Returns:
            list[int]: A list of available devices.
        """
        mumu_player = [16384, 16416]
        # ld_player = [5555, 5557]
        available_devices = [*mumu_player]
        return available_devices

    @computed_field
    @property
    def serials(self) -> list[str]:
        """Retrieves a list of serial numbers for connected devices.

        Returns:
            A list of serial numbers for connected devices.
        """
        for available_device in self.available_devices:
            adb.connect(addr=f"{self.host}:{available_device}", timeout=3.0)
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
        """Retrieves the running apps on the connected devices.

        Returns:
            A list of AppInfo objects representing the running apps on the connected devices.
        """
        running_apps = []
        for serial in self.serials:
            device = adb.device(serial=serial)
            running_app = device.app_current()
            running_details = AppInfo(**{"serial": serial, "package": running_app.package})
            running_apps.append(running_details)
        return running_apps

    def get_correct_serial(self) -> AppInfo:
        """Returns the correct serial number for the target app.

        This method searches for the running apps that match the target app's package name.
        If there are multiple or no matching apps found, an exception is raised.
        Otherwise, the serial number of the first matching app is returned.

        Returns:
            AppInfo: The app information for the correct serial number.

        Raises:
            Exception: If multiple or no matching apps are found.
        """
        apps = [r_app for r_app in self.running_apps if r_app.package == self.target]
        if len(apps) > 1 or len(apps) == 0:
            raise Exception("Multiple or no devices found")
        app = next(iter(apps))
        return app


if __name__ == "__main__":
    target = "com.longe.allstarhmt"
    apps = ADBDeviceManager(host="127.0.0.1", target=target).get_correct_serial()
