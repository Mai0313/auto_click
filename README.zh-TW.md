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

Auto Click 是一個強大的自動化工具，可從螢幕截圖中檢測 UI 元素，並根據 YAML 設定檔執行自動點擊。它使用 OpenCV 範本匹配進行圖像識別，並支援三種目標模式：Windows 桌面應用程式、透過 ADB 連接的 Android 裝置，以及透過 Playwright 控制的網頁瀏覽器。

其他語言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 功能特色

- **多平台支援**:
  - **Windows 應用程式**: 透過視窗標題擷取特定視窗，並使用 `pyautogui` 自動校準視窗位置進行點擊
  - **Android 裝置**: 透過 ADB 連接以擷取並與執行中的應用程式互動
  - **網頁瀏覽器**: 使用 Playwright 進行自動化瀏覽器控制，具有隱身模式和反偵測功能
- **進階圖像識別**:
  - OpenCV 範本匹配搭配灰階轉換以達到最佳效能
  - 可針對每個圖像設定信心閾值以進行精確檢測
  - 自動計算點擊位置(匹配範本的中心)
- **彈性設定**:
  - 以 YAML 驅動的工作流程，可針對每個圖像進行設定
  - 可自訂延遲時間、點擊啟用和信心等級
  - 支援複雜的自動化序列
- **智慧通知**:
  - Discord Webhook 整合，支援豐富的嵌入訊息
  - 自動錯誤回報和任務完成警示
  - 附加圖像以進行視覺確認
- **強健的錯誤處理**:
  - 自動裝置偵測和連線管理
  - 優雅的失敗恢復機制與重試
  - 完整的日誌記錄，整合 Logfire

## 系統需求

- **Python 3.11+** (已測試 3.11、3.12、3.13)
- **Windows 10+** 建議使用 (Windows 應用程式自動化所需)
- **Google Chrome** 用於瀏覽器自動化 (Playwright 使用 `channel="chrome"`)
- **ADB (Android Debug Bridge)** 用於 Android 裝置自動化
- **uv** 套件管理器用於相依性管理

## 安裝步驟

1. **安裝 uv** (如果尚未安裝):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **複製儲存庫並同步相依套件**:

   ```bash
   git clone https://github.com/Mai0313/auto_click.git
   cd auto_click
   uv sync
   ```

3. **安裝 Playwright 瀏覽器** (瀏覽器自動化所需):

   ```bash
   uv run playwright install chrome
   ```

   **注意**：工具使用 `channel="chrome"` 需要已安裝 Google Chrome。

4. **設定 Discord 通知** (選用):
   在專案根目錄建立 `.env` 檔案:

   ```bash
   echo DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your-webhook-url" > .env
   ```

5. **驗證 ADB 設定** (用於 Android 自動化):

   ```bash
   adb devices
   ```

## 設定檔說明

Auto Click 使用 YAML 設定檔來定義自動化工作流程。每個設定檔指定目標應用程式和要偵測及互動的圖像序列。

### Windows 應用程式範例

用於自動化 Windows 桌面應用程式 (例如：雀魂麻將):

```yaml
enable: true              # 主開關（注意：在 YAML 中使用 True/False，而非 true/false）
target: 雀魂麻将          # 精確的視窗標題（區分大小寫）
host: ''                 # Windows 模式使用空字串
serial: ''               # Windows 模式使用空字串
image_list:
  - image_name: 開始段位
    image_path: ./data/mahjong/ranking.png
    delay_after_click: 1
    enable_click: true
    enable_screenshot: false
    confidence: 0.9
```

### Android 應用程式範例

用於透過 ADB 自動化 Android 應用程式 (套件必須正在執行):

```yaml
enable: true
target: com.longe.allstarhmt    # Android 套件名稱（必須正在執行中）
host: 127.0.0.1                # ADB 主機地址
serial: '16416'                 # ADB 連接埠（組合為 127.0.0.1:16416）
image_list:
  - image_name: 開始配對
    image_path: ./data/allstars/start.png
    delay_after_click: 20
    enable_click: true
    enable_screenshot: true
    confidence: 0.75
```

**重要**：工具會自動偵測哪個已連接的裝置正在執行目標套件。

### 瀏覽器自動化範例

使用具有隱身模式的 Playwright 進行網頁自動化：

```yaml
enable: true
target: https://example.com     # 目標 URL（將在 Chrome 中開啟）
host: ''                        # 瀏覽器模式使用空字串
serial: ''                      # 瀏覽器模式使用空字串
image_list:
  - image_name: Login Button
    image_path: ./data/browser/login.png
    delay_after_click: 3
    enable_click: true
    enable_screenshot: false
    confidence: 0.8
```

**注意**：瀏覽器以無頭模式執行，並啟用反偵測功能。

### 設定參數說明

