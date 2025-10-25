# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Auto Click is a multi-platform UI automation tool that uses OpenCV template matching to detect and interact with UI elements. It supports three target modes:

- **Windows applications**: Uses `pygetwindow` for window detection and `pyautogui` for clicking with automatic position calibration
- **Android devices**: Uses `adbutils` to connect via ADB and control Android apps
- **Web browsers**: Uses Playwright with stealth mode for browser automation

## Development Commands

### Running the Application

```bash
# Install dependencies
uv sync

# Install Playwright browsers (required for browser automation)
uv run playwright install chrome

# Run with specific config (using Python Fire CLI syntax)
uv run auto_click --config_path=./configs/games/mahjong.yaml
# Or with space separator
uv run auto_click --config_path ./configs/games/mahjong.yaml

# Alternative command (both entry points work identically)
uv run cli --config_path=./configs/games/all_stars.yaml

# Using Python module directly
uv run python -m auto_click.cli --config_path=./configs/games/league.yaml

# Run with default config (./configs/games/all_stars.yaml)
uv run auto_click

# Adjust loop delay to prevent CPU overuse (default: 0.1 seconds)
uv run auto_click --config_path=./configs/games/mahjong.yaml --loop_delay=0.5
```

### Testing

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_config.py

# Run with specific pytest options (configured in pyproject.toml)
# - Coverage minimum: 80%
# - Parallel execution with pytest-xdist (-n=auto)
# - Reports: ./.github/reports/coverage.xml and ./.github/reports/.coverage.pytest.xml
# - Asyncio mode: auto (configured for async test support)
# - Test logs: ./.github/reports/pytest_logs.log
```

### Code Quality

```bash
# Linting and formatting (auto-fix enabled)
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/
```

### Documentation

```bash
# Generate documentation
make gen-docs

# Serve documentation locally
mkdocs serve

