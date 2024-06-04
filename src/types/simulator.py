from pydantic import BaseModel


class SimulatorSettings(BaseModel):
    adb_port: int
