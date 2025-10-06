# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Auto Click is a multi-platform automation tool that detects UI elements from screenshots and performs automatic clicks using OpenCV template matching. It supports three target modes:
- **Windows Applications**: Uses pyautogui with window calibration
- **Android Devices**: ADB-based interaction
- **Web Browsers**: Playwright with stealth mode

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Install Playwright browsers (for browser automation)
uv run playwright install chromium

# Install pre-commit hooks
pre-commit install
```

### Running the Application
```bash
# Using CLI with config file
uv run auto_click --config_path=./configs/games/mahjong.yaml

# Alternative: Direct module invocation
uv run python src/auto_click/cli.py --config_path=./configs/games/all_stars.yaml
```

### Testing and Quality
```bash
# Run all tests (with parallel execution and coverage)
pytest
# Or: make test

# Run linting and formatting
pre-commit run -a
# Or: make format

# Clean build artifacts
make clean
```

### Documentation
```bash
# Generate documentation
make gen-docs

# Serve documentation locally
uv run poe docs_run
```

## Code Architecture

### Core Components

1. **Entry Point** (`cli.py`)
   - Uses Fire library for CLI argument parsing
   - Loads YAML configuration and initializes `RemoteController`
   - Main loop runs until task completion or error

2. **RemoteController** (`controller.py`)
   - Central orchestrator that coordinates all automation logic
   - Manages screenshot capture, image comparison, and click execution
   - Handles three device types: Windows (ShiftPosition), Android (AdbDevice), Browser (Page)
   - Key methods:
     - `get_screenshot()`: Routes to appropriate screenshot method based on target type
     - `click_button()`: Executes clicks with device-specific logic
     - `run()`: Main automation loop

3. **Screenshot Management** (`cores/screenshot.py`)
   - `ScreenshotManager` provides three capture methods:
     - `from_window()`: Captures Windows application using pygetwindow
     - `from_adb()`: Captures Android screen via ADB
     - `from_browser()`: Captures webpage using Playwright with anti-detection
   - Returns `Screenshot` object containing both image and device reference

4. **Image Comparison** (`cores/compare.py`)
   - `ImageComparison` uses OpenCV template matching (TM_CCOEFF_NORMED)
   - Converts images to grayscale for better matching performance
   - Returns `FoundPosition` with button coordinates when confidence threshold met
   - Click coordinates calculated as center of matched template

5. **ADB Device Management** (`cores/manager.py`)
   - `ADBDeviceManager` handles multiple connected Android devices
   - Validates that target package is currently running
   - Automatically selects correct device when multiple are connected

6. **Configuration** (`cores/config.py`)
   - Pydantic models for type-safe configuration parsing
   - `ImageModel`: Per-image settings (path, confidence, delays, click enable)
   - `DeviceModel`: Target specification with host/serial validation
   - `ConfigModel`: Top-level configuration combining device + image list

### Target Detection Logic

The system determines automation mode based on the `target` field:
- Starts with `http`: Browser mode
- Starts with `com`: Android package mode (requires host + serial)
- Otherwise: Windows application mode (matches exact window title)

### Click Calibration

**Windows Mode**: Click coordinates must be calibrated with window position offset (shift_x, shift_y) because pyautogui uses absolute screen coordinates.

**Android/Browser Mode**: No calibration needed; coordinates are relative to device/page.

### Configuration Files

YAML configs in `configs/games/` define:
- `target`: Window title, Android package name, or URL
- `host` + `serial`: ADB connection (both required for Android, both empty otherwise)
- `image_list`: Ordered sequence of images to detect and click
  - `confidence`: Match threshold (0.7-0.95 typical range)
  - `delay_after_click`: Seconds to wait after clicking
  - `enable_click`: Whether to click when found

## Important Notes

### Testing
- Pytest configured with parallel execution (`-n=auto`)
- Coverage requirement: 80% minimum
- Test markers: `@pytest.mark.slow`, `@pytest.mark.skip_when_ci`
- Tests located in `tests/` directory

### Code Quality
- Uses Ruff for linting and formatting (Google docstring convention)
- Line length: 99 characters
- Type hints required (except `__init__`)
- Pre-commit hooks enforce style consistency

### Logging
- Logfire integration for structured logging
- Logs stored in `.cache/.logfire/`
- Console output includes timestamps and spans

### Windows Automation Specifics
- Target window must be restored (not minimized) and visible
- Window title matching is case-sensitive and exact
- Uses `ImageGrab.grab()` with bbox based on window position

### Android Automation Specifics
- ADB connection format: `{host}:{serial}` (e.g., "127.0.0.1:16416")
- Validates that target package is currently running before each screenshot
- Device.click() uses pixel coordinates directly

### Browser Automation Specifics
- Uses Chromium via Playwright with `channel="chrome"`
- Stealth mode enabled to bypass anti-bot detection
- Headless mode by default
- Custom user agent and viewport settings

### Discord Notifications
- Configured via `DISCORD_WEBHOOK_URL` environment variable
- Sends alerts on task completion or errors
- Can attach screenshots for visual confirmation
