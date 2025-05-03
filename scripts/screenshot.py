import contextlib

from adbutils import adb
from pydantic import Field, BaseModel


class Screenshot(BaseModel):
    port: int = Field(default=5557, description="The port number of the device.")
    output_path: str = Field(default="./debug.png")

    async def screenshots(self) -> None:
        serial = f"127.0.0.1:{self.port}"
        try:
            # Try to connect to the device
            adb.connect(addr=serial)
            device = adb.device(serial=serial)

            # Take the screenshot
            current_screent = device.screenshot()
            current_screent.save(self.output_path)
        finally:
            # Always disconnect to free the port
            with contextlib.suppress(Exception):
                adb.disconnect(serial)

    async def __call__(self) -> None:
        await self.screenshots()


if __name__ == "__main__":
    import fire

    fire.Fire(Screenshot)
