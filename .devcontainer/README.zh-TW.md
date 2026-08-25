# Python 專案 Dev Container 說明

本目錄提供 VS Code Dev Container 的設定，讓你在一致且可重現的環境中開發此專案。

## 內容說明

這裡沒有 Dockerfile。環境是由官方 image 加上 [Dev Container Features](https://containers.dev/features) 組成的，image 更小，也免除了手寫 Dockerfile 得自己盯著 base image tag 的維護成本。

- **Base image**：`python:3.11-slim`，與 `.python-version` 一致。
- **Features**：
  - `common-utils`：git、curl、zsh 與 oh-my-zsh，預設 shell 為 zsh。`username` 設為 `none`，因此容器維持以 `root` 執行，與先前行為相同。
  - `uv`：`Makefile` 與 CI 依賴的 Python 套件管理工具。
- **devcontainer.json**：沿用本專案原有的擴充套件建議清單，並設定 zsh 終端機。
- **updateContentCommand**：執行 `uv sync && uv cache clean`，容器開啟時虛擬環境已經備妥。

## Git 與 SSH

這裡沒有掛載任何 git 或 SSH 相關檔案，也不需要。VS Code Dev Containers 會自動把本機的 `.gitconfig` 複製進容器，並轉發本機的 SSH agent，因此透過 SSH `git push` 可以正常運作，而私鑰始終留在本機。GitHub Codespaces 也有等效的機制。

## 個人 shell 設定

容器裡只有一份原始的 oh-my-zsh。提示字元主題、外掛與 alias 屬於個人偏好而非專案設定，所以刻意不寫進這裡。

若想讓你自己的設定出現在每個開啟的容器中，在 VS Code 設定中填一次 `dotfiles.repository`，或到 [GitHub Settings > Codespaces](https://github.com/settings/codespaces) 開啟 **Automatically install dotfiles**。兩者都是個人層級的設定，對所有你建立的容器生效，也不會影響其他在這個專案工作的人。

## 使用方式

1. 以 VS Code 開啟本資料夾並安裝 Dev Containers 擴充套件。
2. 執行「Dev Containers: Reopen in Container」。

## 自訂化

- **更換 Python 版本**：修改 `image` 的 tag，並同步更新 `.python-version`。
- **新增工具**：優先從 [containers.dev/features](https://containers.dev/features) 找 feature，而不是重新引入 Dockerfile。
- **新增 VS Code 擴充套件**：修改 `devcontainer.json` 的 `extensions` 清單。

## 疑難排解

- **修改 `devcontainer.json` 之後**：執行「Dev Containers: Rebuild Container」。
- **SSH 金鑰無法使用**：確認本機的 ssh-agent 有在執行，且 `ssh-add -l` 列得出你的金鑰。容器本身不持有任何金鑰。
- 更多細節請見 [VS Code Dev Containers 文件](https://code.visualstudio.com/docs/devcontainers/containers)。