| 參數                | 類型   | 說明                                      |
| ------------------- | ------ | ----------------------------------------- |
| `enable`            | bool   | 自動化的主開關                            |
| `target`            | string | 視窗標題、套件名稱或 URL                  |
| `host`              | string | ADB 主機 (Android 模式需配合 serial 使用) |
| `serial`            | string | ADB 連接埠 (Android 模式需配合 host 使用) |
| `image_name`        | string | 圖像的描述名稱                            |
| `image_path`        | string | 範本圖像檔案的路徑                        |
| `delay_after_click` | int    | 點擊後等待的秒數                          |
| `enable_click`      | bool   | 找到圖像時是否點擊                        |
| `enable_screenshot` | bool   | 保留供未來使用                            |
| `confidence`        | float  | 匹配閾值 (0.0-1.0，值越高越嚴格)          |

### 重要注意事項

- Android 模式：`host` 和 `serial` 必須同時提供或同時留空
- 視窗標題必須完全匹配 (區分大小寫)
- 範本圖像應該是清晰、高對比度的螢幕截圖
- 信心值通常在 0.7-0.95 之間可提供可靠的偵測
- 點擊位置會自動計算為匹配範本的中心

## 使用方式

### 執行 Auto Click

使用特定設定檔執行自動化:

```bash
# 使用 auto_click 指令（推薦）
uv run auto_click --config_path=./configs/games/mahjong.yaml

# 替代方案：使用 CLI 腳本名稱
uv run cli --config_path=./configs/games/all_stars.yaml

# 直接使用 Python 模組
uv run python -m auto_click.cli --config_path=./configs/games/league.yaml

# 使用預設設定檔 (./configs/games/all_stars.yaml)
uv run auto_click

# 在 Windows 上使用 start.bat
start.bat
```

**注意**: CLI 使用 Python Fire，因此請使用 `--config_path=<路徑>` 或 `--config_path <路徑>` 語法。

### 運作原理

1. **初始化**: 載入 YAML 設定並建立目標連線
   - Android 模式：透過 ADB 連接並驗證目標應用程式是否正在執行
   - Windows 模式：透過精確的標題定位視窗並計算位置偏移
   - 瀏覽器模式：啟動具有反偵測隱身模式的 Chromium
2. **螢幕截圖擷取**: 根據目標模式定期擷取螢幕截圖
   - Windows：擷取特定視窗區域並自動校準位置
   - Android：使用 ADB screencap 指令
   - 瀏覽器：使用 Playwright 截圖 API
3. **圖像偵測**: 使用 OpenCV 範本匹配搭配灰階轉換來尋找 UI 元素
4. **動作執行**: 以指定的延遲時間點擊偵測到的元素
   - Windows：使用 pyautogui 搭配校準後的座標 (shift_x, shift_y)
   - Android：使用 ADB input tap 指令
   - 瀏覽器：使用 Playwright 滑鼠點擊 API
5. **通知**: 在完成或錯誤時傳送 Discord Webhook 更新並附帶嵌入圖像
6. **循環繼續**: 重複執行直到任務完成或發生錯誤

### 可用的設定檔

專案包含數個預先設定的自動化範例:

- `configs/games/mahjong.yaml` - 雀魂麻將自動化
- `configs/games/all_stars.yaml` - All Stars 遊戲自動化
- `configs/games/league.yaml` - League 遊戲自動化

## 疑難排解

### 常見問題

**視窗模式問題**:

- 確保目標視窗已還原 (未最小化) 且可見
- 視窗標題必須完全匹配 (區分大小寫)
- 工具會自動啟用並還原最小化的視窗
- 點擊座標會根據視窗位置自動校準 (shift_x, shift_y)
- 使用 pygetwindow 定位視窗並使用 pyautogui 進行點擊
- 檢查視窗標題在應用程式生命週期中是否會變更

**Android 模式問題**:

- 驗證 ADB 連線: `adb devices`
- 確保目標套件目前正在裝置上執行（工具會主動檢查此項目）
- 檢查裝置是否正確連接且可存取
- 確認 host:port 組合正確 (例如："127.0.0.1:16416")
- 工具會自動偵測哪個已連接的裝置正在執行目標應用程式
- 如果多個裝置執行相同應用程式，將會引發 AdbError

**瀏覽器模式問題**:

- 安裝 Google Chrome（使用 `channel="chrome"` 的 Playwright 所需）
- 檢查目標 URL 是否可存取
- 驗證網路連線
- 工具使用具有隱身模式和反偵測功能的無頭 Chromium：
  - 自訂使用者代理
  - 停用自動化標記
  - 修改瀏覽器指紋
- 對於自訂瀏覽器，請修改 `src/auto_click/cores/screenshot.py` 中的 `channel` 參數

**圖像偵測問題**:

- 調整 `confidence` 閾值 (嘗試 0.7-0.95 之間的值)
- 更新 `./data/*` 目錄中的範本圖像
- 確保範本圖像與目前 UI 外觀相符
- 檢查圖像解析度和縮放因子
- 範本圖像應清晰且高對比度

**Discord 通知問題**:

- 驗證 `.env` 中的 `DISCORD_WEBHOOK_URL` 設定正確
- 手動測試 webhook URL 以確保其有效
- 檢查 Discord 伺服器對 webhook 的權限

### 除錯提示

- 透過檢查日誌輸出啟用詳細日誌記錄
- 使用比較工具測試單個圖像範本
- 在執行自動化之前驗證目標應用程式狀態
- 使用螢幕截圖除錯來查看工具擷取的內容

## 授權

MIT
