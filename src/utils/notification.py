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
        timestamp = datetime.datetime.now().isoformat()  # ISO 8601 格式
        payload = {
            "embeds": [
                {
                    "author": {
                        "name": "Notification Bot",
                        "url": "https://example.com",
                        "icon_url": "https://i.imgur.com/fKL31aD.jpg",
                    },
                    "title": f"📢 {self.title}",
                    "url": "https://your-service-url.com",  # 可選：加入點擊標題跳轉的 URL
                    "description": f"**當前狀態**: {self.current_status}\n**敘述**: {self.description}",
                    "color": 65280,  # 綠色
                    "fields": [
                        {
                            "name": "更多資訊",
                            "value": "[點擊這裡](https://your-service-url.com/details)",
                            "inline": True,
                        },
                        {"name": "狀態更新", "value": "此通知為自動生成", "inline": True},
                    ],
                    "image": {
                        "url": "https://i.imgur.com/ZGPxFN2.jpg"  # 可選：加入圖片
                    },
                    "thumbnail": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/3/38/4-Nature-Wallpapers-2014-1_ukaavUI.jpg"  # 可選：加入縮略圖
                    },
                    "footer": {
                        "text": f"時間: {timestamp}",
                        "icon_url": "https://i.imgur.com/fKL31aD.jpg",
                    },
                    "timestamp": timestamp,
                }
            ]
        }

        # 發送請求到 Discord Webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(url=self.discord_webhook_url, json=payload)
            response.raise_for_status()  # 確保請求成功


if __name__ == "__main__":
    import asyncio

    notify = Notification(
        title="老大, 我已經幫您打完王朝了",
        current_status="成功",
        description="王朝已完成，將繼續為您採棉花。",
    )

    asyncio.run(notify.send_discord_notification())
