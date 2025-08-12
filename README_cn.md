### Auto Click

[![python](https://img.shields.io/badge/-Python_3.10_%7C_3.11_%7C_3.12-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![tests](https://github.com/Mai0313/auto_click/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/auto_click/tree/master?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/auto_click/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/auto_click.svg)](https://github.com/Mai0313/auto_click/graphs/contributors)

Auto Click 是一個小型自動化工具，透過比對螢幕截圖中的按鈕圖片，自動進行點擊。行為由 YAML 檔案驅動，支援 Windows 視窗、Android（ADB）以及瀏覽器。

## 功能

- **三種目標模式**：
  - **視窗標題（Windows）**：擷取指定視窗並用 `pyautogui` 點擊。
  - **Android（ADB）**：對在裝置上執行的指定套件擷取與點擊。
  - **瀏覽器（Playwright）**：開啟網址並在頁面上點擊。
- **樣板比對**：以 OpenCV `matchTemplate`（灰階）偵測；每張圖可調整 `confidence`。比對僅依賴擷取到的截圖與樣板圖片；底層的裝置物件只在執行點擊時使用。
- **YAML 流程**：每張圖可設定 `enable_click` 與 `delay_after_click`。
- **Discord 通知**：完成與錯誤時可透過 Webhook 發送訊息。

## 需求

- 建議 Windows 10+。視窗模式僅支援 Windows。
- 若使用瀏覽器模式，需安裝 Google Chrome（以 `channel="chrome"` 啟動）。
- 若使用 Android 模式，需安裝 ADB 並確保可連線到裝置/模擬器。

## 安裝

1) 安裝 `uv` 並同步依賴：

```bash
uv sync
```

2) （可選）安裝 Playwright 瀏覽器：

```bash
uv run playwright install
```

3) （可選）在 `.env` 設定 Discord webhook：

```bash
echo DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." > .env
```

## 設定範例

Windows 視窗模式（例如：雀魂麻將）：

```yaml
enable: true
target: "雀魂麻将"   # 視窗標題（需完全相符）
host: ""
serial: ""
image_list:
  - image_name: "開始段位"
    image_path: "./data/mahjong/ranking.png"
    delay_after_click: 1
    enable_click: true
    enable_screenshot: false  # 目前程式中未使用
    confidence: 0.9
```

Android（ADB）模式（指定套件需在裝置上執行中）：

```yaml
enable: true
target: com.longe.allstarhmt
host: "127.0.0.1"
serial: "16416"
image_list:
  - image_name: "開始配對"
    image_path: "./data/allstars/start.png"
    delay_after_click: 20
    enable_click: true
    enable_screenshot: true  # 目前程式中未使用
    confidence: 0.75
```

注意：
- `host` 與 `serial` 需同時提供或同時留空。
- `confidence` 為樣板比對門檻（0.0–1.0）。
- 點擊位置為樣板中心點。

## 執行

以特定設定檔啟動：

```bash
uv run python src/auto_click/cli.py --config_path=./configs/games/mahjong.yaml
```

若已安裝腳本，也可：

```bash
uv run auto_click --config_path=./configs/games/all_stars.yaml
```

程式會依序掃描 `image_list`，偵測到符合項目即進行點擊。在 All Stars 範例中，部分確認畫面會觸發切換模式並傳送 Discord 通知。

## 疑難排解

- **視窗模式**：視窗需被還原並聚焦；標題需完全相符。
- **Android 模式**：確認目標套件正在執行；工具會透過 ADB 尋找正在執行 `target` 的裝置。
- **瀏覽器模式**：請安裝 Google Chrome，或修改 `cores/screenshot.py` 中的啟動 `channel`。
- **無法偵測**：調整 `confidence` 或替換 `./data/*` 下的圖片素材。

## 授權

MIT
