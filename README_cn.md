### Auto Click

[![python](https://img.shields.io/badge/-Python_3.10_%7C_3.11_%7C_3.12-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![uv](https://img.shields.io/badge/-uv_dependency_management-2C5F2D?logo=python&logoColor=white)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![tests](https://github.com/Mai0313/auto_click/actions/workflows/test.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/test.yml)
[![code-quality](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Mai0313/auto_click/actions/workflows/code-quality-check.yml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/Mai0313/auto_click/tree/master?tab=License-1-ov-file)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Mai0313/auto_click/pulls)
[![contributors](https://img.shields.io/github/contributors/Mai0313/auto_click.svg)](https://github.com/Mai0313/auto_click/graphs/contributors)

Auto Click 是一個功能強大的自動化工具，通過屏幕截圖檢測界面元素並根據 YAML 配置文件執行自動點擊。它使用 OpenCV 模板匹配進行圖像識別，支持三種目標模式：Windows 桌面應用程序、通過 ADB 連接的 Android 設備，以及使用 Playwright 的網頁瀏覽器。

## 功能特色

- **多平台支持**：
  - **Windows 應用程序**：通過窗口標題捕獲特定窗口並使用 `pyautogui` 進行自動窗口校準點擊
  - **Android 設備**：通過 ADB 連接以捕獲並與運行中的應用程序交互
  - **網頁瀏覽器**：使用 Playwright 進行自動化瀏覽器控制，具備隱身模式和反檢測功能
- **先進圖像識別**：
  - OpenCV 模板匹配配合灰度轉換以達到最佳性能
  - 每張圖片可配置置信度閾值以實現精確檢測
  - 自動計算點擊位置（匹配模板的中心點）
- **靈活配置**：
  - YAML 驅動的工作流程，包含每張圖片的個別配置
  - 可自定義延遲時間、點擊啟用狀態和置信度水平
  - 支持複雜的自動化序列
- **智能通知**：
  - Discord Webhook 集成，具備豐富的嵌入消息
  - 自動錯誤報告和任務完成提醒
  - 支持圖片附件以進行視覺確認
- **穩健的錯誤處理**：
  - 自動設備檢測和連接管理
  - 優雅的故障恢復機制和重試邏輯
  - 集成 Logfire 的完整日志記錄

## 系統需求

- **Python 3.10+**（已測試 3.10、3.11、3.12）
- **Windows 10+** 建議（Windows 應用程式自動化需要）
- **Google Chrome** 用於瀏覽器自動化（Playwright 使用 `channel="chrome"`）
- **ADB（Android Debug Bridge）** 用於 Android 裝置自動化
- **uv** 套件管理工具進行依賴管理

## 安裝步驟

1) **安裝 uv**（如果尚未安裝）：
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2) **複製專案並同步依賴**：
   ```bash
   git clone <repository-url>
   cd auto_click_dev
   uv sync
   ```

3) **安裝 Playwright 瀏覽器**（可選，用於瀏覽器自動化）：
   ```bash
   uv run playwright install chromium
   ```

4) **設定 Discord 通知**（可選）：
   在專案根目錄建立 `.env` 檔案：
   ```bash
   echo DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your-webhook-url" > .env
   ```

5) **驗證 ADB 設定**（用於 Android 自動化）：
   ```bash
   adb devices
   ```

## 配置說明

Auto Click 使用 YAML 配置檔案來定義自動化工作流程。每個配置檔案指定目標應用程式和要偵測並互動的圖像序列。

### Windows 應用程式範例
用於自動化 Windows 桌面應用程式（例如：雀魂麻將）：

```yaml
enable: true
target: "雀魂麻将"        # 確切的視窗標題
host: ""                 # Windows 模式留空
serial: ""               # Windows 模式留空
image_list:
  - image_name: "開始段位"
    image_path: "./data/mahjong/ranking.png"
    delay_after_click: 1
    enable_click: true
    enable_screenshot: false
    confidence: 0.9
```

### Android 應用程式範例
用於透過 ADB 自動化 Android 應用程式（套件必須正在運行）：

```yaml
enable: true
target: com.longe.allstarhmt    # Android 套件名稱
host: "127.0.0.1"              # ADB 主機
serial: "16416"                 # ADB 端口（組成 127.0.0.1:16416）
image_list:
  - image_name: "開始配對"
    image_path: "./data/allstars/start.png"
    delay_after_click: 20
    enable_click: true
    enable_screenshot: true
    confidence: 0.75
```

