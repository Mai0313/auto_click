### Auto Click

[![python](https://img.shields.io/badge/-Python_3.10_%7C_3.11_%7C_3.12-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![tests](https://github.com/Mai0313/auto_click/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/auto_click/tree/master?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/auto_click/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/auto_click.svg)](https://github.com/Mai0313/auto_click/graphs/contributors)

Auto Click is a small automation tool that detects UI elements from screenshots and clicks them automatically based on a YAML configuration. It supports Windows desktop windows, Android apps via ADB, and web pages via a headless browser.

## Features

- **Three target modes**:
  - **Window title (Windows only)**: capture a specific window and click using `pyautogui`.
  - **Android (ADB)**: capture and click on a device running a specific package.
  - **Browser (Playwright)**: navigate to a URL and click on the page.
- **Template matching**: OpenCV `matchTemplate` on grayscale; configurable `confidence` per image.
- **YAML-driven flows**: per-image `enable_click` and `delay_after_click`.
- **Discord notifications**: optional webhook updates on completion and errors.

## Requirements

- Windows 10+ recommended. Window-title mode requires Windows.
- Google Chrome installed if you use browser mode (Playwright launches with `channel="chrome"`).
- ADB available if you use Android mode; ensure the device/emulator is reachable.

## Install

1) Install `uv` and sync dependencies:

```bash
uv sync
```

2) (Optional) Install Playwright browsers if you prefer bundled browsers:

```bash
uv run playwright install
```

3) (Optional) Set a Discord webhook in a `.env` file:

```bash
echo DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." > .env
```

## Configuration

Minimal example for a Windows window target (e.g., Mahjong Soul):

```yaml
enable: true
target: "雀魂麻将"   # Window title (exact match)
host: ""
serial: ""
image_list:
  - image_name: "開始段位"
    image_path: "./data/mahjong/ranking.png"
    delay_after_click: 1
    enable_click: true
    enable_screenshot: false  # currently not used in code
    confidence: 0.9
```

Android (ADB) example (package must be running on the device):

```yaml
enable: true
target: com.longe.allstarhmt
host: "127.0.0.1"
serial: "16416"          # forms 127.0.0.1:16416
image_list:
  - image_name: "開始配對"
    image_path: "./data/allstars/start.png"
    delay_after_click: 20
    enable_click: true
    enable_screenshot: true  # currently not used in code
    confidence: 0.75
```

Notes:
- `host` and `serial` must be provided together or both empty.
- `confidence` is the threshold for a positive match (0.0–1.0).
- The click point is the center of the matched template.

## Run

Run with a specific config:

```bash
uv run python src/auto_click/cli.py --config_path=./configs/games/mahjong.yaml
```

If installed as a script, you can also do:

```bash
uv run auto_click --config_path=./configs/games/all_stars.yaml
```

The program will loop through `image_list` and click on matched items. For the All Stars example, confirming certain dialogs triggers a game-switch flow and a Discord notification.

## Troubleshooting

- **Window mode**: the window must be restored and focused; the title must match exactly.
- **Android mode**: ensure the target package is running; the tool uses ADB to find the device running `target`.
- **Browser mode**: install Google Chrome or change the launch `channel` in `cores/screenshot.py`.
- **No matches**: adjust `confidence` or image assets under `./data/*`.

## License

MIT
