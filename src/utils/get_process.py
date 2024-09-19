import psutil
import adbutils
from pydantic import BaseModel, ConfigDict, computed_field


class ProcessInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @computed_field
    @property
    def process_list(self) -> list[psutil.Process]:
        processes = psutil.process_iter()
        process_list: list[psutil.Process] = []
        for process in processes:
            process_list.append(process)
            # process_dict = {"pid": process.pid, "name": process.name(), "status": process.status()}
        return process_list

    def get_adb_port(self) -> list[str]:
        """This function will use pid to get the adb port.

        dnplayer.exe: 雷電模擬器
        MuMu Player 12: MuMu模擬器

        Returns:
            list[str]: list of adb host and port
        """
        running_devices = []
        for device in adbutils.adb.device_list():
            running_devices.append(device.info)
        return running_devices


if __name__ == "__main__":
    p = ProcessInfo()
    process = p.process_list
    running_devices = p.get_adb_port()
