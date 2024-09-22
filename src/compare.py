import os
import time

# import datetime
import cv2
import numpy as np
import logfire
from pydantic import Field, BaseModel, ConfigDict, computed_field
import PIL.Image as Image

from src.types.image_models import ImageModel


class ImageComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image_cfg: ImageModel = Field(..., description="The image configuration")
    screenshot: Image.Image | bytes = Field(..., description="The screenshot image")

    # @model_validator(mode="after")
    # def get_screenshot_image(self) -> Image.Image | bytes:
    #     if isinstance(self.screenshot, bytes):
    #         image_stream = BytesIO(self.screenshot)
    #         return Image.open(image_stream)
    #     return self.screenshot

    @computed_field
    @property
    def screenshot_array(self) -> tuple[np.ndarray, np.ndarray]:
        color_screenshot = np.array(self.screenshot)
        color_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2BGR)
        gray_screenshot = cv2.cvtColor(color_screenshot, cv2.COLOR_RGB2GRAY)
        return color_screenshot, gray_screenshot

    @computed_field
    @property
    def log_filename(self) -> str:
        # now = datetime.datetime.now().strftime("%Y%m%d")
        log_dir = "./logs"
        os.makedirs(log_dir, exist_ok=True)
        image_name = self.image_cfg.image_path.split("/")[-1].split(".")[0]
        log_filename = f"{log_dir}/{image_name}.png"
        time.sleep(1)
        return log_filename

    @computed_field
    @property
    def button_image(self) -> cv2.typing.MatLike:
        button_image = cv2.imread(self.image_cfg.image_path, 0)
        if button_image is None:
            logfire.warn("Unable to load button image", **self.image_cfg.model_dump())
        return button_image

    # def draw_rectangle(
    #     self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point
    # ) -> None:
    #     color_screenshot, _ = self.screenshot_array
    #     cv2.rectangle(color_screenshot, max_loc, matched_image_position, (0, 0, 255), 2)
    #     cv2.imwrite(self.log_filename, color_screenshot)
    #     logfire.info(
    #         "The screenshot has been saved",
    #         log_filename=self.log_filename,
    #         **self.image_cfg.model_dump(),
    #     )

    def draw_rectangle(
        self, matched_image_position: tuple[int, int], max_loc: cv2.typing.Point
    ) -> None:
        color_screenshot, _ = self.screenshot_array

        # 建立一個全黑的遮罩
        mask = np.zeros_like(color_screenshot)

        # 在遮罩上畫出白色矩形，表示保留紅色框內的部分
        cv2.rectangle(mask, max_loc, matched_image_position, (255, 255, 255), -1)

        # 創建一個完全黑色的圖片
        black_img = np.zeros_like(color_screenshot)

        # 將紅色框內的部分保留，其餘部分塗黑
        color_screenshot = cv2.bitwise_and(color_screenshot, mask) + cv2.bitwise_and(
            black_img, cv2.bitwise_not(mask)
        )

        # 在結果圖像上畫出紅色框
        cv2.rectangle(color_screenshot, max_loc, matched_image_position, (0, 0, 255), 2)

        # 儲存結果圖像
        cv2.imwrite(self.log_filename, color_screenshot)

        logfire.info(
            "The screenshot has been saved",
            log_filename=self.log_filename,
            **self.image_cfg.model_dump(),
        )

    def find(self) -> tuple[int | None, int | None]:
        _, gray_screenshot = self.screenshot_array

        result = cv2.matchTemplate(gray_screenshot, self.button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        button_center_x = int(max_loc[0] + self.button_image.shape[1])
        button_center_y = int(max_loc[1] + self.button_image.shape[0])
        matched_image_position = (button_center_x, button_center_y)

        if max_val > self.image_cfg.confidence:
            logfire.info(
                "Found the target image",
                confidence_decision=max_val,
                button_center_x=button_center_x,
                button_center_y=button_center_y,
                **self.image_cfg.model_dump(),
            )
            if self.image_cfg.screenshot_option is True:
                self.draw_rectangle(matched_image_position, max_loc)
            return button_center_x, button_center_y
        return None, None
