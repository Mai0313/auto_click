<div align="center" markdown="1">

# Auto Click

[![PyPI version](https://img.shields.io/pypi/v/swebenchv2.svg)](https://pypi.org/project/swebenchv2/)
[![python](https://img.shields.io/badge/-Python_%7C_3.11%7C_3.12%7C_3.13%7C_3.14-blue?logo=python&logoColor=white)](https://www.python.org/downloads/source/)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![tests](https://github.com/Mai0313/auto_click/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/auto_click/tree/main?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/auto_click/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/auto_click.svg)](https://github.com/Mai0313/auto_click/graphs/contributors)

</div>

Auto Click is a powerful automation tool that detects UI elements from screenshots and performs automatic clicks based on YAML configuration files. It uses OpenCV template matching for image recognition and supports three target modes: Windows desktop applications, Android devices via ADB, and web browsers via Playwright.

Other Languages: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## Features

- **Multi-Platform Support**:
  - **Windows Applications**: Capture specific windows by title and click using `pyautogui` with automatic window calibration
  - **Android Devices**: Connect via ADB to capture and interact with running applications
  - **Web Browsers**: Automated browser control using Playwright with stealth mode and anti-detection features
- **Advanced Image Recognition**:
  - OpenCV template matching with grayscale conversion for optimal performance
  - Configurable confidence thresholds per image for precise detection
  - Automatic click position calculation (center of matched template)
- **Flexible Configuration**:
  - YAML-driven workflows with per-image settings
  - Customizable delays, click enablement, and confidence levels
  - Support for complex automation sequences
- **Smart Notifications**:
  - Discord webhook integration with rich embeds
  - Automatic error reporting and task completion alerts
  - Image attachments for visual confirmation
- **Robust Error Handling**:
  - Automatic device detection and connection management
  - Graceful failure recovery with retry mechanisms
  - Comprehensive logging with Logfire integration

## Requirements

- **Python 3.11+** (tested with 3.11, 3.12, 3.13)
- **Windows 10+** recommended (required for Windows application automation)
- **Google Chrome** for browser automation (Playwright uses `channel="chrome"`)
- **ADB (Android Debug Bridge)** for Android device automation
- **uv** package manager for dependency management

## Installation

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository and sync dependencies**:

   ```bash
   git clone https://github.com/Mai0313/auto_click.git
   cd auto_click
   uv sync
   ```

3. **Install Playwright browsers** (required for browser automation):

   ```bash
   uv run playwright install chrome
   ```

   **Note**: The tool uses `channel="chrome"` which requires Google Chrome to be installed.

4. **Set up Discord notifications** (optional):
   Create a `.env` file in the project root:

   ```bash
   echo DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your-webhook-url" > .env
   ```

5. **Verify ADB setup** (for Android automation):

   ```bash
   adb devices
   ```

## Configuration

Auto Click uses YAML configuration files to define automation workflows. Each config file specifies target applications and image sequences to detect and interact with.

### Windows Application Example

For automating Windows desktop applications (e.g., Mahjong Soul):

```yaml
enable: true              # Master switch (note: use True/False, not true/false in YAML)
target: 雀魂麻将          # Exact window title (case-sensitive)
host: ''                 # Empty string for Windows mode
serial: ''               # Empty string for Windows mode
image_list:
  - image_name: 開始段位
    image_path: ./data/mahjong/ranking.png
    delay_after_click: 1
    enable_click: true
    enable_screenshot: false
    confidence: 0.9
```

### Android Application Example

For automating Android apps via ADB (package must be running):

```yaml
enable: true
target: com.longe.allstarhmt    # Android package name (must be currently running)
host: 127.0.0.1                # ADB host address
serial: '16416'                 # ADB port (combines to 127.0.0.1:16416)
image_list:
  - image_name: 開始配對
    image_path: ./data/allstars/start.png
    delay_after_click: 20
    enable_click: true
    enable_screenshot: true
    confidence: 0.75
```

**Important**: The tool automatically detects which connected device is running the target package.

### Browser Automation Example

For web automation using Playwright with stealth mode:

```yaml
enable: true
target: https://example.com     # Target URL (will be opened in Chrome)
host: ''                        # Empty string for browser mode
serial: ''                      # Empty string for browser mode
image_list:
  - image_name: Login Button
    image_path: ./data/browser/login.png
    delay_after_click: 3
    enable_click: true
    enable_screenshot: false
    confidence: 0.8
```

**Note**: Browser runs in headless mode with anti-detection features enabled.

### Configuration Parameters

| Parameter           | Type   | Description                                  |
| ------------------- | ------ | -------------------------------------------- |
| `enable`            | bool   | Master switch for automation                 |
| `target`            | string | Window title, package name, or URL           |
| `host`              | string | ADB host (required with serial for Android)  |
| `serial`            | string | ADB port (required with host for Android)    |
| `image_name`        | string | Descriptive name for the image               |
| `image_path`        | string | Path to template image file                  |
| `delay_after_click` | int    | Seconds to wait after clicking               |
| `enable_click`      | bool   | Whether to click when image is found         |
| `enable_screenshot` | bool   | Reserved for future use                      |
| `confidence`        | float  | Match threshold (0.0-1.0, higher = stricter) |

### Important Notes

- For Android mode: `host` and `serial` must both be provided or both empty
- Window titles must match exactly (case-sensitive)
- Template images should be clear, high-contrast screenshots
- Confidence values typically range from 0.7-0.95 for reliable detection
- Click position is automatically calculated as the center of the matched template

## Usage

### Running Auto Click

Execute automation with a specific configuration file:

```bash
# Using the auto_click command (recommended)
uv run auto_click --config_path=./configs/games/mahjong.yaml

# Alternative: Using the cli command
uv run cli --config_path=./configs/games/all_stars.yaml

# Using Python module directly
uv run python -m auto_click.cli --config_path=./configs/games/league.yaml

# Using default configuration (./configs/games/all_stars.yaml)
uv run auto_click

# Using start.bat on Windows
start.bat
```

**Note**: The CLI uses Python Fire, so use `--config_path=<path>` or `--config_path <path>` syntax.

### How It Works

1. **Initialization**: Loads YAML configuration and establishes target connection
   - For Android: Connects via ADB and verifies the target app is running
   - For Windows: Locates the window by exact title and calculates position offsets
   - For Browser: Launches Chromium with anti-detection stealth mode
2. **Screenshot Capture**: Takes periodic screenshots based on target mode
   - Windows: Captures specific window area with automatic position calibration
   - Android: Uses ADB screencap command
   - Browser: Uses Playwright screenshot API
3. **Image Detection**: Uses OpenCV template matching with grayscale conversion to find UI elements
4. **Action Execution**: Clicks detected elements with specified delays
   - Windows: Uses pyautogui with calibrated coordinates (shift_x, shift_y)
   - Android: Uses ADB input tap command
   - Browser: Uses Playwright mouse click API
5. **Notification**: Sends Discord webhook updates on completion or errors with embedded images
6. **Loop Continuation**: Repeats until task completion or error occurs

### Available Configurations

The project includes several pre-configured automation examples:

- `configs/games/mahjong.yaml` - Mahjong Soul automation
- `configs/games/all_stars.yaml` - All Stars game automation
- `configs/games/league.yaml` - League game automation

## Troubleshooting

### Common Issues

**Window Mode Issues**:

- Ensure the target window is restored (not minimized) and visible
- Window title must match exactly (case-sensitive)
- The tool will automatically activate and restore minimized windows
- Click coordinates are automatically calibrated based on window position (shift_x, shift_y)
- Uses pygetwindow to locate windows and pyautogui for clicking
- Check if window title changes during app lifecycle

**Android Mode Issues**:

- Verify ADB connection: `adb devices`
- Ensure target package is currently running on the device (the tool actively checks this)
- Check device is properly connected and accessible
- Confirm host:port combination is correct (e.g., "127.0.0.1:16416")
- The tool will automatically detect which connected device is running the target app
- If multiple devices run the same app, an AdbError will be raised

**Browser Mode Issues**:

- Install Google Chrome (required for Playwright with `channel="chrome"`)
- Check if target URL is accessible
- Verify network connectivity
- The tool uses headless Chromium with stealth mode and anti-detection features:
  - Custom user agent
  - Disabled automation flags
  - Modified browser fingerprints
- For custom browsers, modify `channel` parameter in `src/auto_click/cores/screenshot.py`

**Image Detection Issues**:

- Adjust `confidence` threshold (try values between 0.7-0.95)
- Update template images in `./data/*` directories
- Ensure template images match current UI appearance
- Check image resolution and scaling factors
- Template images should be clear and high-contrast

**Discord Notification Issues**:

- Verify `DISCORD_WEBHOOK_URL` is set correctly in `.env`
- Test webhook URL manually to ensure it's active
- Check Discord server permissions for the webhook

### Debug Tips

- Enable detailed logging by checking log output
- Test individual image templates using the comparison tools
- Verify target application state before running automation
- Use screenshot debugging to see what the tool captures

## License

MIT
