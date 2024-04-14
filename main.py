import time
import datetime

from PIL import ImageGrab
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from rich.console import Console

console = Console()


def find_and_click_button(image_path: str, log_filename: str, screenshot: str):
    button_image = cv2.imread(image_path, 0)
    if button_image is None:
        raise Exception(f"Unable to load button image from path: {image_path}")
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(screenshot_gray, button_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    threshold = 0.9
    if max_val > threshold:
        button_w = button_image.shape[1]
        button_h = button_image.shape[0]
        top_left = max_loc
        bottom_right = (top_left[0] + button_w, top_left[1] + button_h)
        cv2.rectangle(screenshot_gray, top_left, bottom_right, 255, 2)
        cv2.imwrite(log_filename, screenshot_gray)
        return max_loc, button_image.shape
    return None, None


def capture_screen(window_title: str):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        if window.isMinimized:
            window.restore()
        window.activate()
        time.sleep(0.1)
        x, y = window.topleft
        width, height = window.size
        bbox = (x, y, x + width, y + height)
        screenshot = ImageGrab.grab(bbox=bbox)
        return screenshot
    except Exception as e:
        console.log(f"Error capturing screen: {e}")
        return None


def main(pic_samples: list, log_dir: str, window_title: str):
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{log_dir}/{now}.png"
        screenshot = capture_screen(window_title)
        if screenshot is not None:
            for pic_sample in pic_samples:
                loc, button_shape = find_and_click_button(pic_sample, log_filename, screenshot)
                if loc and button_shape:
                    button_center_x = loc[0] + button_shape[1] / 2
                    button_center_y = loc[1] + button_shape[0] / 2
                    pyautogui.moveTo(button_center_x, button_center_y)
                    # pyautogui.click()
                    console.log(f"Clicked on button found at {loc}")
                    break
        time.sleep(5)


if __name__ == "__main__":
    pic_samples = ["./data/samples/confirm.png"]
    log_dir = "./data/logs"
    main(pic_samples, log_dir, "雀魂麻将")
