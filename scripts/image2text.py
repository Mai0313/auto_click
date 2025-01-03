from PIL import Image, ImageDraw
from pydantic import Field, BaseModel, ConfigDict
from paddleocr import PaddleOCR
from rich.console import Console

console = Console()


class OCRCore(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    image_path: str = Field(
        ...,
        title="Path to the image file",
        description="Path to the image file for OCR processing",
        deprecated=False,
    )

    def get_text(self) -> list:
        ocr = PaddleOCR(use_angle_cls=False, lang="ch", ocr_version="PP-OCRv4")
        return ocr.ocr(self.image_path, cls=True)

    def get_text_from_image(self) -> str:
        result = self.get_text()
        text = ""
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                text += line[1][0] + "\n"
        return text

    def draw_boxes(self) -> Image:
        result = self.get_text()
        image = Image.open(self.image_path)
        draw = ImageDraw.Draw(image)
        result = result[0]
        for line in result:
            box = line[0]
            flat_box = [coord for point in box for coord in point]
            draw.polygon(flat_box, outline="red", width=2)
        image.save("custom_result.jpg")
        return image


if __name__ == "__main__":
    ocr_core = OCRCore(image_path="./logs/cropped/confirm.png")
    console.print(ocr_core.get_text_from_image())
    ocr_core.draw_boxes()
