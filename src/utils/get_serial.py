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
        for port in self.available_devices:
            adb.connect(addr=f"{self.host}:{port}", timeout=3.0)
        devices = adb.device_list()
        serials = [device.serial for device in devices if not device.serial.startswith("emulator")]
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
            running_details = AppInfo(serial=serial, package=running_app.package)
            running_apps.append(running_details)
        return running_apps

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
            raise ValueError("No devices running the target app were found.")
        raise ValueError("Multiple devices running the target app were found.")


if __name__ == "__main__":
    target = "com.longe.allstarhmt"
    apps = ADBDeviceManager(host="127.0.0.1", target=target).get_correct_serial()
