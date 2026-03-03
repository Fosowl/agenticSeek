# AgenticSeek: Manusのプライベートでローカルな代替品

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek Logo">
<p>

  English | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md) | [Español](./README_ES.md) | [Türkçe](./README_TR.md)

*音声対応のAIアシスタントで、**100%ローカルで動作するManus AIの代替品**です。自律的にウェブを閲覧し、コードを書き、タスクを計画し、すべてのデータをデバイス上に保持します。ローカル推論モデル向けに設計されており、完全にあなたのハードウェア上で動作し、プライバシーを保証し、クラウドへの依存をゼロにします。*

[![AgenticSeekを訪問](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460) [![GitHub stars](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### なぜAgenticSeekを選ぶのか？

* 🔒 完全にローカル＆プライベート - すべてがあなたのマシン上で動作し、クラウドなし、データ共有なし。あなたのファイル、会話、検索はプライベートのままです。

* 🌐 インテリジェントなウェブブラウジング - AgenticSeekは自律的にインターネットを閲覧できます：検索、読み取り、情報抽出、ウェブフォーム入力、すべて手動操作なしで。

* 💻 自律的なプログラミングアシスタント - コードが必要ですか？Python、C、Go、Javaなどのプログラムを監督なしで書き、デバッグし、実行できます。

* 🧠 インテリジェントなエージェント選択 - あなたが要求すると、自動的に最適なエージェントがタスクに割り当てられます。常に利用可能な専門家チームを持っているようなものです。

* 📋 複雑なタスクの計画と実行 - 旅行計画から複雑なプロジェクトまで、大きなタスクをステップに分解し、複数のAIエージェントを使用して完了できます。

* 🎙️ 音声サポート - クリーンで高速で未来的な音声と音声認識機能により、SF映画のようなパーソナルAIと会話できます。（開発中）

### **デモ**

> *agenticSeekプロジェクトを検索して必要なスキルを学び、CV_candidates.zipを開いて、どの候補がプロジェクトに最も適しているか教えてくれますか？*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

免責事項：このデモと表示されるすべてのファイル（例：CV_candidates.zip）は完全に架空のものです。私たちは企業ではなく、候補者ではなくオープンソースの貢献者を求めています。

> 🛠⚠️️ **アクティブな開発中**

> 🙏 このプロジェクトはサイドプロジェクトとして始まり、ロードマップも資金もありませんでした。GitHub Trendingに登場して予想以上に成長しました。貢献、フィードバック、忍耐に深く感謝します。

## 前提条件

始める前に、以下がインストールされていることを確認してください：

*   **Git:** リポジトリをクローンするため。[Gitをダウンロード](https://git-scm.com/downloads)
*   **Python 3.10.x:** Python 3.10.xを強く推奨します。他のバージョンでは依存関係エラーが発生する可能性があります。[Python 3.10をダウンロード](https://www.python.org/downloads/release/python-3100/)（3.10.xバージョンを選択）。
*   **Docker Engine & Docker Compose:** SearxNGなどのパッケージ化されたサービスを実行するため。
    *   Docker Desktopをインストール（Docker Compose V2を含む）：[Windows](https://docs.docker.com/desktop/install/windows-install/) | [Mac](https://docs.docker.com/desktop/install/mac-install/) | [Linux](https://docs.docker.com/desktop/install/linux-install/)
    *   またはLinuxでDocker EngineとDocker Composeを別々にインストール：[Docker Engine](https://docs.docker.com/engine/install/) | [Docker Compose](https://docs.docker.com/compose/install/)（Compose V2をインストールしていることを確認、例：`sudo apt-get install docker-compose-plugin`）。

### 1. **リポジトリをクローンして設定**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2. .envファイルの内容を変更

```sh
SEARXNG_BASE_URL="http://searxng:8080" # ホストでCLIモードを実行する場合はhttp://127.0.0.1:8080を使用
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

必要に応じて`.env`ファイルを更新してください：

- **SEARXNG_BASE_URL**: ホストでCLIモードを実行する場合を除き、変更しないでください。
- **REDIS_BASE_URL**: 変更しないでください 
- **WORK_DIR**: ローカル作業ディレクトリへのパス。AgenticSeekはこれらのファイルを読み取り、操作できます。
- **OLLAMA_PORT**: Ollamaサービスのポート番号。
- **LM_STUDIO_PORT**: LM Studioサービスのポート番号。
- **CUSTOM_ADDITIONAL_LLM_PORT**: 追加のカスタムLLMサービスのポート。

**APIキーは、ローカルでLLMを実行することを選択するユーザーには完全にオプションであり、これがこのプロジェクトの主な目的です。ハードウェアが十分にある場合は空のままにしてください。**

### 3. **Dockerを起動**

Dockerがインストールされ、システム上で実行されていることを確認してください。以下のコマンドでDockerを起動できます：

- **Linux/macOS:**  
    ターミナルを開いて実行：
    ```sh
    sudo systemctl start docker
    ```
    または、インストールされている場合はアプリケーションメニューからDocker Desktopを起動。

- **Windows:**  
    スタートメニューからDocker Desktopを起動。

Dockerが実行されているかは以下で確認できます：
```sh
docker info
```
Dockerインストール情報が表示されれば正常に動作しています。

要約については以下の[ローカルプロバイダーリスト](#ローカルプロバイダーリスト)を参照してください。

次のステップ：[ローカルでAgenticSeekを実行](#サービスを起動して実行)

*問題が発生した場合は、[トラブルシューティング](#トラブルシューティング)セクションを参照してください。*
*ハードウェアがローカルでLLMを実行できない場合は、[APIを使用した実行設定](#apiを使用した実行設定)を参照してください。*
*詳細な`config.ini`の説明については、[設定セクション](#設定)を参照してください。*

---

## マシン上でローカルにLLMを実行する設定

**ハードウェア要件:**

LLMをローカルで実行するには、十分なハードウェアが必要です。少なくともMagistral、Qwen、またはDeepseek 14Bを実行できるGPUが必要です。詳細なモデル/パフォーマンスの推奨事項についてはFAQを参照してください。

**ローカルプロバイダーを設定**  

例えばollamaを使用してローカルプロバイダーを起動：

```sh
ollama serve
```

サポートされているローカルプロバイダーのリストは以下を参照してください。

**config.iniを更新**

config.iniファイルを変更して、provider_nameをサポートされているプロバイダーに、provider_modelをプロバイダーがサポートするLLMに設定します。*Magistral*や*Deepseek*などの推論モデルをお勧めします。

必要なハードウェアについては、READMEの最後にある**FAQ**を参照してください。

```sh
[MAIN]
is_local = True # ローカルで実行するかリモートプロバイダーを使用するか
provider_name = ollama # またはlm-studio、openaiなど
provider_model = deepseek-r1:14b # ハードウェアに互換性のあるモデルを選択
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # AIの名前
recover_last_session = True # 前のセッションを復元
save_session = True # 現在のセッションを記憶
speak = False # テキスト読み上げ
listen = False # 音声認識、CLIのみ、実験的
jarvis_personality = False # より「Jarvis」的な性格を使用（実験的）
languages = en zh # 言語リスト、TTSはデフォルトでリストの最初を使用
[BROWSER]
headless_browser = True # ホストでCLIを使用する場合を除き変更しない
stealth_mode = True # 検出されにくいseleniumを使用してブラウザ検出を減らす
```

**警告**:

- `config.ini`ファイル形式はコメントをサポートしていません。
コメントがエラーを引き起こすため、サンプル設定を直接コピー＆ペーストしないでください。代わりに、コメントなしで希望の設定で`config.ini`ファイルを手動で変更してください。

- LM-studioを使用してLLMを実行する場合、provider_nameを`openai`に設定*しない*でください。`lm-studio`として使用してください。

- 一部のプロバイダー（例：lm-studio）では、IPの前に`http://`が必要です。例：`http://127.0.0.1:1234`

**ローカルプロバイダーリスト**

| プロバイダー  | ローカル？ | 説明                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | はい    | ollamaを使用して簡単にローカルでLLMを実行 |
| lm-studio  | はい    | LM studioでローカルにLLMを実行（`provider_name` = `lm-studio`に設定）|
| openai    | はい     |  OpenAI互換API（例：llama.cppサーバー）を使用  |

次のステップ：[サービスを起動してAgenticSeekを実行](#サービスを起動して実行)  

*問題が発生した場合は、[トラブルシューティング](#トラブルシューティング)セクションを参照してください。*
*ハードウェアがローカルでLLMを実行できない場合は、[APIを使用した実行設定](#apiを使用した実行設定)を参照してください。*
*詳細な`config.ini`の説明については、[設定セクション](#設定)を参照してください。*

## APIを使用した実行設定

この設定では、外部のクラウドベースのLLMプロバイダーを使用します。選択したサービスからAPIキーを取得する必要があります。

**1. APIプロバイダーを選択し、APIキーを取得:**

以下の[APIプロバイダーリスト](#apiプロバイダーリスト)を参照してください。ウェブサイトにアクセスして登録し、APIキーを取得してください。

**2. APIキーを環境変数として設定:**

*   **Linux/macOS:**
    ターミナルを開き、`export`コマンドを使用します。永続的にするにはシェルの設定ファイル（例：`~/.bashrc`、`~/.zshrc`）に追加するのがベストです。
    ```sh
    export PROVIDER_API_KEY="your_api_key_here" 
    # PROVIDER_API_KEYを特定の変数名に置き換えてください、例：OPENAI_API_KEY、GOOGLE_API_KEY
    ```
    TogetherAIの例：
    ```sh
    export TOGETHER_API_KEY="xxxxxxxxxxxxxxxxxxxxxx"
    ```
*   **Windows:**
    *   **コマンドプロンプト（現在のセッション限定）:**
        ```cmd
        set PROVIDER_API_KEY=your_api_key_here
        ```
    *   **PowerShell（現在のセッション限定）:**
        ```powershell
        $env:PROVIDER_API_KEY="your_api_key_here"
        ```
    *   **永続的:** Windowsの検索バーで「環境変数」を検索し、「システムの環境変数を編集」をクリックしてから「環境変数...」ボタンをクリックします。適切な名前（例：`OPENAI_API_KEY`）とキーを値として新しいユーザー変数を追加します。

    *(詳細については、FAQを参照してください：[APIキーを設定する方法？](#apiキーを設定する方法))。*


**3. `config.ini`を更新:**
```ini
[MAIN]
is_local = False
provider_name = openai # またはgoogle、deepseek、togetherAI、huggingface
provider_model = gpt-3.5-turbo # またはgemini-1.5-flash、deepseek-chat、mistralai/Mixtral-8x7B-Instruct-v0.1など
provider_server_address = # is_local = Falseの場合、ほとんどのAPIでは無視されるか空にできる
# ... その他の設定 ...
```
*警告:* configの値に末尾のスペースがないことを確認してください。

**APIプロバイダーリスト**

| プロバイダー     | `provider_name` | ローカル？ | 説明                                       | APIキーリンク（例）                     |
|--------------|-----------------|--------|---------------------------------------------------|---------------------------------------------|
| OpenAI       | `openai`        | いいえ     | OpenAIのAPIを通じてChatGPTモデルを使用。              | [platform.openai.com/signup](https://platform.openai.com/signup) |
| Google Gemini| `google`        | いいえ     | Google AI Studioを通じてGoogle Geminiモデルを使用。    | [aistudio.google.com/keys](https://aistudio.google.com/keys) |
| Deepseek     | `deepseek`      | いいえ     | 彼らのAPIを通じてDeepseekモデルを使用。                | [platform.deepseek.com](https://platform.deepseek.com) |
| Hugging Face | `huggingface`   | いいえ     | Hugging Face Inference APIのモデルを使用。       | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| TogetherAI   | `togetherAI`    | いいえ     | TogetherAI APIを通じて様々なオープンソースモデルを使用。| [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) |
| OpenRouter   | `openrouter`    | いいえ     | OpenRouter APIを通じて様々なオープンソースモデルを使用。| [openrouter.api](https://openrouter.ai/) |

*注:*
*   複雑なウェブブラウジングとタスクプランニングには`gpt-4o`や他のOpenAIモデルの使用は推奨しません。現在のプロンプト最適化はDeepseekなどのモデルを対象としているためです。
*   コーディング/bashタスクはGeminiで失敗する可能性があります。Deepseek r1用に最適化されたプロンプト形式を無視する傾向があるためです。
*   `is_local = False`の場合、`config.ini`の`provider_server_address`は通常使用されません。APIエンドポイントは通常、対応するプロバイダーのライブラリで処理されるためです。

次のステップ：[サービスを起動してAgenticSeekを実行](#サービスを起動して実行)

*問題が発生した場合は、**既知の問題**セクションを参照してください*

*詳細な設定ファイルの説明については、**設定セクション**を参照してください。*

---

## サービスを起動して実行

デフォルトでは、AgenticSeekは完全にDocker内で実行されます。

**オプション1:** DockerでWebインターフェースを使用して実行：

必要なサービスを起動します。これにより、docker-compose.ymlのすべてのサービスが起動します：
    - searxng
    - redis（searxngに必要）
    - frontend
    - backend（Webインターフェースに`full`を使用する場合）

```sh
./start_services.sh full # MacOS
start start_services.cmd full # Windows
```

**警告:** このステップではすべてのDockerイメージがダウンロードされロードされます。最大30分かかる場合があります。サービスを起動した後、メッセージを送信する前にバックエンドサービスが完全に実行されていることを確認してください（ログに**backend: "GET /health HTTP/1.1" 200 OK**が表示されるはずです）。初回実行時、バックエンドサービスは起動に5分かかる場合があります。

`http://localhost:3000/`にアクセスすると、Webインターフェースが表示されます。

*サービス起動のトラブルシューティング:* これらのスクリプトが失敗する場合は、Docker Engineが実行中でDocker Compose（V2、`docker compose`）が正しくインストールされていることを確認してください。ターミナル出力のエラーメッセージを確認してください。[FAQ: ヘルプ！AgenticSeekまたはそのスクリプトを実行するとエラーが発生します](#faq-トラブルシューティング)を参照してください。

**オプション2:** CLIモード：

CLIインターフェースで実行するには、ホストにパッケージをインストールする必要があります：

```sh
./install.sh
./install.bat # windows
```

次に、`config.ini`のSEARXNG_BASE_URLを以下に変更する必要があります：

```sh
SEARXNG_BASE_URL="http://localhost:8080"
```

必要なサービスを起動します。これにより、docker-compose.ymlの一部のサービスが起動します：
    - searxng
    - redis（searxngに必要）
    - frontend

```sh
./start_services.sh # MacOS
start start_services.cmd # Windows
```

実行：uv run: `uv run python -m ensurepip` でuvがpipを有効にしていることを確認します。

CLIを使用：`uv run cli.py`

---

## 使用方法

サービスが`./start_services.sh full`で実行されていることを確認し、`localhost:3000`にアクセスしてWebインターフェースを使用します。

`listen = True`を設定することで音声認識も使用できます。CLIモードのみ。

終了するには、単に`goodbye`と言う/入力します。

使用例：

> *Pythonでスネークゲームを作って！*

> *ウェブでフランスのレンヌの最高のカフェを検索し、3つとその住所をrennes_cafes.txtに保存して*

> *階乗を計算するGoプログラムを書き、factorial.goとしてワークスペースに保存して*

> *summer_picturesフォルダ内のすべてのJPGファイルを検索し、今日の日付で名前を変更し、名前変更されたファイルのリストをphotos_list.txtに保存して*

> *オンラインで2024年の人気SF映画を検索し、今夜見るために3つ選び、movie_night.txtに保存して*

> *ウェブで2025年の最新AIニュース記事を検索し、3つ選び、タイトルと要約を抽出するPythonスクリプトを書き、スクリプトをnews_scraper.pyとして保存し、要約をai_news.txtに保存（/home/projects）*

> *金曜日、無料の株価APIをウェブ検索し、supersuper7434567@gmail.comで登録し、APIを使用してテスラの日次株価を取得するPythonスクリプトを書き、結果をstock_prices.csvに保存して*

*フォーム入力はまだ実験的であり、失敗する可能性があることに注意してください。*

クエリを入力すると、AgenticSeekが最適なエージェントをタスクに割り当てます。

これは初期プロトタイプであるため、エージェントルーティングシステムは常にクエリに正しいエージェントを割り当てられるとは限りません。

したがって、あなたが何を望んでいるか、そしてAIがどのように進めるかを非常に明確に表現する必要があります。例えば、ウェブ検索をしてほしい場合は、次のように言わないでください：

`一人旅に適した国を知っていますか？`

代わりに、次のように言ってください：

`ウェブ検索を実行し、一人旅に最適な国を見つけてください`

---

## **独自のサーバーでLLMを実行する設定**

強力なコンピューターやアクセス可能なサーバーを持っているが、ラップトップから使用したい場合は、カスタムllmサーバーを使用してリモートサーバーでLLMを実行することを選択できます。

AIモデルを実行する「サーバー」で、IPアドレスを取得します

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # ローカルIP
curl https://ipinfo.io/ip # パブリックIP
```

注：WindowsまたはmacOSでは、IPアドレスを見つけるためにipconfigまたはifconfigを使用してください。

リポジトリをクローンし、`server/`フォルダに移動します。

```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/llm_server/
```

サーバー固有の要件をインストールします：

```sh
pip3 install -r requirements.txt
```

サーバースクリプトを実行します。

```sh
python3 app.py --provider ollama --port 3333
```

LLMサービスとして`ollama`と`llamacpp`のどちらを使用するか選択できます。

次に、あなたのパーソナルコンピューターで：

`config.ini`ファイルを変更して、`provider_name`を`server`に、`provider_model`を`deepseek-r1:xxb`に設定します。
`provider_server_address`をモデルを実行するマシンのIPアドレスに設定します。

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = http://x.x.x.x:3333
```

次のステップ：[サービスを起動してAgenticSeekを実行](#サービスを起動して実行)  

---

## 音声認識

警告：現在、音声認識はCLIモードでのみ機能します。

現在、音声認識は英語でのみ機能することに注意してください。

音声認識機能はデフォルトで無効になっています。有効にするには、config.iniファイルでlistenオプションをTrueに設定します：

```
listen = True
```

有効にすると、音声認識機能はトリガーワード、つまりエージェントの名前をリッスンし、その後入力を処理し始めます。*config.ini*ファイルの`agent_name`値を更新することでエージェントの名前をカスタマイズできます：

```
agent_name = Friday
```

最高の認識のためには、エージェント名として「John」や「Emma」などの一般的な英語名を使用することをお勧めします。

文字起こしが表示され始めたら、エージェントの名前を大声で言って起動します（例：「Friday」）。

クエリを明確に言います。

確認フレーズでリクエストを終了して、システムに続行するように指示します。確認フレーズの例：
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
provider_server_address = http://127.0.0.1:11434 # Ollama例；LM-Studioはhttp://127.0.0.1:1234を使用
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False

jarvis_personality = False
languages = en zh # TTSおよび潜在的なルーティングの言語リスト。
[BROWSER]
headless_browser = False
stealth_mode = False
```

**`config.ini`設定の説明**：

*   **`[MAIN]`セクション：**
    *   `is_local`: ローカルLLMプロバイダー（Ollama、LM-Studio、ローカルOpenAI互換サーバー）またはセルフホストサーバーオプションを使用する場合は`True`。クラウドベースのAPI（OpenAI、Googleなど）を使用する場合は`False`。
    *   `provider_name`: LLMプロバイダーを指定します。
        *   ローカルオプション：`ollama`、`lm-studio`、`openai`（ローカルOpenAI互換サーバー用）、`server`（セルフホストサーバー設定用）。
        *   APIオプション：`openai`、`google`、`deepseek`、`huggingface`、`togetherAI`。
    *   `provider_model`: 選択したプロバイダーの特定のモデル名またはID（例：Ollamaの`deepseekcoder:6.7b`、OpenAI APIの`gpt-3.5-turbo`、TogetherAIの`mistralai/Mixtral-8x7B-Instruct-v0.1`）。
    *   `provider_server_address`: あなたのLLMプロバイダーのアドレス。
        *   ローカルプロバイダー用：例：Ollamaの`http://127.0.0.1:11434`、LM-Studioの`http://127.0.0.1:1234`。
        *   `server`プロバイダータイプ用：あなたのセルフホストLLMサーバーのアドレス（例：`http://your_server_ip:3333`）。
        *   クラウドAPI用（`is_local = False`）：これは通常無視されるか空にできます。APIエンドポイントは通常クライアントライブラリで処理されるためです。
    *   `agent_name`: AIアシスタントの名前（例：Friday）。有効な場合、音声認識のトリガーワードとして使用されます。
    *   `recover_last_session`: `True`は前のセッションの状態を復元しようとし、`False`は最初から開始します。
    *   `save_session`: `True`は現在のセッションの状態を潜在的な復元用に保存し、`False`はしません。
    *   `speak`: `True`はテキスト読み上げ音声出力を有効にし、`False`は無効にします。
    *   `listen`: `True`は音声認識音声入力を有効にし（CLIモードのみ）、`False`は無効にします。
    *   `work_dir`: **重要：** AgenticSeekがファイルを読み書きするディレクトリ。**このパスがシステムで有効かつアクセス可能であることを確認してください。**
    *   `jarvis_personality`: `True`はより「Jarvis-like」なシステムプロンプトを使用（実験的）、`False`は標準プロンプトを使用。
    *   `languages`: カンマ区切りの言語リスト（例：`en, zh, fr`）。TTS音声選択（デフォルトは最初）に使用され、LLMルーターを支援できます。ルーターの非効率性を避けるため、多すぎる言語や非常に類似した言語の使用は避けてください。
*   **`[BROWSER]`セクション：**
    *   `headless_browser`: `True`は可視ウィンドウなしで自動化ブラウザを実行（Webインターフェースまたは非対話的使用に推奨）。`False`はブラウザウィンドウを表示（CLIモードまたはデバッグに有用）。
    *   `stealth_mode`: `True`はブラウザ自動化の検出を困難にする措置を有効にします。anticaptchaなどのブラウザ拡張機能の手動インストールが必要な場合があります。

このセクションはサポートされているLLMプロバイダータイプをまとめています。`config.ini`で設定します。

**ローカルプロバイダー（独自のハードウェアで実行）：**

| config.iniのプロバイダー名 | `is_local` | 説明                                                                 | 設定セクション                                                    |
|-------------------------------|------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| `ollama`                      | `True`     | Ollamaを使用してローカルでLLMを簡単に提供。                                             | [マシン上でローカルにLLMを実行する設定](#マシン上でローカルにllmを実行する設定) |
| `lm-studio`                   | `True`     | LM-StudioでローカルにLLMを提供。                                          | [マシン上でローカルにLLMを実行する設定](#マシン上でローカルにllmを実行する設定) |
| `openai`（ローカルサーバー用）   | `True`     | OpenAI互換APIを公開するローカルサーバー（例：llama.cpp）に接続。 | [マシン上でローカルにLLMを実行する設定](#マシン上でローカルにllmを実行する設定) |
| `server`                      | `False`    | 別のマシンで実行されているAgenticSeekセルフホストLLMサーバーに接続。 | [独自のサーバーでLLMを実行する設定](#独自のサーバーでllmを実行する設定) |

**APIプロバイダー（クラウドベース）：**

| config.iniのプロバイダー名 | `is_local` | 説明                                      | 設定セクション                                       |
|-------------------------------|------------|--------------------------------------------------|-----------------------------------------------------|
| `openai`                      | `False`    | OpenAIの公式API（例：GPT-3.5、GPT-4）を使用。 | [APIを使用した実行設定](#apiを使用した実行設定) |
| `google`                      | `False`    | APIを通じてGoogleのGeminiモデルを使用。              | [APIを使用した実行設定](#apiを使用した実行設定) |
| `deepseek`                    | `False`    | Deepseekの公式APIを使用。                     | [APIを使用した実行設定](#apiを使用した実行設定) |
| `huggingface`                 | `False`    | Hugging Face Inference APIを使用。                  | [APIを使用した実行設定](#apiを使用した実行設定) |
| `togetherAI`                  | `False`    | TogetherAIのAPIを通じて様々なオープンモデルを使用。    | [APIを使用した実行設定](#apiを使用した実行設定) |

---
## トラブルシューティング

問題が発生した場合、このセクションはガイダンスを提供します。

# 既知の問題

## ChromeDriverの問題

**エラー例：** `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

### 根本原因
ChromeDriverのバージョン非互換性は以下で発生します：
1. インストールしたChromeDriverのバージョンがChromeブラウザのバージョンと一致しない
2. Docker環境では、`undetected_chromedriver`が独自のChromeDriverバージョンをダウンロードし、マウントされたバイナリを回避する可能性がある

### 解決手順

#### 1. Chromeのバージョンを確認
Google Chromeを開く → `設定 > Chromeについて`でバージョンを確認（例：「バージョン 134.0.6998.88」）

#### 2. 一致するChromeDriverをダウンロード

**Chrome 115以降の場合：** [Chrome for Testing API](https://googlechromelabs.github.io/chrome-for-testing/)を使用
- Chrome for Testingの可用性ダッシュボードにアクセス
- あなたのChromeバージョンまたは最も近い利用可能な一致を見つける
- オペレーティングシステム用のChromeDriverをダウンロード（Docker環境ではLinux64を使用）

**古いChromeバージョンの場合：** [レガシーChromeDriverダウンロード](https://chromedriver.chromium.org/downloads)を使用

![Chrome for TestingからChromeDriverをダウンロード](./media/chromedriver_readme.png)

#### 3. ChromeDriverをインストール（方法を選択）

**方法A：プロジェクトルートディレクトリ（Docker推奨）**
```bash
# ダウンロードしたchromedriverバイナリをプロジェクトルートディレクトリに配置
cp path/to/downloaded/chromedriver ./chromedriver
chmod +x ./chromedriver  # Linux/macOSで実行可能にする
```

**方法B：システムPATH**
```bash
# Linux/macOS
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Windows: chromedriver.exeをPATH内のフォルダに配置
```

#### 4. インストールを確認
```bash
# ChromeDriverのバージョンをテスト
./chromedriver --version
# またはPATHにある場合：
chromedriver --version
```

### Docker固有の指示

⚠️ **Dockerユーザーへの重要：**
- Dockerボリュームマウント方法はステルスモード（`undetected_chromedriver`）では機能しない可能性があります
- **解決策：** ChromeDriverをプロジェクトルートディレクトリに`./chromedriver`として配置
- アプリケーションが自動的に検出し、このバイナリを使用します
- ログに次のメッセージが表示されるはずです：`"Using ChromeDriver from project root: ./chromedriver"`

### トラブルシューティングのヒント

1. **まだバージョンの不一致が発生しますか？**
   - ChromeDriverが実行可能か確認：`ls -la ./chromedriver`
   - ChromeDriverのバージョンを確認：`./chromedriver --version`
   - Chromeブラウザのバージョンと一致することを確認

2. **Dockerコンテナの問題ですか？**
   - バックエンドログを確認：`docker logs backend`
   - メッセージを探す：`"Using ChromeDriver from project root"`
   - 見つからない場合は、ファイルが存在し実行可能であることを確認

3. **Chrome for Testingのバージョン**
   - 可能な限り完全一致を使用
   - バージョン134.0.6998.88の場合、ChromeDriver 134.0.6998.165を使用（最も近い利用可能バージョン）
   - メジャーバージョン番号は一致する必要があります（134 = 134）

### バージョン互換性マトリックス

| Chromeバージョン | ChromeDriverバージョン | ステータス |
|----------------|---------------------|---------|
| 134.0.6998.x   | 134.0.6998.165     | ✅ 利用可能 |
| 133.0.6943.x   | 133.0.6943.141     | ✅ 利用可能 |
| 132.0.6834.x   | 132.0.6834.159     | ✅ 利用可能 |

*最新の互換性については、[Chrome for Testingダッシュボード](https://googlechromelabs.github.io/chrome-for-testing/)を確認*

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

ブラウザとchromedriverのバージョンが一致しない場合に発生します。

最新バージョンをダウンロードする必要があります：

https://developer.chrome.com/docs/chromedriver/downloads

Chromeバージョン115以降を使用している場合は、以下にアクセス：

https://googlechromelabs.github.io/chrome-for-testing/

オペレーティングシステムに一致するchromedriverバージョンをダウンロードします。

![alt text](./media/chromedriver_readme.png)

このセクションが不完全な場合は、issueを開いてください。

##  接続アダプターの問題

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:1234/v1/chat/completions'`（注：ポートは異なる場合があります）
```

*   **原因：** `config.ini`の`lm-studio`（または他の類似のローカルOpenAI互換サーバー）の`provider_server_address`に`http://`プレフィックスが欠けているか、間違ったポートを指している。
*   **解決策：**
    *   アドレスに`http://`が含まれていることを確認。LM-Studioは通常デフォルトで`http://127.0.0.1:1234`を使用。
    *   正しい`config.ini`：`provider_server_address = http://127.0.0.1:1234`（または実際のLM-Studioサーバーポート）。

## SearxNGベースURLが提供されていない

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.`
```

間違ったsearxngベースURLでCLIモードを実行すると発生する可能性があります。

SEARXNG_BASE_URLは、Dockerで実行するかホストで実行するかによって異なります：

**ホストで実行：** `SEARXNG_BASE_URL="http://localhost:8080"`

**完全にDocker内で実行（Webインターフェース）：** `SEARXNG_BASE_URL="http://searxng:8080"`

## FAQ

**Q: どのようなハードウェアが必要ですか？**  

| モデルサイズ  | GPU  | コメント                                               |
|-----------|--------|-----------------------------------------------------------|
| 7B        | 8GB VRAM | ⚠️ 非推奨。パフォーマンスが低く、頻繁な幻覚、計画エージェントが失敗する可能性があります。 |
| 14B        | 12 GB VRAM（例：RTX 3060） | ✅ 単純なタスクに使用可能。ウェブブラウジングとタスク計画に困難がある可能性があります。 |
| 32B        | 24+ GB VRAM（例：RTX 4090） | 🚀 ほとんどのタスクで成功、タスク計画にまだ困難がある可能性があります |
| 70B+        | 48+ GB VRAM | 💪 優れています。高度な使用例に推奨。 |

**Q: エラーが発生したらどうすればよいですか？**  

ローカルが実行されていること（`ollama serve`）、`config.ini`がプロバイダーと一致していること、依存関係がインストールされていることを確認してください。どれも機能しない場合は、遠慮なくissueを開いてください。

**Q: 本当に100%ローカルで実行できますか？**  

はい、Ollama、lm-studio、またはserverプロバイダーを使用すると、すべての音声認識、LLM、テキスト読み上げモデルがローカルで実行されます。非ローカルオプション（OpenAI或其他API）はオプションです。

**Q: Manusがあるのに、なぜAgenticSeekを使用する必要がありますか？**

Manusとは異なり、AgenticSeekは外部システムからの独立性を優先し、より多くの制御、プライバシー、APIコストの回避を提供します。

**Q: このプロジェクトの背後には誰がいますか？**

このプロジェクトは私によって作成され、2人の友人がメンテナーとして、GitHub上のオープンソースコミュニティの貢献者と共に運営されています。私たちは単なる情熱的な個人であり、スタートアップではなく、どの組織にも所属していません。

私の個人アカウント（https://x.com/Martin993886460）以外のX上のAgenticSeekアカウントはすべて偽物です。

## 貢献

AgenticSeekを改善する開発者を探しています！オープンなissueやディスカッションを確認してください。

[貢献ガイド](./docs/CONTRIBUTING.md)

## スポンサー：

フライト検索、旅行計画、または最高の買い物のお得な情報の取得などの機能でAgenticSeekの能力を向上させたいですか？SerpApiを使用してカスタムツールを作成し、より多くのJarvisのような機能を解放することを検討してください。SerpApiを使用すると、プロフェッショナルなタスクのためにエージェントを加速させながら、完全な制御を維持できます。

<a href="https://serpapi.com/"><img src="./media/banners/sponsor_banner_serpapi.png" height="350" alt="SerpApi Banner" ></a>

[Contributing.md](./docs/CONTRIBUTING.md)をチェックして、カスタムツールを統合する方法を学びましょう！

### **スポンサー**：

- [tatra-labs](https://github.com/tatra-labs)

## メンテナー：

 > [Fosowl](https://github.com/Fosowl) | パリ時間 

 > [antoineVIVIES](https://github.com/antoineVIVIES) | 台北時間 

## 特別な感謝：

 > [tcsenpai](https://github.com/tcsenpai) と [plitc](https://github.com/plitc) がバックエンドのDocker化を支援

[![Star History Chart](https://api.star-history.com/svg?repos=Fosowl/agenticSeek&type=Date)](https://www.star-history.com/#Fosowl/agenticSeek&Date)
