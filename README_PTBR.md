# AgenticSeek: Uma Alternativa Privada e Local ao Manus

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek Logo">
<p>

  English | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md) | [Español](./README_ES.md) | [Türkçe](./README_TR.md)

*Um assistente de IA com reconhecimento de voz que é uma **alternativa 100% local ao Manus AI**, navega autonomamente na web, escreve código e planeja tarefas enquanto mantém todos os dados no seu dispositivo. Projetado para modelos de raciocínio local, funciona inteiramente no seu hardware, garantindo total privacidade e zero dependência de nuvem.*

[![Visitar AgenticSeek](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460) [![GitHub stars](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### Por que escolher o AgenticSeek?

* 🔒 Totalmente Local & Privado - Tudo funciona na sua máquina, sem nuvem, sem compartilhamento de dados. Seus arquivos, conversas e pesquisas permanecem privados.

* 🌐 Navegação Web Inteligente - O AgenticSeek pode navegar na Internet autonomamente: pesquisar, ler, extrair informações, preencher formulários web, tudo sem intervenção manual.

* 💻 Assistente de Programação Autônomo - Precisa de código? Ele pode escrever, depurar e executar programas em Python, C, Go, Java e muito mais, sem supervisão.

* 🧠 Seleção Inteligente de Agentes - Você pergunta, ele escolhe automaticamente o melhor agente para a tarefa. Como ter uma equipe de especialistas sempre disponível.

* 📋 Planeja e Executa Tarefas Complexas - Desde o planejamento de viagens até projetos complexos, ele pode decompor grandes tarefas em etapas e completá-las usando múltiplos agentes de IA.

* 🎙️ Suporte de Voz - Voz clara, rápida e futurista com reconhecimento de voz, permitindo que você converse como com sua IA pessoal de filme de ficção científica. (Em desenvolvimento)

### **Demo**

> *Você pode pesquisar o projeto agenticSeek, aprender quais habilidades são necessárias e, em seguida, abrir CV_candidates.zip e me dizer quais correspondem melhor ao projeto?*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

Aviso: Esta demonstração e todos os arquivos que aparecem (ex: CV_candidates.zip) são totalmente fictícios. Não somos uma empresa, estamos procurando contribuidores de código aberto, não candidatos.

> 🛠⚠️️ **Trabalho Ativo em Andamento**

> 🙏 Este projeto começou como um projeto paralelo e não tem roadmap nem financiamento. Cresceu muito além das expectativas ao aparecer no GitHub Trending. Contribuições, comentários e paciência são profundamente apreciados.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

*   **Git:** Para clonar o repositório. [Baixar Git](https://git-scm.com/downloads)
*   **Python 3.10.x:** Python 3.10.x é altamente recomendado. Outras versões podem causar erros de dependência. [Baixar Python 3.10](https://www.python.org/downloads/release/python-3100/) (selecione a versão 3.10.x).
*   **Docker Engine & Docker Compose:** Para executar serviços empacotados como SearxNG.
    *   Instalar Docker Desktop (inclui Docker Compose V2): [Windows](https://docs.docker.com/desktop/install/windows-install/) | [Mac](https://docs.docker.com/desktop/install/mac-install/) | [Linux](https://docs.docker.com/desktop/install/linux-install/)
    *   Ou instalar Docker Engine e Docker Compose separadamente no Linux: [Docker Engine](https://docs.docker.com/engine/install/) | [Docker Compose](https://docs.docker.com/compose/install/) (certifique-se de instalar Compose V2, por exemplo `sudo apt-get install docker-compose-plugin`).

### 1. **Clonar o repositório e configurar**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2. Modificar o conteúdo do arquivo .env

```sh
SEARXNG_BASE_URL="http://searxng:8080" # o valor depende de onde o backend é executado — veja a nota sobre SEARXNG abaixo
SEARXNG_PORT=8080
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

Atualize o arquivo `.env` conforme necessário:

- **SEARXNG_PORT**: A porta do **host** na qual o Docker publica o SearXNG. Se a porta `8080` já estiver ocupada na sua máquina, defina outra (por exemplo, `8001`). Dentro do Docker, o contêiner sempre escuta na porta `8080` — esta variável nunca altera isso.
- **SEARXNG_BASE_URL**: O endereço que o **backend** usa para acessar o SearXNG. Ele é definido aqui no `.env` (não no `config.ini`) e depende apenas de onde o backend é executado:

| Como você executa o AgenticSeek | `SEARXNG_BASE_URL` |
|---|---|
| Interface web — backend no Docker (`./start_services.sh full`) | `http://searxng:8080` — sempre a porta `8080`, mesmo que você tenha alterado `SEARXNG_PORT` |
| Modo CLI — backend no host (`uv run cli.py`) | `http://localhost:8080` — se você alterou `SEARXNG_PORT`, use essa porta no lugar (por exemplo, `http://localhost:8001`). `http://searxng:...` **não** funciona aqui: esse hostname só existe dentro do Docker |

> Para verificar o SearXNG em um navegador, use sempre a porta do host: `http://localhost:<SEARXNG_PORT>`. Depois de alterar o `.env`, reinicie o backend — o arquivo só é lido na inicialização do processo.
- **REDIS_BASE_URL**: Mantenha inalterado 
- **WORK_DIR**: Caminho para o diretório de trabalho local. O AgenticSeek poderá ler e interagir com esses arquivos.
- **OLLAMA_PORT**: Número da porta para o serviço Ollama.
- **LM_STUDIO_PORT**: Número da porta para o serviço LM Studio.
- **CUSTOM_ADDITIONAL_LLM_PORT**: Porta para qualquer serviço LLM personalizado adicional.

**As chaves de API são completamente opcionais para aqueles que optam por executar LLM localmente, que é o objetivo principal deste projeto. Deixe-as vazias se você tiver hardware suficiente.**

### 3. **Iniciar o Docker**

Certifique-se de que o Docker está instalado e funcionando no seu sistema. Você pode iniciar o Docker com os seguintes comandos:

- **Linux/macOS:**  
    Abra um terminal e execute:
    ```sh
    sudo systemctl start docker
    ```
    Ou inicie o Docker Desktop a partir do menu de aplicativos, se instalado.

- **Windows:**  
    Inicie o Docker Desktop a partir do menu Iniciar.

Você pode verificar se o Docker está funcionando executando:
```sh
docker info
```
Se você vir informações sobre sua instalação do Docker, ele está funcionando corretamente.

Consulte a [Lista de provedores locais](#lista-de-provedores-locais) abaixo para um resumo.

Próxima etapa: [Executar o AgenticSeek localmente](#iniciar-os-serviços-e-executar)

*Se você encontrar problemas, consulte a seção [Solução de problemas](#solução-de-problemas).*
*Se seu hardware não puder executar LLM localmente, consulte [Configuração para executar com uma API](#configuração-para-executar-com-uma-api).*
*Para explicações detalhadas do `config.ini`, consulte a [seção Configuração](#configuração).*

---

## Configuração para executar LLM localmente na sua máquina

**Requisitos de hardware:**

Para executar LLM localmente, você precisará de hardware suficiente. No mínimo, uma GPU capaz de executar Magistral, Qwen ou Deepseek 14B é necessária. Consulte o FAQ para recomendações detalhadas de modelo/desempenho.

**Configure seu provedor local**  

Inicie seu provedor local, por exemplo com ollama:

```sh
ollama serve
```

Consulte a lista de provedores locais suportados abaixo.

**Atualizar config.ini**

Altere o arquivo config.ini para definir provider_name como um provedor suportado e provider_model como um LLM suportado pelo seu provedor. Recomendamos modelos de raciocínio como *Magistral* ou *Deepseek*.

Consulte o **FAQ** no final do README para o hardware necessário.

```sh
[MAIN]
is_local = True # Se você está executando localmente ou com um provedor remoto.
provider_name = ollama # ou lm-studio, openai, etc.
provider_model = deepseek-r1:14b # escolha um modelo compatível com seu hardware
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # o nome da sua IA
recover_last_session = True # recuperar a sessão anterior
save_session = True # memorizar a sessão atual
speak = False # texto para fala
listen = False # fala para texto, apenas para CLI, experimental
jarvis_personality = False # usar uma personalidade mais "Jarvis" (experimental)
languages = en zh # Lista de idiomas, TTS usará o primeiro da lista por padrão
[BROWSER]
headless_browser = True # mantenha inalterado, a menos que use CLI no host.
stealth_mode = True # Use selenium indetectável para reduzir a detecção do navegador
```

**Aviso**:

- O formato do arquivo `config.ini` não suporta comentários.
Não copie e cole diretamente a configuração de exemplo, pois os comentários causarão erros. Em vez disso, modifique manualmente o arquivo `config.ini` com sua configuração desejada, sem comentários.

- *NÃO* defina provider_name como `openai` se você estiver usando LM-studio para executar LLM. Use-o como `lm-studio`.

- Alguns provedores (ex: lm-studio) exigem `http://` antes do IP. Exemplo: `http://127.0.0.1:1234`

**Lista de provedores locais**

| Provedor  | Local ? | Descrição                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | Sim    | Executa LLM localmente facilmente usando ollama |
| lm-studio  | Sim    | Executa LLM localmente com LM studio (defina `provider_name` = `lm-studio`)|
| openai    | Sim     |  Use uma API compatível com openai (ex: servidor llama.cpp)  |

Próxima etapa: [Iniciar os serviços e executar o AgenticSeek](#iniciar-os-serviços-e-executar)  

*Se você encontrar problemas, consulte a seção [Solução de problemas](#solução-de-problemas).*
*Se seu hardware não puder executar LLM localmente, consulte [Configuração para executar com uma API](#configuração-para-executar-com-uma-api).*
*Para explicações detalhadas do `config.ini`, consulte a [seção Configuração](#configuração).*

## Configuração para executar com uma API

Esta configuração usa provedores de LLM externos baseados em nuvem. Você precisará obter chaves de API do serviço escolhido.

**1. Escolha um provedor de API e obtenha uma chave de API:**

Consulte a [Lista de provedores de API](#lista-de-provedores-de-api) abaixo. Visite seus sites para se inscrever e obter chaves de API.

**2. Defina sua chave de API como variável de ambiente:**

*   **Linux/macOS:**
    Abra um terminal e use o comando `export`. É melhor adicioná-lo ao arquivo de configuração do seu shell (ex: `~/.bashrc`, `~/.zshrc`) para que seja persistente.
    ```sh
    export PROVIDER_API_KEY="your_api_key_here" 
    # Substitua PROVIDER_API_KEY pelo nome de variável específico, ex: OPENAI_API_KEY, GOOGLE_API_KEY
    ```
    Exemplo TogetherAI:
    ```sh
    export TOGETHER_API_KEY="xxxxxxxxxxxxxxxxxxxxxx"
    ```
*   **Windows:**
    *   **Prompt de comando (temporário para a sessão atual):**
        ```cmd
        set PROVIDER_API_KEY=your_api_key_here
        ```
    *   **PowerShell (temporário para a sessão atual):**
        ```powershell
        $env:PROVIDER_API_KEY="your_api_key_here"
        ```
    *   **Permanente:** Pesquise "variáveis de ambiente" na barra de pesquisa do Windows, clique em "Editar variáveis de ambiente do sistema" e depois no botão "Variáveis de ambiente...". Adicione uma nova variável de usuário com o nome apropriado (ex: `OPENAI_API_KEY`) e sua chave como valor.

    *(Para mais detalhes, consulte o FAQ: [Como configurar uma chave de API?](#como-configurar-uma-chave-de-api)).*


**3. Atualize `config.ini`:**
```ini
[MAIN]
is_local = False
provider_name = openai # ou google, deepseek, togetherAI, huggingface
provider_model = gpt-3.5-turbo # ou gemini-1.5-flash, deepseek-chat, mistralai/Mixtral-8x7B-Instruct-v0.1, etc.
provider_server_address = # Quando is_local = False, geralmente ignorado ou pode ser deixado vazio para a maioria das APIs
# ... outras configurações ...
```
*Aviso:* Certifique-se de que não há espaços no final dos valores no config.

**Lista de provedores de API**

| Provedor     | `provider_name` | Local ? | Descrição                                       | Link da chave de API (exemplo)                     |
|--------------|-----------------|--------|---------------------------------------------------|---------------------------------------------|
| OpenAI       | `openai`        | Não     | Use os modelos ChatGPT via API OpenAI.              | [platform.openai.com/signup](https://platform.openai.com/signup) |
| Google Gemini| `google`        | Não     | Use os modelos Google Gemini via Google AI Studio.    | [aistudio.google.com/keys](https://aistudio.google.com/keys) |
| Deepseek     | `deepseek`      | Não     | Use os modelos Deepseek via sua API.                | [platform.deepseek.com](https://platform.deepseek.com) |
| Hugging Face | `huggingface`   | Não     | Use modelos do Hugging Face Inference API.       | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| TogetherAI   | `togetherAI`    | Não     | Use vários modelos open source via API TogetherAI.| [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) |

*Nota:*
*   Não recomendamos usar `gpt-4o` ou outros modelos OpenAI para navegação web complexa e planejamento de tarefas, pois a otimização atual de prompts visa modelos como Deepseek.
*   Tarefas de codificação/bash podem falhar com Gemini, pois tende a ignorar nosso formato de prompt otimizado para Deepseek r1.
*   Quando `is_local = False`, `provider_server_address` no `config.ini` geralmente não é usado, pois os endpoints de API são geralmente gerenciados pelas bibliotecas do provedor correspondente.

Próxima etapa: [Iniciar os serviços e executar o AgenticSeek](#iniciar-os-serviços-e-executar)

*Se você encontrar problemas, consulte a seção **Problemas conhecidos***

*Para explicações detalhadas do arquivo de configuração, consulte a **seção Configuração**.*

---

## Iniciar os serviços e executar

Por padrão, o AgenticSeek é executado inteiramente no Docker.

**Opção 1:** Executar no Docker com interface web:

Inicie os serviços necessários. Isso iniciará todos os serviços do docker-compose.yml, incluindo:
    - searxng
    - redis (necessário para searxng)
    - frontend
    - backend (se você usar `full` para a interface web)

```sh
./start_services.sh full # MacOS
start start_services.cmd full # Windows
```

**Aviso:** Esta etapa baixará e carregará todas as imagens do Docker, o que pode levar até 30 minutos. Depois de iniciar os serviços, aguarde até que o serviço backend esteja totalmente operacional (você deve ver **backend: "GET /health HTTP/1.1" 200 OK** nos logs) antes de enviar mensagens. Na primeira inicialização, o serviço backend pode levar 5 minutos para iniciar.

Vá para `http://localhost:3000/` e você deve ver a interface web.

*Solução de problemas de inicialização de serviços:* Se esses scripts falharem, certifique-se de que o Docker Engine está funcionando e que o Docker Compose (V2, `docker compose`) está instalado corretamente. Verifique as mensagens de erro na saída do terminal. Consulte [FAQ: Ajuda! Estou recebendo erros ao executar o AgenticSeek ou seus scripts.](#faq-solução-de-problemas)

**Opção 2:** Modo CLI:

Para executar com a interface CLI, você precisa instalar os pacotes no host:

```sh
./install.sh
./install.bat # windows
```

Em seguida, você precisa alterar SEARXNG_BASE_URL no seu arquivo `.env` (**não** no `config.ini`) para o endereço mapeado no host, porque no modo CLI o backend é executado na sua máquina, fora do Docker:

```sh
SEARXNG_BASE_URL="http://localhost:8080"
```

> Se você alterou `SEARXNG_PORT` no `.env`, use essa porta aqui no lugar (por exemplo, `http://localhost:8001`). Reinicie o `cli.py` depois de editar o `.env` — o valor é lido na inicialização.

Inicie os serviços necessários. Isso iniciará alguns serviços do docker-compose.yml, incluindo:
    - searxng
    - redis (necessário para searxng)
    - frontend

```sh
./start_services.sh # MacOS
start start_services.cmd # Windows
```

Execute: uv run: `uv run python -m ensurepip` para garantir que o uv tenha o pip ativado.

Use CLI: `uv run cli.py`

---

## Uso

Certifique-se de que os serviços estão funcionando com `./start_services.sh full` e vá para `localhost:3000` para a interface web.

Você também pode usar fala para texto definindo `listen = True`. Apenas para o modo CLI.

Para sair, basta dizer/digitar `goodbye`.

Alguns exemplos de uso:

> *Faça um jogo da cobra em python!*

> *Pesquise na web os melhores cafés em Rennes, França, e salve uma lista de três com seus endereços em rennes_cafes.txt.*

> *Escreva um programa Go para calcular o fatorial de um número, salve-o como factorial.go em seu workspace*

> *Pesquise na pasta summer_pictures todos os arquivos JPG, renomeie-os com a data de hoje e salve a lista de arquivos renomeados em photos_list.txt*

> *Pesquise online os filmes de ficção científica populares de 2024 e escolha três para assistir esta noite. Salve a lista em movie_night.txt.*

> *Pesquise na web os últimos artigos de notícias sobre IA de 2025, selecione três e escreva um script Python para extrair os títulos e resumos. Salve o script como news_scraper.py e os resumos em ai_news.txt em /home/projects*

> *Sexta-feira, pesquise na web uma API gratuita de preços de ações, inscreva-se com supersuper7434567@gmail.com e escreva um script Python para obter os preços diários da Tesla usando a API, salvando os resultados em stock_prices.csv*

*Observe que o preenchimento de formulários ainda é experimental e pode falhar.*

Depois de inserir sua consulta, o AgenticSeek atribuirá o melhor agente para a tarefa.

Como este é um protótipo inicial, o sistema de roteamento de agentes pode nem sempre atribuir o agente correto à sua consulta.

Portanto, seja muito explícito sobre o que você quer e como a IA pode proceder, por exemplo, se você quiser que ela faça uma pesquisa na web, não diga:

`Você conhece bons países para viajar sozinho?`

Em vez disso, diga:

`Execute uma pesquisa na web e descubra quais são os melhores países para viajar sozinho`

---

## **Configuração para executar LLM em seu próprio servidor**

Se você tem um computador poderoso ou um servidor que pode acessar, mas quer usá-lo do seu laptop, você pode optar por executar o LLM em um servidor remoto usando nosso servidor llm personalizado.

No seu "servidor" que executará o modelo de IA, obtenha o endereço IP

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # IP local
curl https://ipinfo.io/ip # IP público
```

Nota: Para Windows ou macOS, use ipconfig ou ifconfig para encontrar o endereço IP.

Clone o repositório e entre na pasta `server/`.

```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/llm_server/
```

Instale os requisitos específicos do servidor:

```sh
pip3 install -r requirements.txt
```

Execute o script do servidor.

```sh
python3 app.py --provider ollama --port 3333
```

Você pode escolher usar `ollama` e `llamacpp` como serviço LLM.

Agora no seu computador pessoal:

Altere o arquivo `config.ini` para definir `provider_name` como `server` e `provider_model` como `deepseek-r1:xxb`.
Defina `provider_server_address` como o endereço IP da máquina que executará o modelo.

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = http://x.x.x.x:3333
```

Próxima etapa: [Iniciar os serviços e executar o AgenticSeek](#iniciar-os-serviços-e-executar)  

---

## Fala para Texto

Aviso: Fala para texto funciona apenas no modo CLI no momento.

Observe que a fala para texto funciona apenas em inglês no momento.

A funcionalidade de fala para texto está desativada por padrão. Para ativá-la, defina listen como True no arquivo config.ini:

```
listen = True
```

Quando ativada, a funcionalidade de fala para texto ouve uma palavra-chave de gatilho, que é o nome do agente, antes de processar sua entrada. Você pode personalizar o nome do agente atualizando o valor `agent_name` em *config.ini*:

```
agent_name = Friday
```

Para melhor reconhecimento, recomendamos usar um nome comum em inglês como "John" ou "Emma" como nome do agente.

Assim que você vir a transcrição começar a aparecer, diga o nome do agente em voz alta para acordá-lo (ex: "Friday").

Diga sua consulta claramente.

Termine sua solicitação com uma frase de confirmação para indicar ao sistema para continuar. Exemplos de frases de confirmação incluem:
```
"do it", "go ahead", "execute", "run", "start", "thanks", "would ya", "please", "okay?", "proceed", "continue", "go on", "do that", "go it", "do you understand?"
```

## Configuração

Exemplo de configuração:
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = http://127.0.0.1:11434 # Exemplo Ollama; LM-Studio usa http://127.0.0.1:1234
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False

jarvis_personality = False
languages = en zh # Lista de idiomas para TTS e roteamento potencial.
[BROWSER]
headless_browser = False
stealth_mode = False
```

**Explicação das configurações de `config.ini`**:

*   **Seção `[MAIN]`:**
    *   `is_local`: `True` se você estiver usando provedores de LLM locais (Ollama, LM-Studio, servidor local compatível com OpenAI) ou a opção de servidor auto-hospedado. `False` se você estiver usando APIs baseadas em nuvem (OpenAI, Google, etc.).
    *   `provider_name`: Especifica o provedor de LLM.
        *   Opções locais: `ollama`, `lm-studio`, `openai` (para servidor local compatível com OpenAI), `server` (para configuração de servidor auto-hospedado).
        *   Opções de API: `openai`, `google`, `deepseek`, `huggingface`, `togetherAI`.
    *   `provider_model`: Nome ou ID específico do modelo do provedor selecionado (ex: `deepseekcoder:6.7b` para Ollama, `gpt-3.5-turbo` para API OpenAI, `mistralai/Mixtral-8x7B-Instruct-v0.1` para TogetherAI).
    *   `provider_server_address`: O endereço do seu provedor de LLM.
        *   Para provedores locais: ex: `http://127.0.0.1:11434` para Ollama, `http://127.0.0.1:1234` para LM-Studio.
        *   Para o tipo de provedor `server`: O endereço do seu servidor LLM auto-hospedado (ex: `http://your_server_ip:3333`).
        *   Para APIs em nuvem (`is_local = False`): Isso geralmente é ignorado ou pode ser deixado em branco, pois os endpoints da API são geralmente gerenciados pelas bibliotecas do provedor correspondente.
    *   `agent_name`: O nome do assistente de IA (ex: Friday). Se ativado, usado como palavra de gatilho para fala para texto.
    *   `recover_last_session`: `True` para tentar recuperar o estado da sessão anterior, `False` para começar do zero.
    *   `save_session`: `True` para salvar o estado da sessão atual para possível recuperação, `False` caso contrário.
    *   `speak`: `True` para ativar a saída de voz de texto para fala, `False` para desativar.
    *   `listen`: `True` para ativar a entrada de voz de fala para texto (apenas modo CLI), `False` para desativar.
    *   `work_dir`: **Crítico:** O diretório onde o AgenticSeek lerá/escreverá arquivos. **Certifique-se de que este caminho é válido e acessível no seu sistema.**
    *   `jarvis_personality`: `True` para usar prompts de sistema mais "Jarvis-like" (experimental), `False` para usar prompts padrão.
    *   `languages`: Lista de idiomas separados por vírgulas (ex: `en, zh, fr`). Usado para seleção de voz TTS (primeira por padrão) e pode ajudar o roteador LLM. Para evitar ineficiências do roteador, evite usar muitos idiomas ou idiomas muito semelhantes.
*   **Seção `[BROWSER]`:**
    *   `headless_browser`: `True` para executar o navegador automatizado sem janela visível (recomendado para interface web ou uso não interativo). `False` para exibir a janela do navegador (útil para modo CLI ou depuração).
    *   `stealth_mode`: `True` para ativar medidas que tornam mais difícil a detecção da automação do navegador. Pode exigir instalação manual de extensões de navegador como anticaptcha.

Esta seção resume os tipos de provedores de LLM suportados. Configure-os em `config.ini`.

**Provedores locais (executando em seu próprio hardware):**

| Nome do provedor em config.ini | `is_local` | Descrição                                                                 | Seção de configuração                                                    |
|-------------------------------|------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| `ollama`                      | `True`     | Fornece LLM localmente facilmente usando Ollama.                                             | [Configuração para executar LLM localmente na sua máquina](#configuração-para-executar-llm-localmente-na-sua-máquina) |
| `lm-studio`                   | `True`     | Fornece LLM localmente com LM-Studio.                                          | [Configuração para executar LLM localmente na sua máquina](#configuração-para-executar-llm-localmente-na-sua-máquina) |
| `openai` (para servidor local)   | `True`     | Conecte-se a um servidor local expondo uma API compatível com OpenAI (ex: llama.cpp). | [Configuração para executar LLM localmente na sua máquina](#configuração-para-executar-llm-localmente-na-sua-máquina) |
| `server`                      | `False`    | Conecte-se ao servidor LLM auto-hospedado do AgenticSeek em execução em outra máquina. | [Configuração para executar LLM em seu próprio servidor](#configuração-para-executar-llm-em-seu-próprio-servidor) |

**Provedores de API (baseados em nuvem):**

| Nome do provedor em config.ini | `is_local` | Descrição                                      | Seção de configuração                                       |
|-------------------------------|------------|--------------------------------------------------|-----------------------------------------------------|
| `openai`                      | `False`    | Use a API oficial da OpenAI (ex: GPT-3.5, GPT-4). | [Configuração para executar com uma API](#configuração-para-executar-com-uma-api) |
| `google`                      | `False`    | Use os modelos Google Gemini via API.              | [Configuração para executar com uma API](#configuração-para-executar-com-uma-api) |
| `deepseek`                    | `False`    | Use a API oficial da Deepseek.                     | [Configuração para executar com uma API](#configuração-para-executar-com-uma-api) |
| `huggingface`                 | `False`    | Use Hugging Face Inference API.                  | [Configuração para executar com uma API](#configuração-para-executar-com-uma-api) |
| `togetherAI`                  | `False`    | Use vários modelos abertos via API TogetherAI.    | [Configuração para executar com uma API](#configuração-para-executar-com-uma-api) |

---
## Solução de problemas

Se você encontrar problemas, esta seção fornece orientações.

# Problemas conhecidos

## Problemas do ChromeDriver

**Exemplo de erro:** `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

### Causa raiz
A incompatibilidade de versão do ChromeDriver ocorre quando:
1. A versão do ChromeDriver que você instalou não corresponde à versão do navegador Chrome
2. Em ambientes Docker, `undetected_chromedriver` pode baixar sua própria versão do ChromeDriver, contornando os binários montados

### Etapas de solução

#### 1. Verifique sua versão do Chrome
Abra o Google Chrome → `Configurações > Sobre o Chrome` para encontrar sua versão (ex: "Versão 134.0.6998.88")

#### 2. Baixe o ChromeDriver correspondente

**Para Chrome 115 e superior:** Use [Chrome for Testing API](https://googlechromelabs.github.io/chrome-for-testing/)
- Visite o painel de disponibilidade do Chrome for Testing
- Encontre sua versão do Chrome ou a correspondência disponível mais próxima
- Baixe o ChromeDriver para seu sistema operacional (use Linux64 para ambientes Docker)

**Para versões mais antigas do Chrome:** Use [Downloads legados do ChromeDriver](https://chromedriver.chromium.org/downloads)

![Baixar ChromeDriver do Chrome for Testing](./media/chromedriver_readme.png)

#### 3. Instale o ChromeDriver (escolha um método)

**Método A: Diretório raiz do projeto (recomendado para Docker)**
```bash
# Coloque o binário chromedriver baixado no diretório raiz do projeto
cp path/to/downloaded/chromedriver ./chromedriver
chmod +x ./chromedriver  # Torne-o executável no Linux/macOS
```

**Método B: PATH do sistema**
```bash
# Linux/macOS
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Windows: Coloque chromedriver.exe em uma pasta do PATH
```

#### 4. Verifique a instalação
```bash
# Teste a versão do ChromeDriver
./chromedriver --version
# Ou se estiver no PATH:
chromedriver --version
```

### Instruções específicas do Docker

⚠️ **Importante para usuários do Docker:**
- O método de montagem de volumes do Docker pode não funcionar com o modo furtivo (`undetected_chromedriver`)
- **Solução:** Coloque o ChromeDriver no diretório raiz do projeto como `./chromedriver`
- O aplicativo o detectará automaticamente e usará este binário
- Você deve ver nos logs: `"Using ChromeDriver from project root: ./chromedriver"`

### Dicas de solução de problemas

1. **Ainda há incompatibilidade de versão?**
   - Verifique se o ChromeDriver é executável: `ls -la ./chromedriver`
   - Verifique a versão do ChromeDriver: `./chromedriver --version`
   - Certifique-se de que corresponde à versão do seu navegador Chrome

2. **Problemas com o contêiner Docker?**
   - Verifique os logs do backend: `docker logs backend`
   - Procure a mensagem: `"Using ChromeDriver from project root"`
   - Se não for encontrado, verifique se o arquivo existe e é executável

3. **Versões do Chrome for Testing**
   - Use uma correspondência exata quando possível
   - Para a versão 134.0.6998.88, use o ChromeDriver 134.0.6998.165 (a versão disponível mais próxima)
   - O número da versão principal deve corresponder (134 = 134)

### Matriz de compatibilidade de versões

| Versão do Chrome | Versão do ChromeDriver | Status |
|----------------|---------------------|---------|
| 134.0.6998.x   | 134.0.6998.165     | ✅ Disponível |
| 133.0.6943.x   | 133.0.6943.141     | ✅ Disponível |
| 132.0.6834.x   | 132.0.6834.159     | ✅ Disponível |

*Para a compatibilidade mais recente, consulte o [Painel do Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)*

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

Isso acontece se seu navegador e a versão do chromedriver não corresponderem.

Você precisa navegar para baixar a versão mais recente:

https://developer.chrome.com/docs/chromedriver/downloads

Se você estiver usando o Chrome versão 115 ou superior, vá para:

https://googlechromelabs.github.io/chrome-for-testing/

e baixe a versão do chromedriver correspondente ao seu sistema operacional.

![alt text](./media/chromedriver_readme.png)

Se esta seção estiver incompleta, abra um issue.

##  Problemas de adaptadores de conexão

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:1234/v1/chat/completions'` (nota: a porta pode variar)
```

*   **Causa:** Falta o prefixo `http://` em `provider_server_address` para `lm-studio` (ou outro servidor local compatível com OpenAI semelhante) no `config.ini`, ou ele aponta para a porta errada.
*   **Solução:**
    *   Certifique-se de que o endereço inclui `http://`. O LM-Studio geralmente usa `http://127.0.0.1:1234` por padrão.
    *   `config.ini` correto: `provider_server_address = http://127.0.0.1:1234` (ou sua porta real do servidor LM-Studio).

## URL base do SearxNG não fornecida

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.`
```

Isso pode acontecer se você executar o modo CLI com uma URL base do searxng incorreta.

`SEARXNG_BASE_URL` é definido no `.env` e depende apenas de **onde o backend é executado**:

**Backend no host (modo CLI)**: `SEARXNG_BASE_URL="http://localhost:8080"` — se você alterou `SEARXNG_PORT`, use essa porta no lugar (por exemplo, `http://localhost:8001`). `http://searxng:...` **não** funciona aqui: esse hostname só é resolvido dentro do Docker.

**Backend no Docker (interface web, perfil `full`)**: `SEARXNG_BASE_URL="http://searxng:8080"` — sempre a porta `8080`, mesmo que você tenha alterado `SEARXNG_PORT`; essa variável só remapeia o lado do host.

> **Nota sobre conflitos de porta**: Se a porta `8080` já estiver em uso no seu host, defina `SEARXNG_PORT` (por exemplo, `8001`) no `.env` e, em seguida:
> - Interface web (backend no Docker): mantenha `SEARXNG_BASE_URL="http://searxng:8080"` — a porta interna do Docker não muda.
> - Modo CLI (backend no host): defina `SEARXNG_BASE_URL="http://localhost:8001"` — o valor deve corresponder a `SEARXNG_PORT`.
> - Verificações no navegador: abra `http://localhost:<SEARXNG_PORT>` — o que responder na antiga porta `8080` é alguma outra aplicação, não o SearXNG do AgenticSeek.
>
> Depois de alterar o `.env`, reinicie o backend (`api.py` ou `cli.py`) — o arquivo só é lido na inicialização do processo.

## FAQ

**P: De qual hardware eu preciso?**  

| Tamanho do modelo  | GPU  | Comentários                                               |
|-----------|--------|-----------------------------------------------------------|
| 7B        | 8GB VRAM | ⚠️ Não recomendado. Desempenho ruim, alucinações frequentes, agentes de planejamento podem falhar. |
| 14B        | 12 GB VRAM (ex: RTX 3060) | ✅ Utilizável para tarefas simples. Pode ter dificuldades com navegação web e planejamento de tarefas. |
| 32B        | 24+ GB VRAM (ex: RTX 4090) | 🚀 Consegue a maioria das tarefas, ainda pode ter dificuldades com planejamento de tarefas |
| 70B+        | 48+ GB VRAM | 💪 Excelente. Recomendado para casos de uso avançados. |

**P: O que fazer se eu encontrar erros?**  

Certifique-se de que o local está funcionando (`ollama serve`), que seu `config.ini` corresponde ao seu provedor e que as dependências estão instaladas. Se nada funcionar, sinta-se à vontade para abrir um issue.

**P: Ele pode realmente funcionar 100% localmente?**  

Sim, com os provedores Ollama, lm-studio ou server, todos os modelos de fala para texto, LLM e texto para fala funcionam localmente. As opções não locais (OpenAI ou outras APIs) são opcionais.

**P: Por que eu deveria usar o AgenticSeek quando tenho o Manus?**

Ao contrário do Manus, o AgenticSeek prioriza a independência de sistemas externos, dando a você mais controle, privacidade e evitando custos de API.

**P: Quem está por trás deste projeto?**

Este projeto foi criado por mim, com dois amigos como mantenedores e contribuidores da comunidade de código aberto no GitHub. Somos apenas indivíduos apaixonados, não uma startup, nem afiliados a qualquer organização.

Qualquer conta AgenticSeek no X diferente da minha conta pessoal (https://x.com/Martin993886460) é um impostor.

## Contribuir

Estamos procurando desenvolvedores para melhorar o AgenticSeek! Verifique os problemas abertos ou discussões.

[Guia de contribuição](./docs/CONTRIBUTING.md)

## Patrocinadores:

Você quer melhorar as capacidades do AgenticSeek com recursos como pesquisa de voos, planejamento de viagens ou obtenção das melhores ofertas de compra? Considere usar o SerpApi para criar ferramentas personalizadas que desbloqueiem mais recursos do tipo Jarvis. Com o SerpApi, você pode acelerar seu agente para tarefas profissionais enquanto mantém o controle total.

<a href="https://serpapi.com/"><img src="./media/banners/sponsor_banner_serpapi.png" height="350" alt="SerpApi Banner" ></a>

Confira [Contributing.md](./docs/CONTRIBUTING.md) para aprender como integrar ferramentas personalizadas!

## Mantenedores:

 > [Fosowl](https://github.com/Fosowl) | Horário de Paris 

## Agradecimentos especiais:

 > [tcsenpai](https://github.com/tcsenpai) e [plitc](https://github.com/plitc) por ajudar na dockerização do backend

[![Star History Chart](https://star-history.dera.page/svg?repos=Fosowl/agenticSeek&type=Date)](https://star-history.dera.page/#Fosowl/agenticSeek&Date)