### 瀏覽器自動化範例
使用 Playwright 進行網頁自動化：

```yaml
enable: true
target: "https://example.com"   # 目標網址
host: ""                        # 瀏覽器模式留空
serial: ""                      # 瀏覽器模式留空
image_list:
  - image_name: "登入按鈕"
    image_path: "./data/browser/login.png"
    delay_after_click: 3
    enable_click: true
    enable_screenshot: false
    confidence: 0.8
```

### 配置參數說明

| 參數 | 類型 | 說明 |
|------|------|------|
| `enable` | bool | 自動化的主開關 |
| `target` | string | 視窗標題、套件名稱或 URL |
| `host` | string | ADB 主機（Android 模式需要與 serial 一起使用） |
| `serial` | string | ADB 端口（Android 模式需要與 host 一起使用） |
| `image_name` | string | 圖像的描述性名稱 |
| `image_path` | string | 樣板圖像檔案路徑 |
| `delay_after_click` | int | 點擊後等待的秒數 |
| `enable_click` | bool | 找到圖像時是否點擊 |
| `enable_screenshot` | bool | 保留供未來使用 |
| `confidence` | float | 比對閾值（0.0-1.0，數值越高越嚴格） |

### 重要注意事項
- Android 模式：`host` 和 `serial` 必須同時提供或同時留空
- 視窗標題必須完全相符（區分大小寫）
- 樣板圖像應該是清晰、高對比度的截圖
- 信心度值通常在 0.7-0.95 之間可實現可靠偵測
- 點擊位置會自動計算為比對樣板的中心點

## 使用方式

### 執行 Auto Click

使用特定配置檔案執行自動化：

```bash
# 直接使用 CLI 模組
uv run python src/auto_click/cli.py --config_path=./configs/games/mahjong.yaml

# 使用已安裝的腳本
uv run auto_click --config_path=./configs/games/all_stars.yaml

# 執行聯盟自動化
uv run auto_click --config_path=./configs/games/league.yaml
```

### 工作原理

1. **初始化**：載入 YAML 配置並建立目標連接
2. **截圖擷取**：根據目標模式定期擷取截圖
3. **圖像偵測**：使用 OpenCV 樣板比對尋找介面元素
4. **動作執行**：點擊偵測到的元素並按指定延遲等待
5. **通知發送**：在完成或發生錯誤時傳送 Discord 更新
6. **循環繼續**：重複執行直到任務完成或發生錯誤

### 可用配置

專案包含數個預配置的自動化範例：

- `configs/games/mahjong.yaml` - 雀魂麻將自動化
- `configs/games/all_stars.yaml` - All Stars 遊戲自動化
- `configs/games/league.yaml` - 聯盟遊戲自動化

## 疑難排解

### 常見問題

**視窗模式問題**：
- 確保目標視窗已還原（未最小化）且可見
- 視窗標題必須完全相符（區分大小寫）
- 視窗應為作用中/聚焦的視窗
- 檢查視窗標題是否在應用程式生命週期中有變化

**Android 模式問題**：
- 驗證 ADB 連接：`adb devices`
- 確保目標套件目前正在裝置上運行
- 檢查裝置是否正確連接且可存取
- 確認主機:端口組合正確（例如："127.0.0.1:16416"）

**瀏覽器模式問題**：
- 安裝 Google Chrome（Playwright 需要）
- 檢查目標 URL 是否可存取
- 驗證網路連接
- 若要使用自訂瀏覽器，請修改 `cores/screenshot.py` 中的 `channel` 參數

**圖像偵測問題**：
- 調整 `confidence` 閾值（嘗試 0.7-0.95 之間的值）
- 更新 `./data/*` 目錄中的樣板圖像
- 確保樣板圖像與當前介面外觀相符
- 檢查圖像解析度和縮放因子
- 樣板圖像應清晰且具有高對比度

**Discord 通知問題**：
- 驗證 `.env` 中的 `DISCORD_WEBHOOK_URL` 設定正確
- 手動測試 webhook URL 確保其有效
- 檢查 Discord 伺服器對該 webhook 的權限

### 除錯提示

- 透過檢查日誌輸出啟用詳細日誌記錄
- 使用比較工具測試個別圖像樣板
- 在執行自動化前驗證目標應用程式狀態
- 使用截圖除錯功能查看工具擷取的內容

## 授權

MIT
