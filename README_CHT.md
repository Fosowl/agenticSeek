# AgenticSeek：私有、本地的 Manus 替代方案

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek Logo">
<p>

  English | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md) | [Español](./README_ES.md) | [Türkçe](./README_TR.md)

*一個**100%本地運行的 Manus AI 替代品**，支援語音的 AI 助手，可自主瀏覽網頁、編寫代碼、規劃任務，所有數據僅保存在你的設備上。專為本地推理模型設計，完全在你的硬件上運行，確保隱私無憂，無需雲端依賴。*

[![訪問 AgenticSeek](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460) [![GitHub stars](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### 為什麼選擇 AgenticSeek？

* 🔒 完全本地 & 私有 —— 所有內容都在你的電腦上運行，無雲端、無數據共享。你的文件、對話和搜索都保持私密。

* 🌐 智能網頁瀏覽 —— AgenticSeek 可自主瀏覽互聯網：搜索、閱讀、提取信息、填寫網頁表單，全程免手動。

* 💻 自動化編程助手 —— 需要代碼？它能編寫、調試並運行 Python、C、Go、Java 等程序，無需監督。

* 🧠 智能代理選擇 —— 你提問，它自動判斷最合適的代理來完成任務。就像有一支專家團隊隨時待命。

* 📋 規劃並執行複雜任務 —— 從旅行規劃到複雜項目，可將大任務拆分為步驟，調用多個 AI 代理協作完成。

* 🎙️ 語音支持 —— 乾淨、快速、未來感的語音與語音轉文本功能，讓你像科幻電影中的 AI 一樣與它對話。（開發中）

### **演示**

> *你能搜索 agenticSeek 項目，了解需要哪些技能，然後打開 CV_candidates.zip 並告訴我哪些最匹配該項目嗎？*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

免責聲明：本演示及出現的所有文件（如 CV_candidates.zip）均為虛構。我們不是公司，只尋求開源貢獻者而非候選人。

> 🛠⚠️️ **項目正在積極開發中**

> 🙏 本項目起初只是一個副業，沒有路線圖也沒有資金支持。它意外地登上了 GitHub Trending。非常感謝大家的貢獻、反饋與耐心。

## 前置條件

開始前，請確保已安裝以下軟件：

*   **Git:** 用於克隆倉庫。[下載 Git](https://git-scm.com/downloads)
*   **Python 3.10.x:** 強烈推薦使用 Python 3.10.x 版本。使用其他版本可能導致依賴錯誤。[下載 Python 3.10](https://www.python.org/downloads/release/python-3100/)（選擇 3.10.x 版本）。
*   **Docker Engine & Docker Compose:** 用於運行捆綁服務如 SearxNG。
    *   安裝 Docker Desktop（包含 Docker Compose V2）：[Windows](https://docs.docker.com/desktop/install/windows-install/) | [Mac](https://docs.docker.com/desktop/install/mac-install/) | [Linux](https://docs.docker.com/desktop/install/linux-install/)
    *   或者在 Linux 上分別安裝 Docker Engine 和 Docker Compose：[Docker Engine](https://docs.docker.com/engine/install/) | [Docker Compose](https://docs.docker.com/compose/install/)（確保安裝 Compose V2，例如 `sudo apt-get install docker-compose-plugin`）。

### 1. **克隆倉庫並設置**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2. 修改 .env 文件內容

```sh
SEARXNG_BASE_URL="http://searxng:8080" # 如果在主機上運行 CLI 模式，使用 http://127.0.0.1:8080
REDIS_BASE_URL="redis://redis:6379/0"
WORK_DIR="/Users/mlg/Documents/workspace_for_ai"
OLLAMA_PORT="11434"
LM_STUDIO_PORT="1234"
CUSTOM_ADDITIONAL_LLM_PORT="11435"
OPENAI_API_KEY='optional'
DEEPSEEK_API_KEY='optional'
OPENROUTER_API_KEY='optional'
TOGETHER_API_KEY='optional'
GOOGLE_API_KEY='optional'
ANTHROPIC_API_KEY='optional'
```

根據需要更新 `.env` 文件：

- **SEARXNG_BASE_URL**: 除非在主機上運行 CLI 模式，否則保持不變。
- **REDIS_BASE_URL**: 保持不變 
- **WORK_DIR**: 本地工作目錄路徑。AgenticSeek 可讀取和操作這些文件。
- **OLLAMA_PORT**: Ollama 服務端口號。
- **LM_STUDIO_PORT**: LM Studio 服務端口號。
- **CUSTOM_ADDITIONAL_LLM_PORT**: 任何額外自定義 LLM 服務的端口。

**API 密鑰對於選擇本地運行 LLM 的用戶完全可選，這也是本項目的主要目的。如果硬件足夠，請留空。**

### 3. **啟動 Docker**

確保 Docker 已安裝並在系統上運行。可以使用以下命令啟動 Docker：

- **Linux/macOS:**  
    打開終端運行：
    ```sh
    sudo systemctl start docker
    ```
    或者如果已安裝，從應用程序菜單啟動 Docker Desktop。

- **Windows:**  
    從開始菜單啟動 Docker Desktop。

可以通過執行以下命令驗證 Docker 是否運行：
```sh
docker info
```
如果看到 Docker 安裝信息，則表示運行正常。

請參閱下面的[本地提供商列表](#本地提供商列表)了解摘要。

下一步：[本地運行 AgenticSeek](#啟動服務並運行)

*如果遇到問題，請參閱[故障排除](#故障排除)部分。*
*如果硬件無法本地運行 LLM，請參閱[使用 API 運行設置](#使用-api-運行設置)。*
*有關詳細 `config.ini` 說明，請參閱[配置部分](#配置)。*

---

## 在您的機器上本地運行 LLM 的設置

**硬件要求：**

要本地運行 LLM，您需要足夠的硬件。至少需要能夠運行 Magistral、Qwen 或 Deepseek 14B 的 GPU。有關詳細的模型/性能建議，請參閱 FAQ。

**設置您的本地提供商**  

啟動您的本地提供商，例如使用 ollama：

```sh
ollama serve
```

請參閱下面的本地支持提供商列表。

**更新 config.ini**

更改 config.ini 文件，將 provider_name 設置為支持的提供商，provider_model 設置為您的提供商支持的 LLM。我們推薦推理模型，如 *Magistral* 或 *Deepseek*。

有關所需硬件，請參閱 README 末尾的 **FAQ**。

```sh
[MAIN]
is_local = True # 無論您是本地運行還是使用遠程提供商。
provider_name = ollama # 或 lm-studio、openai 等。
provider_model = deepseek-r1:14b # 選擇適合您硬件的模型
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # 您的 AI 名稱
recover_last_session = True # 是否恢復上一個會話
save_session = True # 是否記住當前會話
speak = False # 文本轉語音
listen = False # 語音轉文本，僅限 CLI，實驗性
jarvis_personality = False # 是否使用更"Jarvis"風格的性格（實驗性）
languages = en zh # 語言列表，文本轉語音將默認使用列表中的第一種語言
[BROWSER]
headless_browser = True # 除非在主機上使用 CLI，否則保持不變。
stealth_mode = True # 使用不可檢測的 selenium 減少瀏覽器檢測
```

**警告**：

- `config.ini` 文件格式不支持註釋。
不要直接複製粘貼示例配置，因為註釋會導致錯誤。相反，手動修改 `config.ini` 文件，使用您所需的設置，排除任何註釋。

- 如果使用 LM-studio 運行 LLM，請*不要*將 provider_name 設置為 `openai`。將其設置為 `lm-studio`。

- 某些提供商（例如：lm-studio）要求您在 IP 前加上 `http://`。例如 `http://127.0.0.1:1234`

**本地提供商列表**

| 提供商  | 本地？ | 描述                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | 是    | 使用 ollama 作為 LLM 提供商輕鬆本地運行 LLM |
| lm-studio  | 是    | 使用 LM studio 本地運行 LLM（將 `provider_name` 設置為 `lm-studio`）|
| openai    | 是     |  使用 openai 兼容 API（例如：llama.cpp 服務器）  |

下一步：[啟動服務並運行 AgenticSeek](#啟動服務並運行)  

*如果遇到問題，請參閱[故障排除](#故障排除)部分。*
*如果硬件無法本地運行 LLM，請參閱[使用 API 運行設置](#使用-api-運行設置)。*
*有關詳細 `config.ini` 說明，請參閱[配置部分](#配置)。*

## 使用 API 運行設置

此設置使用外部、基於雲的 LLM 提供商。您需要從所選服務獲取 API 密鑰。

**1. 選擇 API 提供商並獲取 API 密鑰：**

請參閱下面的[API 提供商列表](#api-提供商列表)。訪問他們的網站註冊並獲取 API 密鑰。

**2. 將您的 API 密鑰設置為環境變量：**

*   **Linux/macOS:**
    打開終端並使用 `export` 命令。最好將其添加到 shell 的配置文件中（例如 `~/.bashrc`、`~/.zshrc`）以保持持久性。
    ```sh
    export PROVIDER_API_KEY="your_api_key_here" 
    # 將 PROVIDER_API_KEY 替換為特定的變量名，例如 OPENAI_API_KEY、GOOGLE_API_KEY
    ```
    TogetherAI 示例：
    ```sh
    export TOGETHER_API_KEY="xxxxxxxxxxxxxxxxxxxxxx"
    ```
*   **Windows:**
    *   **命令提示符（當前會話臨時）：**
        ```cmd
        set PROVIDER_API_KEY=your_api_key_here
        ```
    *   **PowerShell（當前會話臨時）：**
        ```powershell
        $env:PROVIDER_API_KEY="your_api_key_here"
        ```
    *   **永久性：** 在 Windows 搜索欄中搜索"環境變量"，點擊"編輯系統環境變量"，然後點擊"環境變量..."按鈕。添加一個新的用戶變量，使用適當的名稱（例如 `OPENAI_API_KEY`）和您的密鑰作為值。

    *(有關更多詳細信息，請參閱 FAQ：[如何設置 API 密鑰？](#如何設置-api-密鑰))。*


**3. 更新 `config.ini`：**
```ini
[MAIN]
is_local = False
provider_name = openai # 或 google、deepseek、togetherAI、huggingface
provider_model = gpt-3.5-turbo # 或 gemini-1.5-flash、deepseek-chat、mistralai/Mixtral-8x7B-Instruct-v0.1 等。
provider_server_address = # 當 is_local = False 時，對於大多數 API 通常被忽略或可以留空
# ... 其他設置 ...
```
*警告：* 確保 `config.ini` 值中沒有尾隨空格。

**API 提供商列表**

| 提供商     | `provider_name` | 本地？ | 描述                                       | API 密鑰鏈接（示例）                     |
|--------------|-----------------|--------|---------------------------------------------------|---------------------------------------------|
| OpenAI       | `openai`        | 否     | 通過 OpenAI 的 API 使用 ChatGPT 模型。              | [platform.openai.com/signup](https://platform.openai.com/signup) |
| Google Gemini| `google`        | 否     | 通過 Google AI Studio 使用 Google Gemini 模型。    | [aistudio.google.com/keys](https://aistudio.google.com/keys) |
| Deepseek     | `deepseek`      | 否     | 通過他們的 API 使用 Deepseek 模型。                | [platform.deepseek.com](https://platform.deepseek.com) |
| Hugging Face | `huggingface`   | 否     | 使用 Hugging Face Inference API 中的模型。       | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| TogetherAI   | `togetherAI`    | 否     | 通過 TogetherAI API 使用各種開源模型。| [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) |
| OpenRouter   | `openrouter`    | No     | 通过 OpenRouter 使用各种开源模型| [https://openrouter.ai/](https://openrouter.ai/) |

*注意：*
*   我們不建議將 `gpt-4o` 或其他 OpenAI 模型用於複雜的網頁瀏覽和任務規劃，因為當前的提示優化針對 Deepseek 等模型。
*   編碼/bash 任務可能會遇到 Gemini 的問題，因為它可能不嚴格遵循針對 Deepseek 優化的格式化提示。
*   當 `is_local = False` 時，`config.ini` 中的 `provider_server_address` 通常不使用，因為 API 端點通常在相應提供商的庫中硬編碼。

下一步：[啟動服務並運行 AgenticSeek](#啟動服務並運行)

*如果遇到問題，請參閱**已知問題**部分*

*有關詳細配置文件說明，請參閱**配置**部分。*

---

## 啟動服務並運行

默認情況下，AgenticSeek 完全在 Docker 中運行。

**選項 1:** 在 Docker 中運行，使用 Web 界面：

啟動所需服務。這將啟動 docker-compose.yml 中的所有服務，包括：
    - searxng
    - redis（searxng 所需）
    - frontend
    - backend（如果使用 Web 界面時使用 `full`）

```sh
./start_services.sh full # MacOS
start start_services.cmd full # Windows
```

**警告：** 此步驟將下載並加載所有 Docker 鏡像，可能需要長達 30 分鐘。啟動服務後，請等待後端服務完全運行（您應該在日誌中看到 **backend: "GET /health HTTP/1.1" 200 OK**）後再發送任何消息。首次運行時，後端服務可能需要 5 分鐘才能啟動。

轉到 `http://localhost:3000/`，您應該會看到 Web 界面。

*服務啟動故障排除：* 如果這些腳本失敗，請確保 Docker Engine 正在運行並且 Docker Compose（V2，`docker compose`）已正確安裝。檢查終端輸出中的錯誤消息。請參閱 [FAQ：幫助！運行 AgenticSeek 或其腳本時出現錯誤。](#faq-故障排除)

**選項 2:** CLI 模式：

要使用 CLI 界面運行，您必須在主機上安裝軟件包：

```sh
./install.sh
./install.bat # windows
```

然後您必須將 `config.ini` 中的 SEARXNG_BASE_URL 更改為：

```sh
SEARXNG_BASE_URL="http://localhost:8080"
```

啟動所需服務。這將啟動 docker-compose.yml 中的一些服務，包括：
    - searxng
    - redis（searxng 所需）
    - frontend

```sh
./start_services.sh # MacOS
start start_services.cmd # Windows
```

運行：uv run: `uv run python -m ensurepip` 以確保 uv 已啟用 pip。

使用 CLI：`uv run cli.py`

---

## 使用方法

確保服務已通過 `./start_services.sh full` 啟動並運行，然後轉到 `localhost:3000` 使用 Web 界面。

您也可以通過設置 `listen = True` 來使用語音轉文本。僅限 CLI 模式。

要退出，只需說/輸入 `goodbye`。

以下是一些使用示例：

> *用 python 寫一個貪吃蛇遊戲！*

> *搜索法國雷恩的最佳咖啡館，並將三家及其地址保存到 rennes_cafes.txt。*

> *寫一個 Go 程序計算階乘，保存為 factorial.go 到你的工作區*

> *在 summer_pictures 文件夾中查找所有 JPG 文件，用今天日期重命名，並將重命名文件列表保存到 photos_list.txt*

> *在線搜索 2024 年熱門科幻電影，挑選三部今晚觀看，保存到 movie_night.txt。*

> *搜索 2025 年最新 AI 新聞文章，選三篇，寫 Python 腳本抓取標題和摘要，腳本保存為 news_scraper.py，摘要保存到 ai_news.txt（/home/projects）*

> *周五，搜索免費股票價格 API，用 supersuper7434567@gmail.com 註冊，然後寫 Python 腳本每日獲取特斯拉股價，結果保存到 stock_prices.csv*

*請注意，表單填寫功能仍為實驗性，可能失敗。*

輸入查詢後，AgenticSeek 將分配最佳代理執行任務。

由於這是早期原型，代理路由系統可能無法總是根據您的查詢分配正確的代理。

因此，您應該非常明確地表達您想要什麼以及 AI 可能如何進行，例如如果您希望它進行網頁搜索，不要說：

`你知道哪些適合獨自旅行的國家嗎？`

而應說：

`進行網頁搜索，找出最適合獨自旅行的國家`

---

## **在自己的服務器上運行 LLM 的設置**  

如果您有功能強大的計算機或可以使用的服務器，但想從筆記本電腦使用它，您可以選擇使用我們的自定義 llm 服務器在遠程服務器上運行 LLM。

在將運行 AI 模型的"服務器"上，獲取 IP 地址

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # 本地 IP
curl https://ipinfo.io/ip # 公共 IP
```

注意：對於 Windows 或 macOS，分別使用 ipconfig 或 ifconfig 查找 IP 地址。

克隆倉庫並進入 `server/` 文件夾。

```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/llm_server/
```

安裝服務器特定要求：

```sh
pip3 install -r requirements.txt
```

運行服務器腳本。

```sh
python3 app.py --provider ollama --port 3333
```

您可以選擇使用 `ollama` 和 `llamacpp` 作為 LLM 服務。

現在在您的個人計算機上：

更改 `config.ini` 文件，將 `provider_name` 設置為 `server`，`provider_model` 設置為 `deepseek-r1:xxb`。
將 `provider_server_address` 設置為將運行模型的機器的 IP 地址。

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = http://x.x.x.x:3333
```

下一步：[啟動服務並運行 AgenticSeek](#啟動服務並運行)  

---

## 語音轉文本

警告：目前語音轉文本僅適用於 CLI 模式。

請注意，目前語音轉文本僅適用於英語。

語音轉文本功能默認禁用。要啟用它，請在 config.ini 文件中將 listen 選項設置為 True：

```
listen = True
```

啟用後，語音轉文本功能會監聽觸發關鍵字，即代理的名稱，然後開始處理您的輸入。您可以通過更新 *config.ini* 文件中的 `agent_name` 值來自定義代理的名稱：

```
agent_name = Friday
```

為了獲得最佳識別效果，我們建議使用常見的英文名稱，如 "John" 或 "Emma" 作為代理名稱。

一旦您看到轉錄開始出現，請大聲說出代理的名稱以喚醒它（例如，"Friday"）。

清晰地說出您的查詢。

用確認短語結束您的請求，以指示系統繼續。確認短語的示例包括：
```
"do it", "go ahead", "execute", "run", "start", "thanks", "would ya", "please", "okay?", "proceed", "continue", "go on", "do that", "go it", "do you understand?"
```

## 配置

配置示例：
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = http://127.0.0.1:11434 # Ollama 示例；LM-Studio 使用 http://127.0.0.1:1234
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False

jarvis_personality = False
languages = en zh # TTS 和潛在路由的語言列表。
[BROWSER]
headless_browser = False
stealth_mode = False
```

**`config.ini` 設置說明**：

*   **`[MAIN]` 部分：**
    *   `is_local`: 如果使用本地 LLM 提供商（Ollama、LM-Studio、本地 OpenAI 兼容服務器）或自託管服務器選項，則為 `True`。如果使用基於雲的 API（OpenAI、Google 等），則為 `False`。
    *   `provider_name`: 指定 LLM 提供商。
        *   本地選項：`ollama`、`lm-studio`、`openai`（用於本地 OpenAI 兼容服務器）、`server`（用於自託管服務器設置）。
        *   API 選項：`openai`、`google`、`deepseek`、`huggingface`、`togetherAI`。
    *   `provider_model`: 所選提供商的特定模型名稱或 ID（例如，Ollama 的 `deepseekcoder:6.7b`，OpenAI API 的 `gpt-3.5-turbo`，TogetherAI 的 `mistralai/Mixtral-8x7B-Instruct-v0.1`）。
    *   `provider_server_address`: 您的 LLM 提供商的地址。
        *   對於本地提供商：例如，Ollama 的 `http://127.0.0.1:11434`，LM-Studio 的 `http://127.0.0.1:1234`。
        *   對於 `server` 提供商類型：您的自託管 LLM 服務器的地址（例如 `http://your_server_ip:3333`）。
        *   對於雲 API（`is_local = False`）：這通常被忽略或可以留空，因為 API 端點通常由客戶端庫處理。
    *   `agent_name`: AI 助手的名稱（例如 Friday）。如果啟用，用作語音轉文本的觸發詞。
    *   `recover_last_session`: `True` 嘗試恢復上一個會話的狀態，`False` 重新開始。
    *   `save_session`: `True` 保存當前會話的狀態以供潛在恢復，`False` 否則。
    *   `speak`: `True` 啟用文本轉語音語音輸出，`False` 禁用。
    *   `listen`: `True` 啟用語音轉文本語音輸入（僅限 CLI 模式），`False` 禁用。
    *   `work_dir`: **關鍵：** AgenticSeek 將讀取/寫入文件的目錄。**確保此路徑在您的系統上有效且可訪問。**
    *   `jarvis_personality`: `True` 使用更"Jarvis-like"的系統提示（實驗性），`False` 使用標準提示。
    *   `languages`: 逗號分隔的語言列表（例如 `en, zh, fr`）。用於 TTS 語音選擇（默認為第一個），並可以協助 LLM 路由器。為避免路由器效率低下，避免使用過多或非常相似的語言。
*   **`[BROWSER]` 部分：**
    *   `headless_browser`: `True` 在沒有可見窗口的情況下運行自動化瀏覽器（推薦用於 Web 界面或非交互式使用）。`False` 顯示瀏覽器窗口（對於 CLI 模式或調試有用）。
    *   `stealth_mode`: `True` 啟用使瀏覽器自動化更難檢測的措施。可能需要手動安裝瀏覽器擴展，如 anticaptcha。

本節總結了支持的 LLM 提供商類型。在 `config.ini` 中配置它們。

**本地提供商（在您自己的硬件上運行）：**

| config.ini 中的提供商名稱 | `is_local` | 描述                                                                 | 設置部分                                                    |
|-------------------------------|------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| `ollama`                      | `True`     | 使用 Ollama 輕鬆提供本地 LLM。                                             | [在您的機器上本地運行 LLM 的設置](#在您的機器上本地運行-llm-的設置) |
| `lm-studio`                   | `True`     | 使用 LM-Studio 提供本地 LLM。                                          | [在您的機器上本地運行 LLM 的設置](#在您的機器上本地運行-llm-的設置) |
| `openai`（用於本地服務器）   | `True`     | 連接到暴露 OpenAI 兼容 API 的本地服務器（例如，llama.cpp）。 | [在您的機器上本地運行 LLM 的設置](#在您的機器上本地運行-llm-的設置) |
| `server`                      | `False`    | 連接到在另一台機器上運行的 AgenticSeek 自託管 LLM 服務器。 | [在自己的服務器上運行 LLM 的設置](#在自己的服務器上運行-llm-的設置) |

**API 提供商（基於雲）：**

| config.ini 中的提供商名稱 | `is_local` | 描述                                      | 設置部分                                       |
|-------------------------------|------------|--------------------------------------------------|-----------------------------------------------------|
| `openai`                      | `False`    | 使用 OpenAI 的官方 API（例如，GPT-3.5、GPT-4）。 | [使用 API 運行設置](#使用-api-運行設置) |
| `google`                      | `False`    | 通過 API 使用 Google 的 Gemini 模型。              | [使用 API 運行設置](#使用-api-運行設置) |
| `deepseek`                    | `False`    | 使用 Deepseek 的官方 API。                     | [使用 API 運行設置](#使用-api-運行設置) |
| `huggingface`                 | `False`    | 使用 Hugging Face Inference API。                  | [使用 API 運行設置](#使用-api-運行設置) |
| `togetherAI`                  | `False`    | 使用 TogetherAI 的 API 獲取各種開放模型。    | [使用 API 運行設置](#使用-api-運行設置) |

---
## 故障排除

如果遇到問題，本節提供指導。

# 已知問題

## ChromeDriver 問題

**錯誤示例：** `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

### 根本原因
ChromeDriver 版本不兼容發生在：
1. 您安裝的 ChromeDriver 版本與 Chrome 瀏覽器版本不匹配
2. 在 Docker 環境中，`undetected_chromedriver` 可能會下載自己的 ChromeDriver 版本，繞過掛載的二進制文件

### 解決步驟

#### 1. 檢查您的 Chrome 版本
打開 Google Chrome → `設置 > 關於 Chrome` 查找您的版本（例如，"版本 134.0.6998.88"）

#### 2. 下載匹配的 ChromeDriver

**對於 Chrome 115 及更新版本：** 使用 [Chrome for Testing API](https://googlechromelabs.github.io/chrome-for-testing/)
- 訪問 Chrome for Testing 可用性儀表板
- 找到您的 Chrome 版本或最接近的可用匹配
- 為您的操作系統下載 ChromeDriver（Docker 環境使用 Linux64）

**對於舊版 Chrome：** 使用 [舊版 ChromeDriver 下載](https://chromedriver.chromium.org/downloads)

![從 Chrome for Testing 下載 ChromeDriver](./media/chromedriver_readme.png)

#### 3. 安裝 ChromeDriver（選擇一種方法）

**方法 A：項目根目錄（Docker 推薦）**
```bash
# 將下載的 chromedriver 二進制文件放在項目根目錄
cp path/to/downloaded/chromedriver ./chromedriver
chmod +x ./chromedriver  # 在 Linux/macOS 上使其可執行
```

**方法 B：系統 PATH**
```bash
# Linux/macOS
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Windows：將 chromedriver.exe 放在 PATH 中的文件夾中
```

#### 4. 驗證安裝
```bash
# 測試 ChromeDriver 版本
./chromedriver --version
# 或者在 PATH 中：
chromedriver --version
```

### Docker 特定說明

⚠️ **Docker 用戶重要：**
- Docker 卷掛載方法可能不適用於隱身模式（`undetected_chromedriver`）
- **解決方案：** 將 ChromeDriver 放在項目根目錄中作為 `./chromedriver`
- 應用程序將自動檢測並使用此二進制文件
- 您應該在日誌中看到：`"Using ChromeDriver from project root: ./chromedriver"`

### 故障排除提示

1. **仍然遇到版本不匹配？**
   - 驗證 ChromeDriver 是否可執行：`ls -la ./chromedriver`
   - 檢查 ChromeDriver 版本：`./chromedriver --version`
   - 確保它與您的 Chrome 瀏覽器版本匹配

2. **Docker 容器問題？**
   - 檢查後端日誌：`docker logs backend`
   - 查找消息：`"Using ChromeDriver from project root"`
   - 如果未找到，請驗證文件是否存在且可執行

3. **Chrome for Testing 版本**
   - 盡可能使用完全匹配的版本
   - 對於版本 134.0.6998.88，使用 ChromeDriver 134.0.6998.165（最接近的可用版本）
   - 主要版本號必須匹配（134 = 134）

### 版本兼容性矩陣

| Chrome 版本 | ChromeDriver 版本 | 狀態 |
|----------------|---------------------|---------|
| 134.0.6998.x   | 134.0.6998.165     | ✅ 可用 |
| 133.0.6943.x   | 133.0.6943.141     | ✅ 可用 |
| 132.0.6834.x   | 132.0.6834.159     | ✅ 可用 |

*有關最新兼容性，請查看 [Chrome for Testing 儀表板](https://googlechromelabs.github.io/chrome-for-testing/)*

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

如果您的瀏覽器和 chromedriver 版本不匹配，會發生這種情況。

您需要導航到下載最新版本：

https://developer.chrome.com/docs/chromedriver/downloads

如果您使用 Chrome 版本 115 或更新版本，請轉到：

https://googlechromelabs.github.io/chrome-for-testing/

並下載與您的操作系統匹配的 chromedriver 版本。

![alt text](./media/chromedriver_readme.png)

如果此部分不完整，請提出問題。

##  連接適配器問題

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:1234/v1/chat/completions'`（注意：端口可能不同）
```

*   **原因：** `config.ini` 中 `lm-studio`（或其他類似的本地 OpenAI 兼容服務器）的 `provider_server_address` 缺少 `http://` 前綴或指向錯誤的端口。
*   **解決方案：**
    *   確保地址包含 `http://`。LM-Studio 通常默認為 `http://127.0.0.1:1234`。
    *   正確的 `config.ini`：`provider_server_address = http://127.0.0.1:1234`（或您的實際 LM-Studio 服務器端口）。

## SearxNG 基本 URL 未提供

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.`
```

如果您使用錯誤的 searxng 基本 URL 運行 CLI 模式，可能會出現這種情況。

SEARXNG_BASE_URL 應根據您是在 Docker 中運行還是在主機上運行而有所不同：

**在主機上運行**：`SEARXNG_BASE_URL="http://localhost:8080"`

**完全在 Docker 中運行（Web 界面）**：`SEARXNG_BASE_URL="http://searxng:8080"`

## FAQ

**問：我需要什麼硬件？**  

| 模型大小  | GPU  | 評論                                               |
|-----------|--------|-----------------------------------------------------------|
| 7B        | 8GB 顯存 | ⚠️ 不推薦。性能差，頻繁出現幻覺，規劃代理可能會失敗。 |
| 14B        | 12 GB VRAM（例如 RTX 3060） | ✅ 可用於簡單任務。可能在網頁瀏覽和規劃任務方面有困難。 |
| 32B        | 24+ GB VRAM（例如 RTX 4090） | 🚀 大多數任務成功，可能仍然在任務規劃方面有困難 |
| 70B+        | 48+ GB 顯存 | 💪 優秀。推薦用於高級用例。 |

**問：我遇到錯誤該怎麼辦？**  

確保本地正在運行（`ollama serve`），您的 `config.ini` 與您的提供商匹配，並且依賴項已安裝。如果都不起作用，請隨時提出問題。

**問：它真的可以 100% 本地運行嗎？**  

是的，使用 Ollama、lm-studio 或服務器提供商，所有語音轉文本、LLM 和文本轉語音模型都在本地運行。非本地選項（OpenAI 或其他 API）是可選的。

**問：當我有 Manus 時，為什麼應該使用 AgenticSeek？**

與 Manus 不同，AgenticSeek 優先考慮獨立於外部系統，給您更多控制、隱私和避免 API 成本。

**問：誰是這個項目的幕後推手？**

這個項目是由我創建的，還有兩個朋友作為維護者和 GitHub 上開源社區的貢獻者。我們只是一群充滿熱情的個人，不是初創公司，也不隸屬於任何組織。

X 上除了我的個人賬戶（https://x.com/Martin993886460）之外的任何 AgenticSeek 賬戶都是冒充的。

## 貢獻

我們正在尋找開發人員來改進 AgenticSeek！查看開放的問題或討論。

[貢獻指南](./docs/CONTRIBUTING.md)

## 贊助商：

想要通過航班搜索、旅行規劃或搶購最佳購物優惠等功能來提升 AgenticSeek 的能力？考慮使用 SerpApi 製作自定義工具，以解鎖更多 Jarvis 般的功能。使用 SerpApi，您可以為專業任務加速您的代理，同時保持完全控制。

<a href="https://serpapi.com/"><img src="./media/banners/sponsor_banner_serpapi.png" height="350" alt="SerpApi Banner" ></a>

查看 [Contributing.md](./docs/CONTRIBUTING.md) 了解如何集成自定義工具！

### **贊助商**：

- [tatra-labs](https://github.com/tatra-labs)

## 維護者：

 > [Fosowl](https://github.com/Fosowl) | 巴黎時間 

 > [antoineVIVIES](https://github.com/antoineVIVIES) | 台北時間 

## 特別感謝：

 > [tcsenpai](https://github.com/tcsenpai) 和 [plitc](https://github.com/plitc) 協助後端 Docker 化

[![Star History Chart](https://api.star-history.com/svg?repos=Fosowl/agenticSeek&type=Date)](https://www.star-history.com/#Fosowl/agenticSeek&Date)
