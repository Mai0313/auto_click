⚠️ IMPORTANT: Keep this file aligned with the actual project. Update it whenever behavior, APIs, or workflows change.

### Project Overview

- Auto Click is a YAML-driven UI auto-clicker. It captures screenshots from one of three targets and detects UI elements via OpenCV template matching. If configured, it clicks the matched point and sleeps for a delay. It can send Discord notifications on completion or error.

### Runtime Architecture

- Entry points: `auto_click.cli:main` (also exposed as `auto_click` and `cli`).
- Orchestration: `AutoClicker` loads YAML → builds `RemoteController` → loops `RemoteController.run()` until `task_done` or `error_occurred`.
- Targets (in `auto_click.cores.screenshot.ScreenshotManager`):
  - Window: `from_window(window_title)` uses `pygetwindow` + `PIL.ImageGrab`; clicking via `pyautogui` with window-origin calibration.
  - Android: `from_adb(url=package, serial)` uses `adbutils`; clicking via `AdbDevice.click`.
  - Browser: `from_browser(url)` uses Playwright (Chromium, `channel="chrome"`, headless + stealth) and clicks via `Page.mouse.click`.
- Device selection (ADB): `auto_click.cores.manager.ADBDeviceManager` connects to `host:serial`, enumerates devices, and picks the one whose current package equals `target`.
- Matching: `auto_click.cores.compare.ImageComparison.find()` converts screenshot and template to grayscale and uses `cv2.matchTemplate(..., TM_CCOEFF_NORMED)`. If `max_val > confidence`, returns center point as `FoundPosition`.
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

- Style: PEP 8; Ruff configured in `pyproject.toml` (auto-fix enabled). Use descriptive names; keep functions small.
- Pydantic v2: prefer `Field` with `description`; use `@model_validator` for invariants.
- Async: IO paths (Playwright, HTTP) are async; avoid blocking calls in async flows.
- Assets: images under `data/*`; tests ensure files referenced by YAML exist.
- Logging: use `logfire` structured logs; avoid `print`.

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
- Window mode requires Windows.
- Browser mode launches Chrome; change `channel` in `auto_click.cores.screenshot.from_browser` if needed.
- ADB mode requires `host` and `serial` both set and the `target` package running.
