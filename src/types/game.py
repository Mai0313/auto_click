import json
from typing import Any
from pathlib import Path

import anyio
from pydantic import Field, BaseModel, computed_field


class GameResult(BaseModel):
    win: int = Field(default=0, title="Win", description="Number of wins")
    lose: int = Field(default=0, title="Lose", description="Number of loses")

    @computed_field
    @property
    def total(self) -> int:
        return self.win + self.lose

    @computed_field
    @property
    def win_rate(self) -> float:
        return self.win / self.total

    @computed_field
    @property
    def lose_rate(self) -> float:
        return self.lose / self.total

    @computed_field
    @property
    def win_lost_dict(self) -> dict[str, Any]:
        return {
            "win": self.win,
            "lose": self.lose,
            "total": self.total,
            "win_rate": self.win_rate,
            "lose_rate": self.lose_rate,
        }

    def export(self, today: str) -> dict[str, Any]:
        log_path = Path("./logs")
        log_path.mkdir(parents=True, exist_ok=True)
        with open(f"./logs/{today}.json", "w") as f:
            json.dump(self.win_lost_dict, f)
        return self.win_lost_dict

    async def a_export(self, today: str) -> dict[str, Any]:
        log_path = Path("./logs")
        log_path.mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(f"./logs/{today}.json", "w") as f:
            await f.write(json.dumps(self.win_lost_dict))
        return self.win_lost_dict
