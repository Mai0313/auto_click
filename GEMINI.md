# Auto Click

## Project Overview

**Auto Click** is a powerful Python-based automation tool designed to detect UI elements from screenshots and perform automatic interactions (clicks) based on YAML configuration files.

It supports three primary target modes:

1. **Windows Desktop Applications**: Captures specific windows by title and interacts using `pyautogui` with automatic calibration.
2. **Android Devices**: Connects via ADB to capture screens and simulate touch inputs.
3. **Web Browsers**: Uses Playwright (headless Chromium) for stealthy web automation.

**Core Technologies:**

- **Language:** Python 3.11+
- **Dependency Management:** `uv`
- **Image Recognition:** OpenCV (Template Matching)
- **Automation:** Playwright (Web), ADB (Android), PyAutoGUI (Windows), PyGetWindow
- **CLI:** Google Fire
- **Logging:** Logfire

## Building and Running

### Prerequisites

- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Python**: 3.11 or higher
- **Google Chrome**: Required for Playwright (`channel="chrome"`)
- **ADB**: Required for Android automation

### Installation

```bash
git clone <repository_url>
cd auto_click
uv sync
uv run playwright install chrome
```

### Common Commands

- **Run Automation:**
  ```bash
  # Run with a specific config
  uv run auto_click --config_path=./configs/games/mahjong.yaml

  # Run with default config (./configs/games/all_stars.yaml)
  uv run auto_click
  ```
- **Run Tests:**
  ```bash
  make test
  # or
  uv run pytest
  ```
- **Format & Lint:**
  ```bash
  make format
  # or
  pre-commit run -a
  ```
- **Generate Documentation:**
  ```bash
  make gen-docs
  ```

## Key Files and Directories

- **`src/auto_click/cli.py`**: The main entry point. Uses `python-fire` to expose the `AutoClicker` class to the command line.
- **`src/auto_click/controller.py`**: Contains `RemoteController`, the core logic that orchestrates screenshot capture, image matching, and interaction dispatching.
- **`configs/`**: Stores YAML configuration files defining automation rules (target, images to find, actions).
  - Example: `configs/games/mahjong.yaml`
- **`data/`**: Contains reference images (templates) used for OpenCV matching. Organized by game/task.
- **`src/auto_click/cores/`**: Core modules:
  - `manager.py`: ADB device management.
  - `screenshot.py`: Handling screenshot capture across different platforms.
  - `compare.py`: Image comparison logic using OpenCV.
  - `notify.py`: Discord notification integration.
- **`pyproject.toml`**: Project configuration, dependencies (managed by `uv`), and tool settings (Ruff, MyPy, Pytest).
- **`Makefile`**: Shortcuts for common development tasks.

## Development Conventions

- **Code Style:**
  - Adhere strictly to **Ruff** configuration for linting and formatting.
  - Use **MyPy** for static type checking.
  - Follow **Google-style** docstrings.
- **Configuration:**
  - Automation tasks are defined in **YAML** files.
  - Key fields: `target` (app name/URL), `image_list` (sequence of images to look for), `confidence` (0.0-1.0 matching threshold).
- **Logging & Notifications:**
  - Use `logfire` for application logging.
  - Critical errors or completion status can trigger Discord notifications (configured via `.env` `DISCORD_WEBHOOK_URL`).
- **Testing:**
  - Write tests in `tests/` using `pytest`.
  - Ensure high coverage, especially for core logic.
