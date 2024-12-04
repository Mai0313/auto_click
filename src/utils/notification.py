import datetime

import httpx
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings


class Notification(BaseSettings):
    title: str = Field(
        ...,
        title="Title",
        description="The title of the notification message.",
        frozen=True,
        deprecated=False,
    )
    current_status: str = Field(
        ...,
        title="Current Status",
        description="The current status of the system",
        frozen=True,
        deprecated=False,
    )
    description: str = Field(
        ...,
        title="Description",
        description="The description of the notification message.",
        frozen=True,
        deprecated=False,
    )

    discord_webhook_url: str = Field(
        ...,
        validation_alias=AliasChoices("DISCORD_WEBHOOK_URL"),
        title="Discord Webhook URL",
        description="The URL of the Discord webhook to send notifications to.",
        frozen=True,
        deprecated=False,
    )

    async def send_discord_notification(self) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "embeds": [
                {
                    "title": f"📢 {self.title}",
                    "description": f"**當前狀態**: {self.current_status}\n**敘述**: {self.description}",
                    "color": 65280,  # Green color
                    "footer": {"text": f"時間: {timestamp}"},
                }
            ]
        }

        # Send the request to Discord Webhook

        async with httpx.AsyncClient() as client:
            await client.post(url=self.discord_webhook_url, json=payload)


if __name__ == "__main__":
    notification = Notification(
        title="系統管理員", current_status="更新完成", description="伺服器已成功部署新的更新版本。"
    )
    import asyncio

    asyncio.run(notification.send_discord_notification())
