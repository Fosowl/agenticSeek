# AgenticSeek: プライベートなローカルManus代替

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek ロゴ">
<p>

[English](./README.md) | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | 日本語 | [Português (Brasil)](./README_PTBR.md)

*Manus AIの**100%ローカルな代替**となるこの音声対応AIアシスタントは、自律的にウェブを閲覧し、コードを書き、タスクを計画しながら、すべてのデータをあなたのデバイスに保持します。ローカル推論モデルに合わせて調整されており、完全にあなたのハードウェア上で動作するため、完全なプライバシーとクラウドへの依存ゼロを保証します。*

[![AgenticSeekを訪問](https://img.shields.io/static/v1?label=ウェブサイト&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![ライセンス](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-参加する-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=更新%20%40Fosowl)](https://x.com/Martin993886460) [![GitHubスター](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### なぜAgenticSeekなのか？

* 🔒 完全ローカル＆プライベート - すべてがあなたのマシン上で実行されます — クラウドなし、データ共有なし。あなたのファイル、会話、検索はプライベートに保たれます。

* 🌐 スマートなウェブブラウジング - AgenticSeekは自分でインターネットを閲覧できます — 検索、読み取り、情報抽出、ウェブフォーム入力 — すべてハンズフリーで。

* 💻 自律型コーディングアシスタント - コードが必要ですか？Python、C、Go、Javaなどでプログラムを書き、デバッグし、実行できます — すべて監視なしで。

* 🧠 スマートエージェント選択 - あなたが尋ねると、タスクに最適なエージェントを自動的に見つけ出します。まるで専門家チームが助けてくれるようです。

* 📋 複雑なタスクの計画と実行 - 旅行計画から複雑なプロジェクトまで — 大きなタスクをステップに分割し、複数のAIエージェントを使って物事を成し遂げることができます。

* 🎙️ 音声対応 - クリーンで高速、未来的な音声と音声認識により、まるでSF映画のパーソナルAIのように話しかけることができます。

### **デモ**

> *agenticSeekプロジェクトを検索し、必要なスキルを学び、その後CV_candidates.zipを開いて、プロジェクトに最も適した候補者を教えてください。*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

免責事項：このデモは、表示されるすべてのファイル（例：CV_candidates.zip）を含め、完全に架空のものです。私たちは企業ではなく、候補者ではなくオープンソースの貢献者を求めています。

> 🛠️ **作業中** – 貢献者を募集中です！

## インストール

Chrome Driver、Docker、Python 3.10がインストールされていることを確認してください。

セットアップにはPython 3.10を正確に使用することを強くお勧めします。そうでない場合、依存関係のエラーが発生する可能性があります。

Chromeドライバーに関する問題については、**Chromedriver**セクションを参照してください。

### 1️⃣ **リポジトリのクローンとセットアップ**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2️ **仮想環境の作成**

```sh
python3 -m venv agentic_seek_env
source agentic_seek_env/bin/activate
# Windowsの場合: agentic_seek_env\Scripts\activate
```

### 3️⃣ **パッケージのインストール**

Python、Dockerとdocker compose、Google Chromeがインストールされていることを確認してください。

Python 3.10.0を推奨します。

**自動インストール（推奨）：**

Linux/Macosの場合：
```sh
./install.sh
```

** テキスト読み上げ（TTS）機能で日本語をサポートするには、fugashi（日本語分かち書きライブラリ）をインストールする必要があります：**

** 注意: 日本語のテキスト読み上げ（TTS）機能には多くの依存関係が必要で、問題が発生する可能性があります。mecabrcに関する問題が発生することがあります。現在のところ、この問題を修正する方法が見つかっていません。当面は日本語でのテキスト読み上げ機能を無効にすることをお勧めします。**

必要なライブラリをインストールする場合は以下のコマンドを実行してください：

```
pip3 install --upgrade pyopenjtalk jaconv mojimoji unidic fugashi
pip install unidic-lite
python -m unidic download
```

Windowsの場合：

```sh
./install.bat
```

**手動：**

**注意：どのOSでも、インストールするChromeDriverがインストール済みのChromeバージョンと一致していることを確認してください。`google-chrome --version`を実行してください。Chrome >135の場合の既知の問題を参照してください。**

- *Linux*:

パッケージリストの更新：`sudo apt update`

依存関係のインストール：`sudo apt install -y alsa-utils portaudio19-dev python3-pyaudio libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1`

Chromeブラウザのバージョンに一致するChromeDriverのインストール：
`sudo apt install -y chromium-chromedriver`

要件のインストール：`pip3 install -r requirements.txt`

- *Macos*:

brewの更新：`brew update`

chromedriverのインストール：`brew install --cask chromedriver`

portaudioのインストール：`brew install portaudio`

pipのアップグレード：`python3 -m pip install --upgrade pip`

wheelのアップグレード：`pip3 install --upgrade setuptools wheel`

要件のインストール：`pip3 install -r requirements.txt`

- *Windows*:

pyreadline3のインストール：`pip install pyreadline3`

portaudioの手動インストール（例：vcpkgまたはビルド済みバイナリ経由）後、実行：`pip install pyaudio`

chromedriverの手動ダウンロードとインストール：https://sites.google.com/chromium.org/driver/getting-started

PATHに含まれるディレクトリにchromedriverを配置します。

要件のインストール：`pip3 install -r requirements.txt`

---

## マシン上でローカルにLLMを実行するためのセットアップ

**少なくともDeepseek 14Bの使用を推奨します。より小さなモデルは、特にウェブブラウジングのタスクで苦労します。**


**ローカルプロバイダーのセットアップ**

ローカルプロバイダーを開始します。例えばollamaの場合：

```sh
ollama serve
```

サポートされているローカルプロバイダーのリストについては、以下を参照してください。

**config.iniの更新**

config.iniファイルを変更して、provider_nameをサポートされているプロバイダーに、provider_modelをプロバイダーがサポートするLLMに設定します。*Qwen*や*Deepseek*などの推論モデルを推奨します。

必要なハードウェアについては、READMEの最後にある**FAQ**を参照してください。

```sh
[MAIN]
is_local = True # ローカルで実行するか、リモートプロバイダーで実行するか。
provider_name = ollama # またはlm-studio、openaiなど。
provider_model = deepseek-r1:14b # ハードウェアに合ったモデルを選択してください
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # AIの名前
recover_last_session = True # 前のセッションを復元するかどうか
save_session = True # 現在のセッションを記憶するかどうか
speak = True # テキスト読み上げ
listen = False # 音声認識、CLIのみ
work_dir =  /Users/mlg/Documents/workspace # AgenticSeekのワークスペース。
jarvis_personality = False # より「Jarvis」らしい性格を使用するかどうか（実験的）
languages = en zh # 言語のリスト、テキスト読み上げはリストの最初の言語にデフォルト設定されます
[BROWSER]
headless_browser = True # ヘッドレスブラウザを使用するかどうか、ウェブインターフェースを使用する場合のみ推奨。
stealth_mode = True # undetected seleniumを使用してブラウザ検出を減らす
```

警告：LM-studioを使用してLLMを実行する場合、provider_nameを`openai`に設定しないでください。`lm-studio`に設定してください。

注意：一部のプロバイダー（例：lm-studio）では、IPの前に`http://`が必要です。例：`http://127.0.0.1:1234`

**ローカルプロバイダーのリスト**

| プロバイダー | ローカル？ | 説明                                                      |
|-----------|--------|-----------------------------------------------------------|
| ollama    | はい    | ollamaをLLMプロバイダーとして使用して、LLMをローカルで簡単に実行します |
| lm-studio  | はい    | LM studioでLLMをローカル実行します（`provider_name`を`lm-studio`に設定）|
| openai    | はい     |  openai互換API（例：llama.cppサーバー）を使用します  |

次のステップ：[サービスの開始とAgenticSeekの実行](#サービスの開始と実行)

*問題が発生した場合は、**既知の問題**セクションを参照してください*

*ハードウェアがローカルでdeepseekを実行できない場合は、**APIで実行**セクションを参照してください*

*詳細な設定ファイルの説明については、**設定**セクションを参照してください。*

---

## APIで実行するためのセットアップ

`config.ini`で目的のプロバイダーを設定します。APIプロバイダーのリストについては、以下を参照してください。

```sh
[MAIN]
is_local = False
provider_name = google
provider_model = gemini-2.0-flash
provider_server_address = 127.0.0.1:5000 # 関係ありません
```
警告：設定に末尾のスペースがないことを確認してください。

APIキーをエクスポートします：`export <<PROVIDER>>_API_KEY="xxx"`

例：`export TOGETHER_API_KEY="xxxxx"`

**APIプロバイダーのリスト**

| プロバイダー  | ローカル？ | 説明                                               |
|-----------|--------|-----------------------------------------------------------|
| openai    | 場合による  | ChatGPT APIを使用  |
| deepseek-api  | いいえ     | Deepseek API（非プライベート）                            |
| huggingface| いいえ    | Hugging-Face API（非プライベート）                            |
| togetherAI | いいえ    | together AI APIを使用（非プライベート）                         |
| google | いいえ    | google gemini APIを使用（非プライベート）                         |
| modelscope| いいえ    | ModelScope API（非プライベート）                            |

*gpt-4oや他のclosedAIモデルの使用は推奨しません*。ウェブブラウジングやタスク計画のパフォーマンスが悪いです。

また、geminiではコーディング/bashが失敗する可能性があることに注意してください。deepseek r1用に最適化されたフォーマットのプロンプトを無視するようです。

次のステップ：[サービスの開始とAgenticSeekの実行](#サービスの開始と実行)

*問題が発生した場合は、**既知の問題**セクションを参照してください*

*詳細な設定ファイルの説明については、**設定**セクションを参照してください。*

---

## サービスの開始と実行

必要に応じてPython環境をアクティブ化します。
```sh
source agentic_seek_env/bin/activate
```

必要なサービスを開始します。これにより、docker-compose.ymlからすべてのサービスが開始されます。これには以下が含まれます：
        - searxng
        - redis（searxngに必要）
        - frontend

```sh
sudo ./start_services.sh # MacOS
start ./start_services.cmd # Window
```

**オプション1：** CLIインターフェースで実行します。

```sh
python3 cli.py
```

CLIモードでは、config.iniで`headless_browser`をFalseに設定することをお勧めします。

**オプション2：** Webインターフェースで実行します。

バックエンドを開始します。

```sh
python3 api.py
```

`http://localhost:3000/`にアクセスすると、Webインターフェースが表示されます。

---

## 使用方法

`./start_services.sh`でサービスが起動していることを確認し、CLIモードの場合は`python3 cli.py`で、Webインターフェースの場合は`python3 api.py`を実行してから`localhost:3000`にアクセスしてAgenticSeekを実行します。

設定で`listen = True`を設定することで、音声認識を使用することもできます。CLIモードのみ。

終了するには、単に`goodbye`と発言/入力します。

以下に使用例をいくつか示します：

> *Pythonでスネークゲームを作って！*

> *フランスのレンヌでトップのカフェをウェブ検索し、3つのカフェのリストとその住所をrennes_cafes.txtに保存して。*

> *数値の階乗を計算するGoプログラムを書いて、それをfactorial.goとしてワークスペースに保存して。*

> *summer_picturesフォルダ内のすべてのJPGファイルを検索し、今日の日付で名前を変更し、名前変更されたファイルのリストをphotos_list.txtに保存して。*

> *2024年の人気のSF映画をオンラインで検索し、今夜観る映画を3つ選んで。リストをmovie_night.txtに保存して。*

> *2025年の最新AIニュース記事をウェブで検索し、3つ選択して、それらのタイトルと要約をスクレイピングするPythonスクリプトを書いて。スクリプトをnews_scraper.pyとして、要約を/home/projectsのai_news.txtに保存して。*

> *フライデー、無料の株価APIをウェブで検索し、supersuper7434567@gmail.comで登録し、そのAPIを使用してテスラの日々の価格を取得するPythonスクリプトを書いて、結果をstock_prices.csvに保存して。*

*フォーム入力機能はまだ実験的であり、失敗する可能性があることに注意してください。*



クエリを入力すると、AgenticSeekはタスクに最適なエージェントを割り当てます。

これは初期のプロトタイプであるため、エージェントルーティングシステムがクエリに基づいて常に適切なエージェントを割り当てるとは限りません。

したがって、何をしたいのか、AIがどのように進むべきかについて非常に明確にする必要があります。たとえば、ウェブ検索を実行させたい場合は、次のように言わないでください：

`一人旅に適した良い国を知っていますか？`

代わりに、次のように尋ねてください：

`ウェブ検索をして、一人旅に最適な国を見つけてください`

---

## **独自のサーバーでLLMを実行するためのセットアップ**

強力なコンピューターまたは使用できるサーバーがあるが、ラップトップから使用したい場合は、カスタムLLMサーバーを使用してリモートサーバーでLLMを実行するオプションがあります。

AIモデルを実行する「サーバー」で、IPアドレスを取得します。

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # ローカルIP
curl https://ipinfo.io/ip # パブリックIP
```

注意：WindowsまたはmacOSの場合、それぞれipconfigまたはifconfigを使用してIPアドレスを見つけます。

リポジトリをクローンし、`server/`フォルダに入ります。


```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/server/
```

サーバー固有の要件をインストールします：

```sh
pip3 install -r requirements.txt
```

サーバー スクリプトを実行します。

```sh
python3 app.py --provider ollama --port 3333
```

LLMサービスとして`ollama`と`llamacpp`のどちらかを選択できます。


次に、個人のコンピュータで：

`config.ini`ファイルを変更して、`provider_name`を`server`に、`provider_model`を`deepseek-r1:xxb`に設定します。
`provider_server_address`をモデルを実行するマシンのIPアドレスに設定します。

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = x.x.x.x:3333
```


次のステップ：[サービスの開始とAgenticSeekの実行](#サービスの開始と実行)

---

## 音声認識

現在、音声認識は英語でのみ機能することに注意してください。

音声認識機能はデフォルトで無効になっています。有効にするには、config.iniファイルでlistenオプションをTrueに設定します：

```
listen = True
```

有効にすると、音声認識機能は、入力を処理し始める前にトリガーキーワード（エージェントの名前）をリッスンします。*config.ini*ファイルで`agent_name`の値を更新することで、エージェントの名前をカスタマイズできます：

```
agent_name = Friday
```

最適な認識のためには、エージェント名として「John」や「Emma」のような一般的な英語の名前を使用することをお勧めします。

トランスクリプトが表示され始めたら、エージェントの名前を声に出して起動します（例：「Friday」）。

クエリをはっきりと話します。

システムに処理を進めるよう合図するために、確認フレーズでリクエストを終了します。確認フレーズの例は次のとおりです：
```
"do it", "go ahead", "execute", "run", "start", "thanks", "would ya", "please", "okay?", "proceed", "continue", "go on", "do that", "go it", "do you understand?"
```

## 設定

設定例：
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = 127.0.0.1:11434
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False
work_dir =  /Users/mlg/Documents/ai_folder
jarvis_personality = False
languages = en zh
[BROWSER]
headless_browser = False
stealth_mode = False
```

**説明**:

- is_local -> エージェントをローカルで実行する（True）か、リモートサーバーで実行する（False）か。

- provider_name -> 使用するプロバイダー（`ollama`、`server`、`lm-studio`、`deepseek-api`のいずれか）

- provider_model -> 使用するモデル、例：deepseek-r1:32b。

- provider_server_address -> サーバーアドレス、例：ローカルの場合は127.0.0.1:11434。非ローカルAPIの場合は何でも設定します。

- agent_name -> エージェントの名前、例：Friday。TTSのトリガーワードとして使用されます。

- recover_last_session -> 前回のセッションから再開する（True）かしない（False）か。

- save_session -> セッションデータを保存する（True）かしない（False）か。

- speak -> 音声出力を有効にする（True）かしない（False）か。

- listen -> 音声入力をリッスンする（True）かしない（False）か。

- work_dir -> AIがアクセスできるフォルダ。例：/Users/user/Documents/。

- jarvis_personality -> JARVISのような性格を使用する（True）かしない（False）か。これは単にプロンプトファイルを変更します。

- languages -> サポートされている言語のリスト。LLMルーターが正しく機能するために必要です。あまりにも多くの言語や類似した言語を入れすぎないようにしてください。

- headless_browser -> 表示ウィンドウなしでブラウザを実行する（True）かしない（False）か。

- stealth_mode -> ボット検出を困難にします。唯一の欠点は、anticaptcha拡張機能を手動でインストールする必要があることです。

- languages -> サポートされている言語のリスト。エージェントルーティングシステムに必要です。言語リストが長いほど、ダウンロードされるモデルが多くなります。

## プロバイダー

以下の表は、利用可能なプロバイダーを示しています：

| プロバイダー  | ローカル？ | 説明                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | はい    | ollamaをLLMプロバイダーとして使用して、LLMをローカルで簡単に実行します |
| server    | はい    | モデルを別のマシンでホストし、ローカルマシンで実行します |
| lm-studio  | はい    | LM studioでLLMをローカル実行します（`lm-studio`）             |
| openai    | 場合による  | ChatGPT API（非プライベート）またはopenai互換APIを使用  |
| deepseek-api  | いいえ     | Deepseek API（非プライベート）                            |
| huggingface| いいえ    | Hugging-Face API（非プライベート）                            |
| togetherAI | いいえ    | together AI APIを使用（非プライベート）                         |
| google | いいえ    | google gemini APIを使用（非プライベート）                         |
| modelscope| いいえ    | ModelScope API（非プライベート）                            |

プロバイダーを選択するには、config.iniを変更します：

```
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = 127.0.0.1:5000
```
`is_local`: ローカルで実行されるLLMの場合はTrue、それ以外の場合はFalseである必要があります。

`provider_name`: 使用するプロバイダーを名前で選択します。上記のプロバイダーリストを参照してください。

`provider_model`: エージェントが使用するモデルを設定します。

`provider_server_address`: サーバーアドレス。APIプロバイダーには使用されません。

# 既知の問題

## Chromedriverの問題

**既知のエラー #1:** *chromedriverの不一致*

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

これは、ブラウザとchromedriverのバージョンが一致しない場合に発生します。

最新バージョンをダウンロードするためにナビゲートする必要があります：

https://developer.chrome.com/docs/chromedriver/downloads

Chromeバージョン115以降を使用している場合は、以下にアクセスしてください：

https://googlechromelabs.github.io/chrome-for-testing/

そして、OSに一致するchromedriverバージョンをダウンロードします。

![代替テキスト](./media/chromedriver_readme.png)

このセクションが不完全な場合は、問題を提起してください。

##  接続アダプタの問題

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:11434/v1/chat/completions'
```

プロバイダーのIPアドレスの前に`http://`があることを確認してください：

`provider_server_address = http://127.0.0.1:11434`

## SearxNGのベースURLを指定する必要があります

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.
```

`.env.example`を`.env`として移動しなかった可能性がありますか？SEARXNG_BASE_URLをエクスポートすることもできます：

`export  SEARXNG_BASE_URL="http://127.0.0.1:8080"`

## FAQ

**Q: どのようなハードウェアが必要ですか？**

| モデルサイズ | GPU        | コメント                                                                 |
|-----------|------------|--------------------------------------------------------------------------|
| 7B        | 8GB VRAM   | ⚠️ 非推奨。パフォーマンスが悪く、幻覚が頻繁に発生し、プランナーエージェントは失敗する可能性が高いです。 |
| 14B       | 12GB VRAM（例：RTX 3060） | ✅ 簡単なタスクには使用可能。ウェブブラウジングや計画タスクで苦労する可能性があります。       |
| 32B       | 24GB以上のVRAM（例：RTX 4090） | 🚀 ほとんどのタスクで成功しますが、タスク計画でまだ苦労する可能性があります。             |
| 70B+      | 48GB以上のVRAM（例：mac studio） | 💪 素晴らしい。高度なユースケースに推奨されます。                                 |

**Q: なぜ他のモデルではなくDeepseek R1なのですか？**

Deepseek R1は、そのサイズに対して推論とツール使用に優れています。私たちのニーズに合っていると考えており、他のモデルも正常に動作しますが、Deepseekが私たちの主要な選択肢です。

**Q: `cli.py`を実行するとエラーが発生します。どうすればよいですか？**

ローカルが実行されていること（`ollama serve`）、`config.ini`がプロバイダーと一致していること、依存関係がインストールされていることを確認してください。それでも解決しない場合は、遠慮なく問題を提起してください。

**Q: 本当に100%ローカルで実行できますか？**

はい、Ollama、lm-studio、またはサーバープロバイダーを使用すると、すべての音声認識、LLM、テキスト読み上げモデルがローカルで実行されます。非ローカルオプション（OpenAIまたはその他のAPI）はオプションです。

**Q: Manusがあるのに、なぜAgenticSeekを使うべきなのですか？**

これは、AIエージェントへの関心から始めたサイドプロジェクトです。特別なのは、ローカルモデルを使用し、APIを避けたいということです。
私たちはJarvisとFriday（アイアンマン映画）からインスピレーションを得て「クール」にしましたが、機能性についてはManusからより多くのインスピレーションを得ています。なぜなら、それが人々が最初に望むもの、つまりローカルなManusの代替だからです。
Manusとは異なり、AgenticSeekは外部システムからの独立性を優先し、より多くの制御、プライバシーを提供し、APIコストを回避します。

## 貢献する

AgenticSeekを改善するための開発者を募集しています！オープンな問題やディスカッションを確認してください。

[貢献ガイド](./docs/CONTRIBUTING.md)

[![スター履歴チャート](https://api.star-history.com/svg?repos=Fosowl/agenticSeek&type=Date)](https://www.star-history.com/#Fosowl/agenticSeek&Date)

## メンテナー：

 > [Fosowl](https://github.com/Fosowl) | パリ時間

 > [antoineVIVIES](https://github.com/antoineVIVIES) | Taipei Time 

 > [steveh8758](https://github.com/steveh8758) | 台北時間 |（常に忙しい）
