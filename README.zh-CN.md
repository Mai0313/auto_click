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

Auto Click 是一款功能强大的自动化工具，可以从屏幕截图中检测 UI 元素，并根据 YAML 配置文件执行自动点击。它使用 OpenCV 模板匹配进行图像识别，支持三种目标模式：Windows 桌面应用程序、通过 ADB 连接的 Android 设备，以及通过 Playwright 控制的网页浏览器。

其他语言: [English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

## 功能

- **多平台支持**:
  - **Windows 应用程序**: 通过窗口标题捕获特定窗口，并使用具备自动窗口校准功能的 `pyautogui` 执行点击
  - **Android 设备**: 通过 ADB 连接捕获并与正在运行的应用进行交互
  - **网页浏览器**: 使用 Playwright 进行自动化浏览器控制，提供隐身模式和反检测能力
- **高级图像识别**:
  - 使用 OpenCV 模板匹配并结合灰度转换以获得最佳性能
  - 可为每张图像配置置信度阈值以提升检测精度
  - 自动计算点击位置（匹配模板的中心点）
- **灵活配置**:
  - 通过 YAML 驱动的工作流，可为每张图像单独配置
  - 可自定义延迟、点击开关和置信度阈值
  - 支持复杂的自动化执行序列
- **智能通知**:
  - 集成 Discord Webhook，支持丰富的嵌入消息
  - 自动错误上报和任务完成提醒
  - 附带图像以便进行视觉确认
- **健壮的错误处理**:
  - 自动设备检测与连接管理
  - 优雅的失败恢复与重试机制
  - 与 Logfire 集成的全面日志记录

## 系统要求

- **Python 3.11+**（已在 3.11、3.12、3.13 上测试）
- **Windows 10+** 建议使用（执行 Windows 应用自动化所必需）
- **Google Chrome**（用于浏览器自动化，Playwright 使用 `channel="chrome"`）
- **ADB（Android Debug Bridge）**（用于 Android 自动化）
- **uv** 包管理器（用于依赖管理）

## 安装

1. **安装 uv**（如果尚未安装）：

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **克隆仓库并同步依赖**：

   ```bash
   git clone https://github.com/Mai0313/auto_click.git
   cd auto_click
   uv sync
   ```

3. **安装 Playwright 浏览器**（浏览器自动化所需）：

   ```bash
   uv run playwright install chrome
   ```

   **注意**：工具使用 `channel="chrome"` 需要已安装 Google Chrome。

4. **配置 Discord 通知**（可选）：
   在项目根目录创建 `.env` 文件：

   ```bash
   echo DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your-webhook-url" > .env
   ```

5. **验证 ADB 设置**（用于 Android 自动化）：

   ```bash
   adb devices
   ```

## 配置

Auto Click 使用 YAML 配置文件定义自动化工作流。每个配置文件都指定目标应用以及需要检测并交互的图像序列。

### Windows 应用示例

用于自动化 Windows 桌面应用（例如：雀魂麻将）：

```yaml
enable: true              # 总开关（注意：在 YAML 中使用 True/False，而非 true/false）
target: 雀魂麻将          # 精确的窗口标题（区分大小写）
host: ''                 # Windows 模式使用空字符串
serial: ''               # Windows 模式使用空字符串
image_list:
  - image_name: 开始段位
    image_path: ./data/mahjong/ranking.png
    delay_after_click: 1
    enable_click: true
    enable_screenshot: false
    confidence: 0.9
```

### Android 应用示例

用于通过 ADB 自动化 Android 应用（目标进程需已运行）：

```yaml
enable: true
target: com.longe.allstarhmt    # Android 包名（必须正在运行）
host: 127.0.0.1                # ADB 主机地址
serial: '16416'                 # ADB 端口（组合为 127.0.0.1:16416）
image_list:
  - image_name: 开始配对
    image_path: ./data/allstars/start.png
    delay_after_click: 20
    enable_click: true
    enable_screenshot: true
    confidence: 0.75
```

**重要**：工具会自动检测哪个已连接的设备正在运行目标包。

### 浏览器自动化示例

通过具有隐身模式的 Playwright 实现网页自动化：

```yaml
enable: true
target: https://example.com     # 目标 URL（将在 Chrome 中打开）
host: ''                        # 浏览器模式使用空字符串
serial: ''                      # 浏览器模式使用空字符串
image_list:
  - image_name: Login Button
    image_path: ./data/browser/login.png
    delay_after_click: 3
    enable_click: true
    enable_screenshot: false
    confidence: 0.8
```

**注意**：浏览器以无头模式运行，并启用反检测功能。

### 配置参数

| 参数                | 类型   | 说明                                             |
| ------------------- | ------ | ------------------------------------------------ |
| `enable`            | bool   | 自动化的总开关                                   |
| `target`            | string | 窗口标题、包名或 URL                             |
| `host`              | string | ADB 主机地址（Android 模式需与 serial 一起使用） |
| `serial`            | string | ADB 端口（Android 模式需与 host 一起使用）       |
| `image_name`        | string | 图像的描述性名称                                 |
| `image_path`        | string | 模板图像文件路径                                 |
| `delay_after_click` | int    | 点击后的等待秒数                                 |
| `enable_click`      | bool   | 找到图像时是否执行点击                           |
| `enable_screenshot` | bool   | 预留字段，供后续使用                             |
| `confidence`        | float  | 匹配阈值（0.0-1.0，值越高越严格）                |

### 重要说明

- 在 Android 模式下：`host` 和 `serial` 必须同时提供或同时留空
- 窗口标题必须完全匹配（区分大小写）
- 模板图像应清晰且具有高对比度
- 通常将置信度设定在 0.7-0.95 之间可以获得可靠检测
- 点击位置会自动计算为匹配模板的中心点

## 使用方法

### 运行 Auto Click

通过指定配置文件执行自动化：

```bash
# 使用 auto_click 命令（推荐）
uv run auto_click --config_path=./configs/games/mahjong.yaml

# 替代方案：使用 CLI 脚本名称
uv run cli --config_path=./configs/games/all_stars.yaml

# 直接使用 Python 模块
uv run python -m auto_click.cli --config_path=./configs/games/league.yaml

# 使用默认配置文件 (./configs/games/all_stars.yaml)
uv run auto_click

# 在 Windows 上使用 start.bat
start.bat
```

**注意**：CLI 使用 Python Fire，因此请使用 `--config_path=<路径>` 或 `--config_path <路径>` 语法。

### 工作原理

1. **初始化**：加载 YAML 配置并建立与目标的连接
   - Android 模式：通过 ADB 连接并验证目标应用是否正在运行
   - Windows 模式：通过精确标题定位窗口并计算位置偏移
   - 浏览器模式：启动具有反检测隐身模式的 Chromium
2. **截图采集**：依据目标模式定期获取屏幕截图
   - Windows：捕获特定窗口区域并自动校准位置
   - Android：使用 ADB screencap 命令
   - 浏览器：使用 Playwright 截图 API
3. **图像检测**：使用 OpenCV 模板匹配结合灰度转换寻找 UI 元素
4. **执行操作**：按照配置的延迟点击检测到的元素
   - Windows：使用 pyautogui 配合校准后的坐标 (shift_x, shift_y)
   - Android：使用 ADB input tap 命令
   - 浏览器：使用 Playwright 鼠标点击 API
5. **通知推送**：在完成或出错时发送 Discord Webhook 更新并附带嵌入图像
6. **循环执行**：重复上述步骤直到任务完成或出现错误

### 现成配置

项目提供若干预设的自动化示例：

- `configs/games/mahjong.yaml` - 雀魂麻将自动化
- `configs/games/all_stars.yaml` - All Stars 游戏自动化
- `configs/games/league.yaml` - League 游戏自动化

## 故障排查

### 常见问题

**窗口模式问题**：

- 确保目标窗口已恢复（未最小化）并且可见
- 窗口标题必须完全匹配（区分大小写）
- 工具会自动激活并恢复最小化的窗口
- 点击坐标会根据窗口位置自动校准 (shift_x, shift_y)
- 使用 pygetwindow 定位窗口并使用 pyautogui 进行点击
- 检查应用在生命周期中是否会改变窗口标题

**Android 模式问题**：

- 通过 `adb devices` 检查 ADB 连接
- 确保目标包当前正在设备上运行（工具会主动检查此项）
- 检查设备是否连接正确且可访问
- 确认 host:port 组合正确（例如："127.0.0.1:16416"）
- 工具会自动检测哪个已连接的设备正在运行目标应用
- 如果多个设备运行相同应用，将会抛出 AdbError

**浏览器模式问题**：

- 安装 Google Chrome（使用 `channel="chrome"` 的 Playwright 依赖）
- 检查目标 URL 是否可访问
- 确认网络连接正常
- 工具使用带有隐身模式和反检测功能的无头 Chromium：
  - 自定义用户代理
  - 禁用自动化标志
  - 修改浏览器指纹
- 如需自定义浏览器，在 `src/auto_click/cores/screenshot.py` 中修改 `channel` 参数

**图像检测问题**：

- 调整 `confidence` 阈值（建议尝试 0.7-0.95）
- 更新 `./data/*` 目录中的模板图像
- 确保模板图像与当前 UI 外观保持一致
- 检查图像分辨率与缩放比例
- 模板图像应清晰且高对比度

**Discord 通知问题**：

- 确认 `.env` 中的 `DISCORD_WEBHOOK_URL` 设置正确
- 手动测试 webhook URL 以保证其有效
- 检查 Discord 服务器对该 webhook 的权限

### 调试建议

- 查看日志输出以启用详细日志记录
- 使用对比工具测试单独的模板图像
- 在运行自动化前确认目标应用状态
- 借助截图调试查看工具捕获的画面

## 许可证

MIT
