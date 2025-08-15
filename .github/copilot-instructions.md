⚠️ IMPORTANT: Keep this file aligned with the actual project. Update it whenever behavior, APIs, or workflows change.

### Project Overview

- Auto Click is a YAML-driven UI automation tool. It captures screenshots from one of three targets (Windows apps, Android devices via ADB, or web browsers via Playwright) and detects UI elements via OpenCV template matching. If configured, it clicks the matched point and sleeps for a delay. It can send Discord notifications on completion or error.

### Runtime Architecture

- Entry points: `auto_click.cli:main` (also exposed as `auto_click` and `cli`).
- Orchestration: `AutoClicker` loads YAML → builds `RemoteController` → loops `RemoteController.run()` until `task_done` or `error_occurred`.
- Targets (in `auto_click.cores.screenshot.ScreenshotManager`):
  - Window: `from_window(window_title)` uses `pygetwindow` + `PIL.ImageGrab`; clicking via `pyautogui` with window-origin calibration.
  - Android: `from_adb(url=package, serial)` uses `adbutils`; clicking via `AdbDevice.click`.
  - Browser: `from_browser(url)` uses Playwright (Chromium, `channel="chrome"`, headless + stealth) and clicks via `Page.mouse.click`.
- Device selection (ADB): `auto_click.cores.manager.ADBDeviceManager` connects to `host:serial`, enumerates devices, and picks the one whose current package equals `target`.
- Matching: `auto_click.cores.compare.ImageComparison.find()` converts screenshot and template to grayscale and uses `cv2.matchTemplate(..., TM_CCOEFF_NORMED)`. If `max_val > confidence`, returns center point as `FoundPosition`. `ImageComparison` now accepts only `image_cfg` and `screenshot` (no device parameter).
- Notifications: `auto_click.cores.notify.DiscordNotify` posts an embed (with optional image) to `DISCORD_WEBHOOK_URL`.

### Configuration Schema (YAML → `ConfigModel`)

- `enable: bool` — master switch.
- `target: str` — window title, Android package, or a URL.
- `host: str`, `serial: str` — both required together for ADB mode; otherwise both empty.
- `image_list: list[ImageModel]` — ordered operations:
  - `image_name: str`
  - `image_path: str`
  - `delay_after_click: int` — seconds to sleep after clicking.
  - `enable_click: bool` — whether to click on match.
  - `enable_screenshot: bool` — reserved (not used by runtime today).
  - `confidence: float` — template-match threshold (0.0–1.0).

### CLI Usage

- Run with a config:
  - `uv run python src/auto_click/cli.py --config_path=./configs/games/mahjong.yaml`
  - or `uv run auto_click --config_path=./configs/games/all_stars.yaml`

### Developer Guidelines

- **Code Style**: PEP 8; Ruff configured in `pyproject.toml` (auto-fix enabled). Use descriptive names; keep functions small.
- **Pydantic v2**: prefer `Field` with `description`; use `@model_validator` for invariants and validation.
- **Async/Await**: IO paths (Playwright, HTTP, ADB operations) are async; avoid blocking calls in async flows.
- **Assets Management**: template images under `data/*`; tests ensure files referenced by YAML exist.
- **Logging**: use `logfire` structured logs with contextual information; avoid `print` statements.
- **Error Handling**: implement graceful error recovery with retry mechanisms; use specific exception types.
- **Configuration**: use Pydantic models for all configuration; validate at startup.

### Dependency Management

- Use `uv`:
  - Production: `uv add <pkg>`, `uv remove <pkg>`
  - Development: `uv add <pkg> --dev`, `uv remove <pkg> --dev`

### CI / QA

- Tests: `uv run pytest -q` (async mode auto; coverage to `.github/reports`).
- Lint/format: `uv run ruff check --fix .` or via pre-commit hooks.

### Common Tasks

- Run app: `uv run auto_click --config_path=./configs/games/mahjong.yaml`
- Serve docs: `uv run poe docs`
- Generate docs: `uv run poe docs_gen`

### Notes / Limitations

- `enable_screenshot` is currently not used by runtime; screenshot logging helpers exist but are commented.
- Window mode requires Windows OS and uses `pygetwindow` + `pyautogui`.
- Browser mode launches Chrome by default; change `channel` in `auto_click.cores.screenshot.from_browser` if needed.
- ADB mode requires `host` and `serial` both set and the `target` package running on the device.
- Template matching works best with high-contrast, clear images; avoid blurry or low-resolution templates.
- Confidence thresholds typically range from 0.7-0.95; higher values require more exact matches.

### Architecture Components

- **CLI Layer**: `auto_click.cli` - Entry point and command-line interface using Fire
- **Controller Layer**: `auto_click.controller.RemoteController` - Main orchestration and business logic
- **Core Services**:
  - `auto_click.cores.screenshot` - Multi-platform screenshot capture
  - `auto_click.cores.compare` - OpenCV-based image matching
  - `auto_click.cores.manager` - ADB device management
  - `auto_click.cores.notify` - Discord webhook notifications
  - `auto_click.cores.config` - Pydantic configuration models

### Development Best Practices

- Use type hints for all function parameters and return values
- Implement comprehensive error handling with specific exception types
- Write unit tests for core functionality (especially image comparison logic)
- Use async/await for all I/O operations (file reads, network calls, ADB commands)
- Validate all external inputs using Pydantic models
- Use structured logging with contextual information for debugging