# Deploy documentation
mkdocs gh-deploy --force --clean
```

## Architecture Overview

### Core Components

1. **CLI Entry Point** (`src/auto_click/cli.py`)

   - Uses Python Fire for CLI interface
   - Loads YAML configuration and creates `RemoteController` instance
   - Main loop runs until `task_done` or `error_occurred` flags are set

2. **RemoteController** (`src/auto_click/controller.py`)

   - Core orchestrator that manages the automation workflow
   - Handles three target modes based on `target` field:
     - URLs starting with "http" → Browser mode
     - Package names starting with "com" → Android mode
     - Window titles → Windows mode
   - Uses `target_serial` computed field to automatically detect correct Android device
   - Manages click execution with device-specific logic and coordinate calibration

3. **Screenshot Management** (`src/auto_click/cores/screenshot.py`)

   - `ScreenshotManager` provides three async methods:
     - `from_window()`: Captures Windows application window using `ImageGrab.grab()`, returns `ShiftPosition` for coordinate calibration
     - `from_adb()`: Captures Android screen via ADB screencap, validates running app matches target package
     - `from_browser()`: Captures browser page using Playwright with anti-detection features
   - Returns `Screenshot` object containing both image data and device reference
   - **Performance Optimization**: Reuses browser/ADB connections across calls to avoid repeated initialization overhead
   - Includes `cleanup()` method for proper resource disposal

4. **Image Comparison** (`src/auto_click/cores/compare.py`)

   - `ImageComparison.find()`: Uses OpenCV's `matchTemplate` with grayscale conversion
   - Compares template images against screenshots using `TM_CCOEFF_NORMED` method
   - Returns `FoundPosition` with button center coordinates when confidence threshold is met
   - Click position is calculated as template center: `(max_loc[0] + width // 2, max_loc[1] + height // 2)`
   - **Performance Optimizations**:
     - Template images are cached using `@lru_cache(maxsize=32)` to avoid repeated disk I/O
     - CPU-intensive template matching runs in thread pool via `asyncio.to_thread()` to prevent blocking
     - Screenshot conversion optimized for both PIL Image and bytes input

5. **ADB Device Manager** (`src/auto_click/cores/manager.py`)

   - Connects to ADB using `host:serial` combination (e.g., "127.0.0.1:16416")
   - Automatically detects which connected device is running the target package
   - Raises `AdbError` if zero or multiple devices run the target app

6. **Configuration Models** (`src/auto_click/cores/config.py`)

   - Pydantic models for type-safe configuration:
     - `ImageModel`: Template image settings (path, confidence, delays, click enablement)
     - `DeviceModel`: Target device specification (validates host/serial pairing)
     - `ConfigModel`: Top-level config combining device info and image list

### Key Design Patterns

- **Coordinate Calibration**: Windows mode uses `ShiftPosition` to adjust click coordinates based on window position (`shift_x`, `shift_y`), since screenshots are captured relative to window, but clicks must be absolute screen coordinates. Calibration happens in `FoundPosition.calibrate()` before clicking.
- **Device Detection**: For Android, the tool actively verifies the target app is running and automatically selects the correct device from multiple connected devices via `ADBDeviceManager.get_correct_serial()`
- **Type-Based Routing**: Target string determines mode via `get_screenshot()`: "http" prefix → browser, "com" prefix → Android, otherwise → Windows window title
- **Pydantic Validation**: All configuration uses Pydantic with frozen fields to prevent runtime modification of core settings
- **Resource Reuse**: Browser and ADB connections are cached in `ScreenshotManager` as `_browser`, `_browser_page`, `_adb_device` to minimize initialization overhead
- **Async/Thread Hybrid**: I/O operations (screenshots, clicking) use async/await, CPU-intensive operations (template matching) run in thread pool via `asyncio.to_thread()`

### Automation Flow

1. **Initialization** (`cli.py`):
   - `AutoClicker` loads YAML config via `load_yaml()`
   - Creates `RemoteController` instance with config dict unpacked
   - Enters main loop with `loop_delay` (default 0.1s) to prevent CPU overuse

2. **Main Execution Loop** (`controller.py`):
   - `RemoteController.run()` executes each iteration
   - Capture screenshot via `get_screenshot()` which routes to appropriate method
   - For Android targets: `target_serial` computed field automatically detects device on first access
   - For each template in `image_list`:
     - Match template using `ImageComparison.find()`
     - If match found and `enable_click=True`: call `click_button()`
     - Apply device-specific coordinate calibration if needed (Windows only)
     - Wait for `delay_after_click` seconds
   - Exit conditions: `task_done=True` or `error_occurred=True` breaks the loop

3. **Error Handling**:
   - `AdbError`: Sends Discord notification about emulator issues, sets `error_occurred=True`
   - Generic exceptions: Sends error notification, waits random 0-5 seconds, continues loop

## Configuration System

YAML configs are in `./configs/games/`. Key parameters:

- **Target Identification**:

  - `target`: Window title (exact match, case-sensitive), Android package name, or URL
  - `host` + `serial`: For Android only (e.g., "127.0.0.1" + "16416" → connects to 127.0.0.1:16416)

- **Image Matching**:

  - `confidence`: Threshold for template matching (0.0-1.0, typically 0.7-0.95)
  - `image_path`: Path to template image relative to project root
  - `delay_after_click`: Seconds to wait after clicking
  - `enable_click`: Whether to click when image is found (set to False for detection-only)

## Important Notes

- **Python Version**: Requires 3.11+ (tested with 3.11, 3.12, 3.13)
- **Browser Dependency**: Playwright uses `channel="chrome"` requiring Google Chrome installed (not Chromium)
- **Window Titles**: Must match exactly (case-sensitive). Window is automatically restored/activated before capture via `window.activate()`
- **Android Target**: Must be a running app package name. Tool validates app is currently active via `device.app_current().package`
- **Template Images**: Should be clear, high-contrast screenshots stored in `./data/*/` directories. LRU cached (maxsize=32) for performance
- **Discord Notifications**: Optional feature using `DISCORD_WEBHOOK_URL` environment variable (configured in `.env`). Implemented in `cores/notify.py`
- **Logging**: Uses Logfire with configuration in `[tool.logfire]` section of `pyproject.toml`. Currently set to `send_to_logfire=false` for local-only logging
- **Code Style**: Google-style docstrings, 99 character line length, Ruff for linting/formatting
- **CLI Framework**: Uses Python Fire for automatic CLI generation from `AutoClicker` class methods
- **Entry Points**: Both `cli` and `auto_click` commands point to `auto_click.cli:main` (defined in `[project.scripts]`)
- **Async Architecture**: All core operations are async-first, with CPU-intensive work offloaded to thread pools
- **Error Recovery**: Generic errors trigger random 0-5 second delay before retry; ADB errors terminate immediately
