from typing import Any
import asyncio
import logging
from pathlib import Path
import datetime

import pytz
import yaml
import logfire
from pydantic import Field, BaseModel

from src.controller import RemoteController

logfire.configure(send_to_logfire=False)
logging.getLogger("sqlalchemy.engine.Engine").disabled = True


class AutoClicker(BaseModel):
    config_path: str = Field(default="./configs/games/all_stars.yaml")

    async def load_yaml(self) -> dict[str, Any]:
        config_obj = Path(self.config_path)
        config_content = config_obj.read_text(encoding="utf-8")
        config_dict = yaml.safe_load(config_content)
        return config_dict

    async def __call__(self) -> None:
        config = await self.load_yaml()
        remote_controller = RemoteController(**config)
        # 等到凌晨兩點到晚上十一點才開始
        while True:
            current_hour = datetime.datetime.now(pytz.timezone("Asia/Taipei")).hour
            should_start = 2 <= current_hour <= 23
            if should_start:
                break
            await asyncio.sleep(60)  # 每分鐘檢查一次
        while True:
            await remote_controller.run()
            if remote_controller.task_done:
                break
            if remote_controller.error_occurred:
                break


if __name__ == "__main__":
    import fire

    fire.Fire(AutoClicker)
