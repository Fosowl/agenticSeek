# AgenticSeek: Private, Local Manus Alternative.

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek Logo">
<p>

  English | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md)

*A **100% local alternative to Manus AI**, this voice-enabled AI assistant autonomously browses the web, writes code, and plans tasks while keeping all data on your device. Tailored for local reasoning models, it runs entirely on your hardware, ensuring complete privacy and zero cloud dependency.*

[![Visit AgenticSeek](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460) [![GitHub stars](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### Why AgenticSeek ?

* 🔒 Fully Local & Private - Everything runs on your machine — no cloud, no data sharing. Your files, conversations, and searches stay private.

* 🌐 Smart Web Browsing - AgenticSeek can browse the internet by itself — search, read, extract info, fill web form — all hands-free.

* 💻 Autonomous Coding Assistant - Need code? It can write, debug, and run programs in Python, C, Go, Java, and more — all without supervision.

* 🧠 Smart Agent Selection - You ask, it figures out the best agent for the job automatically. Like having a team of experts ready to help.

* 📋 Plans & Executes Complex Tasks - From trip planning to complex projects — it can split big tasks into steps and get things done using multiple AI agents.

* 🎙️ Voice-Enabled - Clean, fast, futuristic voice and speech to text allowing you to talk to it like it's your personal AI from a sci-fi movie

### **Demo**

> *Can you search for the agenticSeek project, learn what skills are required, then open the CV_candidates.zip and then tell me which match best the project*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

Disclaimer: This demo, including all the files that appear (e.g: CV_candidates.zip), are entirely fictional. We are not a corporation, we seek open-source contributors not candidates.

> 🛠⚠️️ **Active Work in Progress** – Please note that Code/Bash is not dockerized yet but will be soon (see docker_deployement branch) - Do not deploy over network or production.

> 🙏 This project started as a side-project with zero roadmap and zero funding. It's grown way beyond what I expected by ending in GitHub Trending. Contributions, feedback, and patience are deeply appreciated.

## Installation

This section guides you through installing AgenticSeek. Please follow the steps carefully.

### **Prerequisites**

Before you begin, ensure you have the following software installed:

*   **Git:** For cloning the repository. [Download Git](https://git-scm.com/downloads)
*   **Python 3.10.x:** We strongly recommend using Python version 3.10.x. Using other versions might lead to dependency errors. [Download Python 3.10](https://www.python.org/downloads/release/python-3100/) (pick a 3.10.x version).
*   **Docker Engine & Docker Compose:** For running bundled services like SearxNG.
    *   Install Docker Desktop (which includes Docker Compose V2): [Windows](https://docs.docker.com/desktop/install/windows-install/) | [Mac](https://docs.docker.com/desktop/install/mac-install/) | [Linux](https://docs.docker.com/desktop/install/linux-install/)
    *   Alternatively, install Docker Engine and Docker Compose separately on Linux: [Docker Engine](https://docs.docker.com/engine/install/) | [Docker Compose](https://docs.docker.com/compose/install/) (ensure you install Compose V2, e.g., `sudo apt-get install docker-compose-plugin`).
*   **Google Chrome:** The web browser used for autonomous browsing tasks. [Download Chrome](https://www.google.com/chrome/).
*   **ChromeDriver:** The WebDriver for Chrome. This is crucial for browser automation.
    *   **Important:** Your ChromeDriver version *must* match your installed Google Chrome version. See the [ChromeDriver Installation](#chromedriver-installation) subsection for detailed instructions.

For issues related to ChromeDriver after attempting installation, see the [Known Issues](#chromedriver-issues) section.

### 1️⃣ **Clone the repository and setup**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2️ **Create a Python Virtual Environment**

It's highly recommended to use a virtual environment to manage project dependencies.

```sh
# Ensure you are using Python 3.10 for creating the environment
python3.10 -m venv agentic_seek_env 
# Or if 'python3.10' is not found, try 'python3 -m venv agentic_seek_env' 
# but verify version with 'python --version' inside the activated environment.

# Activate the virtual environment
source agentic_seek_env/bin/activate
# On Windows PowerShell: .\agentic_seek_env\Scripts\Activate.ps1
# On Windows CMD: agentic_seek_env\Scripts\activate.bat
```

### 3️⃣ **Install Dependencies**

This step includes installing Python packages and setting up ChromeDriver.

#### **ChromeDriver Installation**

1.  **Check your Chrome Version:** Open Google Chrome, go to `Settings -> About Chrome` to find your version (e.g., 120.0.6099.110).
2.  **Download ChromeDriver:**
    *   For Chrome version 115 or newer, download from [Chrome for Testing (CfT) JSON Endpoints](https://googlechromelabs.github.io/chrome-for-testing/). Find the stable version matching your Chrome's major version.
    *   For older versions (not recommended), you might find them on the [ChromeDriver downloads page](https://chromedriver.chromium.org/downloads).
3.  **Install ChromeDriver:**
    *   **Linux/macOS:** Download the appropriate zip file, extract `chromedriver`, and move it to a directory in your system's PATH (e.g., `/usr/local/bin`). Ensure it's executable (`chmod +x /usr/local/bin/chromedriver`).
    *   **Windows:** Download the zip file, extract `chromedriver.exe`, and place it in a directory included in your system's PATH (e.g., `C:\Windows\System32` or a dedicated scripts folder that you've added to PATH).
    *   Alternatively, you can place `chromedriver` (or `chromedriver.exe`) directly in the root of the `agenticSeek` project directory. The application will try to find it there.

#### **Python Packages & System Dependencies**

**Automatic Installation (Recommended):**

The following scripts attempt to install system dependencies (like `portaudio`) and Python packages from `requirements.txt`.

*   **Linux/macOS:**
    ```sh
    ./install.sh
    ```
*   **Windows:**
    ```sh
    ./install.bat
    ```
    *Note for Windows:* The batch script will attempt to install `pyaudio`. This may require "Microsoft Visual C++ 14.0 or greater". If `pyaudio` installation fails, you might need to install it manually via a wheel file or install PortAudio first. See manual Windows instructions below.

**Manual Installation:**

If automatic installation fails or you prefer manual setup:

*   **All Operating Systems:**
    1.  Ensure your virtual environment is active.
    2.  Install Python packages:
        ```sh
        pip3 install -r requirements.txt
        ```

*   **Linux Specific System Dependencies:**
    ```sh
    sudo apt update
    sudo apt install -y alsa-utils portaudio19-dev python3-pyaudio libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1
    ```
    *(Note: `python3-pyaudio` might be handled by `pip install` if `portaudio19-dev` is present).*

*   **macOS Specific System Dependencies:**
    ```sh
    brew update
    brew install portaudio  # For pyaudio
    # ChromeDriver should be handled by the dedicated ChromeDriver Installation step above.
    # `brew install --cask chromedriver` can also work but ensure version compatibility.
    ```

*   **Windows Specific System Dependencies:**
    1.  `pip install pyreadline3` (usually part of `requirements.txt`)
    2.  **PortAudio for PyAudio:**
        *   `pyaudio` (for voice functionality) requires PortAudio. If `pip install pyaudio` (from `requirements.txt`) fails:
            *   Try installing from a pre-compiled wheel: Find a `pyaudio` wheel compatible with your Python version (3.10) and system architecture from sites like [Christoph Gohlke's Python Libraries page](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio). Download the `.whl` file and install with `pip install PyAudio‑XYZ.whl`.
            *   Alternatively, install PortAudio via a package manager like [vcpkg](https://vcpkg.io/en/index.html) or by [building from source](http://files.portaudio.com/docs/v19-doxydocs/compile_windows.html), then try `pip install pyaudio` again.

---
## Configuration (`config.ini`)

Before running AgenticSeek, you need to configure it by editing the `config.ini` file. This file is created when you run `mv .env.example .env` during the initial setup.

Key settings are explained in the [Config Section](#config) later in this README. For now, be aware that you'll need to update it based on whether you're running an LLM locally or via an API.

---

## Running AgenticSeek

Choose one of the following setups based on how you want to run the Large Language Model (LLM).

## Setup for running LLM locally on your machine

This setup allows you to run AgenticSeek with an LLM hosted entirely on your own hardware, ensuring privacy.

**Hardware Requirements:**

Running LLMs locally requires significant hardware resources. Refer to the [FAQ: What hardware do I need?](#faq) for detailed model performance and hardware recommendations (minimum 8GB VRAM GPU, 12GB+ recommended).

**1. Install a Local LLM Provider:**

You need software to serve the LLM locally. Popular choices:

*   **Ollama:**
    *   **Installation:** Download and install Ollama from [ollama.ai](https://ollama.ai/).
    *   **Homepage:** [https://ollama.ai/](https://ollama.ai/)
*   **LM-Studio:**
    *   **Installation:** Download and install LM-Studio from [lmstudio.ai](https://lmstudio.ai/).
    *   **Homepage:** [https://lmstudio.ai/](https://lmstudio.ai/)
*   **OpenAI-Compatible Server (e.g., llama.cpp, vLLM):**
    *   These are more advanced setups. You'll need to follow their respective documentation to start a server that exposes an OpenAI-compatible API.
    *   Example: [llama.cpp server documentation](https://github.com/ggerganov/llama.cpp/tree/master/examples/server)

**2. Download/Select a Model:**

Once your provider is installed, download a model. We recommend reasoning models like *Qwen* or *Deepseek*.

*   **For Ollama:**
    ```sh
    ollama pull deepseekcoder:6.7b # Example: deepseek-coder 6.7B
    ollama pull qwen:14b           # Example: Qwen 14B
    # List available models with `ollama list`
    ```
*   **For LM-Studio:** Use the UI to search for and download models.
*   **For OpenAI-Compatible Servers:** Configure the server to use your desired model.

**3. Start Your Local LLM Provider:**

*   **Ollama:**
    ```sh
    ollama serve
    ```
    (This often runs automatically after installation on some systems).
*   **LM-Studio:** Start the application and use its UI to load a model and start the server.
*   **OpenAI-Compatible Server:** Follow its specific instructions to start the server.

**4. Update `config.ini`:**

Modify your `config.ini` file:
```ini
[MAIN]
is_local = True
provider_name = ollama  # Or lm-studio, openai (for compatible local servers)
provider_model = deepseekcoder:6.7b # Or the model you downloaded/selected for your provider
provider_server_address = http://127.0.0.1:11434 # Default for Ollama. For LM-Studio, usually http://127.0.0.1:1234. Adjust if needed.
# ... other settings ...
```

*   **Important:**
    *   For `lm-studio` or other OpenAI-compatible local servers, ensure `provider_server_address` includes the `http://` prefix and the correct port.
    *   If using LM-Studio, set `provider_name = lm-studio`, not `openai`.
    *   If using a generic OpenAI-compatible local server, set `provider_name = openai`.

See the table of [Local Providers](#list-of-local-providers) below for a summary.

**Hardware Requirements:**

To run LLMs locally, you'll need sufficient hardware. At a minimum, a GPU capable of running Qwen/Deepseek 14B is required. See the FAQ for detailed model/performance recommendations.

**Setup your local provider**  

Start your local provider, for example with ollama:

```sh
ollama serve
```

See below for a list of local supported provider.

**Update the config.ini**

Change the config.ini file to set the provider_name to a supported provider and provider_model to a LLM supported by your provider. We recommand reasoning model such as *Qwen* or *Deepseek*.

See the **FAQ** at the end of the README for required hardware.

```sh
[MAIN]
is_local = True # Whenever you are running locally or with remote provider.
provider_name = ollama # or lm-studio, openai, etc..
provider_model = deepseek-r1:14b # choose a model that fit your hardware
provider_server_address = http://127.0.0.1:11434 # Default for Ollama. Use http://127.0.0.1:1234 for LM-Studio.
agent_name = Jarvis # name of your AI
recover_last_session = True # whenever to recover the previous session
save_session = True # whenever to remember the current session
speak = True # text to speech
listen = False # Speech to text, only for CLI
work_dir =  /Users/mlg/Documents/workspace # The workspace for AgenticSeek.
jarvis_personality = False # Whenever to use a more "Jarvis" like personality (experimental)
languages = en zh # The list of languages, Text to speech will default to the first language on the list
[BROWSER]
headless_browser = True # Whenever to use headless browser, recommanded only if you use web interface.
stealth_mode = True # Use undetected selenium to reduce browser detection
```

**List of local providers** (summary)

| Provider  | Local? | `provider_name` in `config.ini` | Description                                                      |
|-----------|--------|---------------------------------|------------------------------------------------------------------|
| Ollama    | Yes    | `ollama`                        | Run LLMs locally with ease using Ollama.                         |
| LM-Studio | Yes    | `lm-studio`                     | Run LLMs locally with LM-Studio's UI and server.                 |
| OpenAI Compatible API | Yes | `openai`               | Use a local server (e.g., llama.cpp, vLLM) that mimics the OpenAI API. |

Next step: [Start services and run AgenticSeek](#start-services-and-run)

*See the [Troubleshooting](#troubleshooting) section if you are having issues.*
*If your hardware can't run LLMs locally, see [Setup to run with an API](#setup-to-run-with-an-api).*
*For detailed `config.ini` explanations, see [Config Section](#config).*

---

## Setup to run with an API

This setup uses external, cloud-based LLM providers. You'll need an API key from your chosen service.

**1. Choose an API Provider and Get an API Key:**

Refer to the [List of API Providers](#list-of-api-providers) below. Visit their websites to sign up and obtain an API key.

**2. Set Your API Key as an Environment Variable:**

AgenticSeek expects the API key to be available as an environment variable.

*   **Linux/macOS:**
    Open your terminal and use the `export` command. It's best to add this to your shell's profile file (e.g., `~/.bashrc`, `~/.zshrc`) for persistence.
    ```sh
    export PROVIDER_API_KEY="your_api_key_here" 
    # Replace PROVIDER_API_KEY with the specific variable name, e.g., OPENAI_API_KEY, GOOGLE_API_KEY
    ```
    Example for TogetherAI:
    ```sh
    export TOGETHER_API_KEY="xxxxxxxxxxxxxxxxxxxxxx"
    ```
*   **Windows:**
    *   **Command Prompt (Temporary for current session):**
        ```cmd
        set PROVIDER_API_KEY=your_api_key_here
        ```
    *   **PowerShell (Temporary for current session):**
        ```powershell
        $env:PROVIDER_API_KEY="your_api_key_here"
        ```
    *   **Permanently:** Search for "environment variables" in the Windows search bar, click "Edit the system environment variables," then click the "Environment Variables..." button. Add a new User variable with the appropriate name (e.g., `OPENAI_API_KEY`) and your key as the value.

    *(See FAQ: [How do I set API keys?](#how-do-i-set-api-keys) for more details).*


**3. Update `config.ini`:**
```ini
[MAIN]
is_local = False
provider_name = openai # Or google, deepseek, togetherAI, huggingface
provider_model = gpt-3.5-turbo # Or gemini-1.5-flash, deepseek-chat, mistralai/Mixtral-8x7B-Instruct-v0.1 etc.
provider_server_address = # Typically ignored or can be left blank when is_local = False for most APIs
# ... other settings ...
```
*Warning:* Make sure there are no trailing spaces in the `config.ini` values.

**List of API Providers**

| Provider     | `provider_name` | Local? | Description                                       | API Key Link (Examples)                     |
|--------------|-----------------|--------|---------------------------------------------------|---------------------------------------------|
| OpenAI       | `openai`        | No     | Use ChatGPT models via OpenAI's API.              | [platform.openai.com/signup](https://platform.openai.com/signup) |
| Google Gemini| `google`        | No     | Use Google Gemini models via Google AI Studio.    | [aistudio.google.com/keys](https://aistudio.google.com/keys) |
| Deepseek     | `deepseek`      | No     | Use Deepseek models via their API.                | [platform.deepseek.com](https://platform.deepseek.com) |
| Hugging Face | `huggingface`   | No     | Use models from Hugging Face Inference API.       | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| TogetherAI   | `togetherAI`    | No     | Use various open-source models via TogetherAI API.| [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) |

*Note:*
*   We advise against using `gpt-4o` or other OpenAI models for complex web browsing and task planning as current prompt optimizations are geared towards models like Deepseek.
*   Coding/bash tasks might encounter issues with Gemini, as it may not strictly follow formatting prompts optimized for Deepseek.
*   The `provider_server_address` in `config.ini` is generally not used when `is_local = False` as the API endpoint is usually hardcoded in the respective provider's library.

Next step: [Start services and run AgenticSeek](#start-services-and-run)

*See the [Troubleshooting](#troubleshooting) section if you are having issues.*
*For detailed `config.ini` explanations, see [Config Section](#config).*

---

Please also note that coding/bash might fail with gemini, it seem to ignore our prompt for format to respect, which are optimized for deepseek r1.

Next step: [Start services and run AgenticSeek](#Start-services-and-Run)

*See the **Known issues** section if you are having issues*

*See the **Config** section for detailled config file explanation.*

---

## Start services and Run

Activate your Python virtual environment if it's not already active:
```sh
# Linux/macOS
source agentic_seek_env/bin/activate

# Windows PowerShell
.\agentic_seek_env\Scripts\Activate.ps1

# Windows CMD
agentic_seek_env\Scripts\activate.bat
```

Start required background services using Docker Compose. This will launch:
    - SearxNG (local meta-search engine)
    - Redis (database for SearxNG)
    - Frontend (web interface, if you choose to use it)

```sh
# For Linux (if your user is not in the docker group, sudo might be required for docker commands)
./start_services.sh 
# or if you need sudo for Docker: sudo ./start_services.sh

# For macOS (sudo is typically not required if Docker Desktop is correctly installed)
./start_services.sh

# For Windows
start ./start_services.cmd 
# This will open a new command prompt window for the services.
```
*Troubleshooting service start:* If these scripts fail, ensure Docker Engine is running and Docker Compose (V2, `docker compose`) is correctly installed. Check the output in the terminal for error messages. See [FAQ: Help! I get an error when running AgenticSeek or its scripts.](#faq-troubleshooting)

**Options 1:** Run with the CLI interface.

```sh
python3 cli.py
```

We advice you set `headless_browser` to False in the config.ini for CLI mode.

**Options 2:** Run with the Web interface.

Start the backend.

```sh
python3 api.py
```

Go to `http://localhost:3000/` and you should see the web interface.

---

## Usage

Make sure the services are up and running with `./start_services.sh` and run the AgenticSeek with `python3 cli.py` for CLI mode or `python3 api.py` then go to `localhost:3000` for web interface.

You can also use speech to text by setting `listen = True` in the config. Only for CLI mode.

To exit, simply say/type `goodbye`.

Here are some example usage:

> *Make a snake game in python!*

> *Search the web for top cafes in Rennes, France, and save a list of three with their addresses in rennes_cafes.txt.*

> *Write a Go program to calculate the factorial of a number, save it as factorial.go in your workspace*

> *Search my summer_pictures folder for all JPG files, rename them with today’s date, and save a list of renamed files in photos_list.txt*

> *Search online for popular sci-fi movies from 2024 and pick three to watch tonight. Save the list in movie_night.txt.*

> *Search the web for the latest AI news articles from 2025, select three, and write a Python script to scrape their titles and summaries. Save the script as news_scraper.py and the summaries in ai_news.txt in /home/projects*

> *Friday, search the web for a free stock price API, register with supersuper7434567@gmail.com then write a Python script to fetch using the API daily prices for Tesla, and save the results in stock_prices.csv*

*Note that form filling capabilities are still experimental and might fail.*



After you type your query, AgenticSeek will allocate the best agent for the task.

Because this is an early prototype, the agent routing system might not always allocate the right agent based on your query.

Therefore, you should be very explicit in what you want and how the AI might proceed for example if you want it to conduct a web search, do not say:

`Do you know some good countries for solo-travel?`

Instead, ask:

`Do a web search and find out which are the best country for solo-travel`

---

## **Setup to run the LLM on your own server**  

If you have a powerful computer or a server that you can use, but you want to use it from your laptop you have the options to run the LLM on a remote server using our custom llm server. 

On your "server" that will run the AI model, get the ip address

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # local ip
curl https://ipinfo.io/ip # public ip
```

Note: For Windows or macOS, use ipconfig or ifconfig respectively to find the IP address.

Clone the repository and enter the `server/`folder.


```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/llm_server/
```

Install server specific requirements:

```sh
pip3 install -r requirements.txt
```

Run the server script.

```sh
python3 app.py --provider ollama --port 3333
```

You have the choice between using `ollama` and `llamacpp` as a LLM service.


Now on your personal computer:

Change the `config.ini` file to set the `provider_name` to `server` and `provider_model` to `deepseek-r1:xxb`.
Set the `provider_server_address` to the ip address of the machine that will run the model.

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = x.x.x.x:3333
```


Next step: [Start services and run AgenticSeek](#Start-services-and-Run)  

---

## Speech to Text

Please note that currently speech to text only work in english.

The speech-to-text functionality is disabled by default. To enable it, set the listen option to True in the config.ini file:

```
listen = True
```

When enabled, the speech-to-text feature listens for a trigger keyword, which is the agent's name, before it begins processing your input. You can customize the agent's name by updating the `agent_name` value in the *config.ini* file:

```
agent_name = Friday
```

For optimal recognition, we recommend using a common English name like "John" or "Emma" as the agent name

Once you see the transcript start to appear, say the agent's name aloud to wake it up (e.g., "Friday").

Speak your query clearly.

End your request with a confirmation phrase to signal the system to proceed. Examples of confirmation phrases include:
```
"do it", "go ahead", "execute", "run", "start", "thanks", "would ya", "please", "okay?", "proceed", "continue", "go on", "do that", "go it", "do you understand?"
```

## Config

Example config:
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = http://127.0.0.1:11434 # Example for Ollama; use http://127.0.0.1:1234 for LM-Studio
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False
work_dir =  /Users/mlg/Documents/ai_folder # IMPORTANT: Update this to a valid path on your system
jarvis_personality = False
languages = en zh # List of languages for TTS and potentially routing.
[BROWSER]
headless_browser = False
stealth_mode = False
```

**Explanation of `config.ini` Settings**:

*   **`[MAIN]` Section:**
    *   `is_local`: `True` if using a local LLM provider (Ollama, LM-Studio, local OpenAI-compatible server) or the self-hosted server option. `False` if using a cloud-based API (OpenAI, Google, etc.).
    *   `provider_name`: Specifies the LLM provider.
        *   Local options: `ollama`, `lm-studio`, `openai` (for local OpenAI-compatible servers), `server` (for the self-hosted server setup).
        *   API options: `openai`, `google`, `deepseek`, `huggingface`, `togetherAI`.
    *   `provider_model`: The specific model name or ID for the chosen provider (e.g., `deepseekcoder:6.7b` for Ollama, `gpt-3.5-turbo` for OpenAI API, `mistralai/Mixtral-8x7B-Instruct-v0.1` for TogetherAI).
    *   `provider_server_address`: The address of your LLM provider.
        *   For local providers: e.g., `http://127.0.0.1:11434` for Ollama, `http://127.0.0.1:1234` for LM-Studio.
        *   For the `server` provider type: The address of your self-hosted LLM server (e.g., `http://your_server_ip:3333`).
        *   For cloud APIs (`is_local = False`): This is often ignored or can be left blank, as the API endpoint is usually handled by the client library.
    *   `agent_name`: Name of the AI assistant (e.g., Friday). Used as a trigger word for speech-to-text if enabled.
    *   `recover_last_session`: `True` to attempt to restore the previous session's state, `False` to start fresh.
    *   `save_session`: `True` to save the current session's state for potential recovery, `False` otherwise.
    *   `speak`: `True` to enable text-to-speech voice output, `False` to disable.
    *   `listen`: `True` to enable speech-to-text voice input (CLI mode only), `False` to disable.
    *   `work_dir`: **Crucial:** The directory where AgenticSeek will read/write files. **Ensure this path is valid and accessible on your system.**
    *   `jarvis_personality`: `True` to use a more "Jarvis-like" system prompt (experimental), `False` for the standard prompt.
    *   `languages`: A comma-separated list of languages (e.g., `en, zh, fr`). Used for TTS voice selection (defaults to the first) and can assist the LLM router. Avoid too many or very similar languages for router efficiency.
*   **`[BROWSER]` Section:**
    *   `headless_browser`: `True` to run the automated browser without a visible window (recommended for web interface or non-interactive use). `False` to show the browser window (useful for CLI mode or debugging).
    *   `stealth_mode`: `True` to enable measures to make browser automation harder to detect. May require manual installation of browser extensions like anticaptcha.

---
## Providers

This section summarizes the supported LLM provider types. Configure them in `config.ini`.

**Local Providers (Run on Your Own Hardware):**

| Provider Name in `config.ini` | `is_local` | Description                                                                 | Setup Section                                                    |
|-------------------------------|------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| `ollama`                      | `True`     | Use Ollama to serve local LLMs.                                             | [Setup for running LLM locally](#setup-for-running-llm-locally-on-your-machine) |
| `lm-studio`                   | `True`     | Use LM-Studio to serve local LLMs.                                          | [Setup for running LLM locally](#setup-for-running-llm-locally-on-your-machine) |
| `openai` (for local server)   | `True`     | Connect to a local server that exposes an OpenAI-compatible API (e.g., llama.cpp). | [Setup for running LLM locally](#setup-for-running-llm-locally-on-your-machine) |
| `server`                      | `False`    | Connect to the AgenticSeek self-hosted LLM server running on another machine. | [Setup to run the LLM on your own server](#setup-to-run-the-llm-on-your-own-server) |

**API Providers (Cloud-Based):**

| Provider Name in `config.ini` | `is_local` | Description                                      | Setup Section                                       |
|-------------------------------|------------|--------------------------------------------------|-----------------------------------------------------|
| `openai`                      | `False`    | Use OpenAI's official API (e.g., GPT-3.5, GPT-4). | [Setup to run with an API](#setup-to-run-with-an-api) |
| `google`                      | `False`    | Use Google's Gemini models via API.              | [Setup to run with an API](#setup-to-run-with-an-api) |
| `deepseek`                    | `False`    | Use Deepseek's official API.                     | [Setup to run with an API](#setup-to-run-with-an-api) |
| `huggingface`                 | `False`    | Use Hugging Face Inference API.                  | [Setup to run with an API](#setup-to-run-with-an-api) |
| `togetherAI`                  | `False`    | Use TogetherAI's API for various open models.    | [Setup to run with an API](#setup-to-run-with-an-api) |

---
## Troubleshooting

If you encounter issues, this section provides guidance.

# Known Issues

## ChromeDriver Issues

**Error Example:** `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

*   **Cause:** Your installed ChromeDriver version is incompatible with your Google Chrome browser version.
*   **Solution:**
    1.  **Check Chrome Version:** Open Google Chrome, go to `Settings > About Chrome` to find your version (e.g., "Version 120.0.6099.110").
    2.  **Download Matching ChromeDriver:**
        *   For Chrome versions 115 and newer: Go to the [Chrome for Testing (CfT) JSON Endpoints](https://googlechromelabs.github.io/chrome-for-testing/). Find the "stable" channel and download the ChromeDriver for your OS that matches your Chrome's major version.
        *   For older versions (less common): You might find them on the [ChromeDriver - WebDriver for Chrome](https://chromedriver.chromium.org/downloads) page.
        *   The image below shows an example from the CfT page:
            ![Download Chromedriver specific version from Chrome for Testing page](./media/chromedriver_readme.png)
    3.  **Install ChromeDriver:**
        *   Ensure the downloaded `chromedriver` (or `chromedriver.exe` on Windows) is placed in a directory listed in your system's PATH environment variable (e.g., `/usr/local/bin` on Linux/macOS, or a custom scripts folder added to PATH on Windows).
        *   Alternatively, place it in the root directory of the `agenticSeek` project.
        *   Make sure the driver is executable (e.g., `chmod +x chromedriver` on Linux/macOS).
    4.  Refer to the [ChromeDriver Installation](#chromedriver-installation) section in the main Installation guide for more details.

If this section is incomplete or you encounter other ChromeDriver issues, please consider searching existing [GitHub Issues](https://github.com/Fosowl/agenticSeek/issues) or raising a new one.

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

This happen if there is a mismatch between your browser and chromedriver version.

You need to navigate to download the latest version:

https://developer.chrome.com/docs/chromedriver/downloads

If you're using Chrome version 115 or newer go to:

https://googlechromelabs.github.io/chrome-for-testing/

And download the chromedriver version matching your OS.

![alt text](./media/chromedriver_readme.png)

If this section is incomplete please raise an issue.

##  connection adapters Issues

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:1234/v1/chat/completions'` (Note: port may vary)
```

*   **Cause:** The `provider_server_address` in `config.ini` for `lm-studio` (or other similar local OpenAI-compatible servers) is missing the `http://` prefix or is pointing to the wrong port.
*   **Solution:**
    *   Ensure the address includes `http://`. LM-Studio typically defaults to `http://127.0.0.1:1234`.
    *   Correct `config.ini`: `provider_server_address = http://127.0.0.1:1234` (or your actual LM-Studio server port).

## SearxNG Base URL Not Provided

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.`
```

*   **Cause:** The `.env` file is missing or the `SEARXNG_BASE_URL` variable is not set within it.
*   **Solution:**
    1.  Ensure you have copied `.env.example` to `.env` in the root of the project directory (`mv .env.example .env` on Linux/macOS or `copy .env.example .env` on Windows).
    2.  Verify that the `.env` file contains `SEARXNG_BASE_URL="http://127.0.0.1:8080"`.
    3.  Alternatively (not recommended for permanent setup), you can set the environment variable in your terminal:
        *   Linux/macOS: `export SEARXNG_BASE_URL="http://127.0.0.1:8080"`
        *   Windows (CMD): `set SEARXNG_BASE_URL="http://127.0.0.1:8080"`
        *   Windows (PowerShell): `$env:SEARXNG_BASE_URL="http://127.0.0.1:8080"`

## FAQ (Frequently Asked Questions)

<a name="faq-hardware"></a>
**Q: What hardware do I need to run LLMs locally?**

| Model Size | Minimum GPU VRAM | Performance & Capability Notes                                                                 | Example GPU Tier    |
|------------|------------------|------------------------------------------------------------------------------------------------|---------------------|
| ~7B        | 8GB VRAM         | ⚠️ **Not Recommended for Agentic Tasks:** Performance is generally poor for complex reasoning, web browsing, or planning. May work for very simple queries. Expect frequent errors or nonsensical outputs. | e.g., RTX 3050 Laptop |
| ~14B       | 12GB VRAM        | ✅ **Basic Usability:** Can handle simpler tasks. May struggle with extensive web browsing, complex planning, or generating very long code sequences. | e.g., RTX 3060 (12GB) |
| ~30-34B    | 24GB VRAM        | 🚀 **Good Performance:** Suitable for most tasks, including moderately complex web browsing and planning. Good balance of capability and resource requirements. | e.g., RTX 3090, RTX 4090 |
| 70B+       | 48GB VRAM        | 💪 **Excellent Performance:** Recommended for advanced use cases, extensive research, and complex multi-step planning. Provides the most robust results. | e.g., 2x RTX 3090, A100 (40/80GB), Mac Studio M2/M3 Ultra |

*Notes:*
*   These are general guidelines. Performance also depends on model quantization, software (e.g., Ollama, LM-Studio), and CPU/RAM speed.
*   Always check the specific model card for memory recommendations.
*   Using CPU for inference is possible with some setups (e.g., Ollama with smaller models) but will be significantly slower.

<a name="faq-deepseek"></a>
**Q: Why is Deepseek R1 often mentioned or recommended?**

Deepseek models (especially their coder series) have shown strong performance in reasoning, instruction following, and tool/function calling for their size. AgenticSeek's prompts and internal logic have been tested extensively with these models. While other models can work, Deepseek often provides a good baseline experience for agentic tasks.

<a name="faq-troubleshooting"></a>
**Q: Help! I get an error when running AgenticSeek or its scripts. What should I do?**

Here's a step-by-step troubleshooting guide:

1.  **Read the Error Message Carefully:** The error message itself is the most important clue. Try to understand what it's saying.
2.  **Check Prerequisites & Installation:**
    *   **Python Version:** Are you using Python 3.10.x? Verify with `python --version` (or `python3.10 --version`) in your activated virtual environment.
    *   **Virtual Environment:** Is your virtual environment (`agentic_seek_env`) activated? You should see its name in your terminal prompt. If not, activate it (see [Installation](#2️-create-a-python-virtual-environment)).
    *   **Dependencies:** Did `pip3 install -r requirements.txt` complete without errors? If not, address those errors first. Check for missing system dependencies mentioned in the [Manual Installation](#manual-installation) section.
    *   **Core Software:** Are Git, Docker Engine, Docker Compose (V2, `docker compose`), and Google Chrome installed correctly?
    *   **ChromeDriver:** Is ChromeDriver installed, matching your Chrome version, and accessible (in PATH or project root)? See [ChromeDriver Installation](#chromedriver-installation) and [ChromeDriver Issues](#chromedriver-issues).
3.  **Verify Service Status (`./start_services.sh` or `start_services.cmd`):**
    *   Did this script complete successfully? Review its output for any error messages (e.g., Docker not running, port conflicts).
    *   Are essential services like SearxNG running? Try accessing `http://localhost:8080` in your browser. If it doesn't load, the services didn't start correctly.
4.  **Check `config.ini` (See [Config Section](#config) for details):**
    *   Is the file correctly named `config.ini` (not `config.ini.example`)?
    *   `provider_name`: Does it match your intended setup (e.g., `ollama`, `lm-studio`, `openai`, `google`)?
    *   `is_local`: `True` for local LLMs, `False` for cloud APIs.
    *   `provider_server_address`:
        *   For local LLMs: Is it correct (e.g., `http://127.0.0.1:11434` for Ollama, `http://127.0.0.1:1234` for LM-Studio)? Does it include `http://`?
        *   For API usage, this is usually less critical but ensure it's not misconfigured if present.
    *   `work_dir`: Is this set to a valid, existing directory path on your system where AgenticSeek can read/write files?
5.  **Local LLM Provider Status (if `is_local = True`):**
    *   Is your chosen LLM provider software (Ollama, LM-Studio) running independently?
        *   Ollama: `ollama serve` should be active (often runs as a background service after installation). Check with `ollama list`.
        *   LM-Studio: The application should be open, the model loaded, and the local server started from its UI.
    *   Have you downloaded/pulled the specific model listed in `provider_model` in `config.ini`? (e.g., `ollama pull model-name`).
6.  **API Key Setup (if `is_local = False`):**
    *   Is the API key correctly set as an environment variable for your current terminal session? (See [Setup to run with an API](#2-set-your-api-key-as-an-environment-variable) and [FAQ: How do I set API keys?](#how-do-i-set-api-keys)).
    *   Is the key itself correct and active?
7.  **Consult Known Issues:** Review the [Known Issues](#known-issues) section above for solutions to common problems.
8.  **Search GitHub Issues:** Check if other users have reported similar problems on the [AgenticSeek GitHub Issues page](https://github.com/Fosowl/agenticSeek/issues).
9.  **Raise an Issue:** If you're still stuck, please [create a new issue](https://github.com/Fosowl/agenticSeek/issues/new/choose). Provide as much detail as possible:
    *   Your Operating System (e.g., Windows 11, macOS Sonoma, Ubuntu 22.04).
    *   Python version.
    *   Relevant parts of your `config.ini` (please redact API keys).
    *   The exact steps you took.
    *   The full error message and any relevant logs from the terminal.

<a name="faq-100-local"></a>
**Q: Can AgenticSeek really run 100% locally?**

Yes. When configured with a local LLM provider like Ollama or LM-Studio (and `is_local = True` in `config.ini`), all core components—LLM inference, web search (via local SearxNG), speech-to-text, and text-to-speech—can run on your machine without sending data to external cloud services. Using API providers is optional.

<a name="faq-install-local-llm"></a>
**Q: How do I install local LLM providers like Ollama or LM-Studio?**

*   **Ollama:**
    1.  Go to [ollama.ai](https://ollama.ai/).
    2.  Download the installer for your operating system (Windows, macOS, Linux).
    3.  Run the installer. Ollama typically sets itself up as a background service.
    4.  Open your terminal and you can start pulling models (e.g., `ollama pull deepseekcoder:6.7b`).
    5.  Run `ollama serve` if it's not already running (though it usually starts automatically).
*   **LM-Studio:**
    1.  Go to [lmstudio.ai](https://lmstudio.ai/).
    2.  Download the installer for your system.
    3.  Install and run the application.
    4.  Use the LM-Studio UI to search for and download models.
    5.  In the "Local Server" tab, select your model and click "Start Server".

<a name="faq-get-models-local"></a>
**Q: Where do I get models (e.g., Deepseek, Qwen) for my local provider?**

*   **Ollama:** Use the `ollama pull` command followed by the model name and tag. Common models can be found on [Ollama's model library](https://ollama.ai/library).
    ```sh
    ollama pull deepseekcoder:6.7b  # Pulls a specific version of Deepseek Coder
    ollama pull qwen:14b             # Pulls a specific version of Qwen
    ollama list                     # Shows models you have downloaded
    ```
*   **LM-Studio:** Use the search bar within the LM-Studio application to find models from Hugging Face and other sources. You can then download them through the UI. Ensure you download GGUF format models compatible with llama.cpp-based engines, which LM-Studio uses.

<a name="faq-set-api-keys"></a>
**Q: How do I set API keys (e.g., for OpenAI, Google) correctly?**

API keys are usually set as environment variables. This means they are variables available to the processes running in your terminal session or system-wide.

*   **Linux/macOS:**
    *   **For the current terminal session only:**
        ```sh
        export OPENAI_API_KEY="your_openai_api_key_here"
        export GOOGLE_API_KEY="your_google_api_key_here" 
        # etc. for other providers
        ```
    *   **For persistence (recommended):** Add the `export` line(s) to your shell's configuration file. This file is usually:
        *   `~/.bashrc` (for Bash shell, common on Linux)
        *   `~/.zshrc` (for Zsh shell, default on newer macOS)
        *   `~/.profile` or `~/.bash_profile` (other common locations)
        After adding the line, either source the file (e.g., `source ~/.bashrc`) or open a new terminal window for the changes to take effect.

*   **Windows:**
    *   **Command Prompt (CMD - for current session only):**
        ```cmd
        set OPENAI_API_KEY=your_openai_api_key_here
        ```
    *   **PowerShell (for current session only):**
        ```powershell
        $env:OPENAI_API_KEY="your_openai_api_key_here"
        ```
    *   **Permanently (Recommended):**
        1.  In the Windows search bar, type "environment variables" and select "Edit the system environment variables."
        2.  In the System Properties window, click the "Environment Variables..." button.
        3.  Under "User variables" (for your account only) or "System variables" (for all users, requires admin rights), click "New...".
        4.  Enter the variable name (e.g., `OPENAI_API_KEY`) and the variable value (your actual API key).
        5.  Click OK on all windows. You may need to close and reopen any active Command Prompt or PowerShell windows for the changes to take effect.

**Important:**
*   Replace `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc., with the specific environment variable name expected by the application or library for that provider. These are often found in the provider's API documentation.
*   Ensure there are no extra spaces or quotes around the actual key unless they are part of the key itself.

<a name="faq-install-script-fails"></a>
**Q: What if `install.sh` or `install.bat` fails?**

If the automatic installation scripts encounter errors:
1.  **Examine the Output:** Look closely at the error messages printed in the terminal. This will often tell you which step failed and why.
2.  **Try Manual Installation:** Follow the [Manual Installation](#manual-installation) steps for your operating system. This gives you more control over each step and can help pinpoint the problem.
3.  **System Dependencies:** Failures are often due to missing system-level dependencies required by Python packages (e.g., `portaudio-dev` for `pyaudio`). Ensure these are installed.
4.  **Permissions:** On Linux/macOS, some commands within the script might require `sudo` if your user doesn't have the necessary permissions (e.g., for installing system packages).
5.  If you continue to have issues, refer to the general [troubleshooting FAQ](#faq-troubleshooting).

**Q: Why should I use AgenticSeek as an alternative to other tools?**

AgenticSeek was started as a side-project driven by interest in AI agents, with a strong emphasis on:
*   **Local First & Privacy:** Prioritizing the ability to run entirely on your own hardware using local LLMs, ensuring your data stays private and avoiding API costs.
*   **Open Source:** Allowing for transparency, community contributions, and customization.
*   **Inspired by Sci-Fi, Built for Practicality:** Drawing inspiration from concepts like Jarvis and Friday for a "cool" user experience, while focusing on practical functionalities similar to tools like Manus AI, aiming to provide a robust local alternative.
*   **Control & Independence:** Giving users more control over their AI assistant by reducing dependency on external, proprietary systems.

## Contribute

We’re looking for developers to improve AgenticSeek! Check out open issues or discussion.

[Contribution guide](./docs/CONTRIBUTING.md)

[![Star History Chart](https://api.star-history.com/svg?repos=Fosowl/agenticSeek&type=Date)](https://www.star-history.com/#Fosowl/agenticSeek&Date)

## Maintainers:

 > [Fosowl](https://github.com/Fosowl) | Paris Time 

 > [antoineVIVIES](https://github.com/antoineVIVIES) | Taipei Time 

 > [steveh8758](https://github.com/steveh8758) | Taipei Time 
