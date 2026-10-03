# AgenticSeek: Una Alternativa Privada y Local a Manus

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek Logo">
<p>

  English | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md) | [Español](./README_ES.md) | [Türkçe](./README_TR.md)

*Un asistente de IA con capacidad de voz que es una **alternativa 100% local a Manus AI**, navega autónomamente por la web, escribe código y planifica tareas manteniendo todos los datos en tu dispositivo. Diseñado para modelos de razonamiento local, funciona completamente en tu hardware, garantizando privacidad total y cero dependencia de la nube.*

[![Visitar AgenticSeek](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460) [![GitHub stars](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### ¿Por qué AgenticSeek?

* 🔒 Totalmente Local & Privado - Todo funciona en tu máquina, sin nube, sin compartir datos. Tus archivos, conversaciones y búsquedas permanecen privados.

* 🌐 Navegación Web Inteligente - AgenticSeek puede navegar por Internet de forma autónoma: buscar, leer, extraer información, completar formularios web, todo sin manos.

* 💻 Asistente de Programación Autónomo - ¿Necesitas código? Puede escribir, depurar y ejecutar programas en Python, C, Go, Java y más, sin supervisión.

* 🧠 Selección Inteligente de Agentes - Tú pides, él elige automáticamente el mejor agente para la tarea. Como tener un equipo de expertos siempre disponible.

* 📋 Planifica y Ejecuta Tareas Complejas - Desde planificación de viajes hasta proyectos complejos, puede dividir grandes tareas en pasos y completarlos utilizando múltiples agentes de IA.

* 🎙️ Compatibilidad con Voz - Voz limpia, rápida y futurista con reconocimiento de voz, permitiéndote conversar como si fuera tu IA personal de una película de ciencia ficción. (En desarrollo)

### **Demo**

> *¿Puedes buscar el proyecto agenticSeek, aprender qué habilidades se necesitan, luego abrir CV_candidates.zip y decirme cuáles coinciden mejor con el proyecto?*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

Descargo de responsabilidad: Esta demostración y todos los archivos que aparecen (ej: CV_candidates.zip) son completamente ficticios. No somos una corporación, buscamos colaboradores de código abierto, no candidatos.

> 🛠⚠️️ **Trabajo Activo en Progreso**

> 🙏 Este proyecto comenzó como un proyecto paralelo y no tiene hoja de ruta ni financiación. Creció mucho más allá de lo esperado al aparecer en GitHub Trending. Las contribuciones, comentarios y paciencia son profundamente apreciados.

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

*   **Git:** Para clonar el repositorio. [Descargar Git](https://git-scm.com/downloads)
*   **Python 3.10.x:** Se recomienda encarecidamente Python 3.10.x. Otras versiones pueden causar errores de dependencia. [Descargar Python 3.10](https://www.python.org/downloads/release/python-3100/) (selecciona la versión 3.10.x).
*   **Docker Engine & Docker Compose:** Para ejecutar servicios empaquetados como SearxNG.
    *   Instalar Docker Desktop (incluye Docker Compose V2): [Windows](https://docs.docker.com/desktop/install/windows-install/) | [Mac](https://docs.docker.com/desktop/install/mac-install/) | [Linux](https://docs.docker.com/desktop/install/linux-install/)
    *   O instalar Docker Engine y Docker Compose por separado en Linux: [Docker Engine](https://docs.docker.com/engine/install/) | [Docker Compose](https://docs.docker.com/compose/install/) (asegúrate de instalar Compose V2, por ejemplo `sudo apt-get install docker-compose-plugin`).

### 1. **Clonar el repositorio y configurar**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2. Modificar el contenido del archivo .env

```sh
SEARXNG_BASE_URL="http://searxng:8080" # el valor depende de dónde se ejecute el backend — consulta la nota sobre SEARXNG más abajo
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

Actualiza el archivo `.env` según sea necesario:

- **SEARXNG_PORT**: El puerto del **host** en el que Docker publica SearXNG. Si el puerto `8080` ya está ocupado en tu máquina, establece otro (por ejemplo, `8001`). Dentro de Docker el contenedor siempre escucha en `8080` — esta variable nunca cambia eso.
- **SEARXNG_BASE_URL**: La dirección que el **backend** usa para conectarse a SearXNG. Se configura aquí, en `.env` (no en `config.ini`), y depende únicamente de dónde se ejecute el backend:

| Cómo ejecutas AgenticSeek | `SEARXNG_BASE_URL` |
|---|---|
| Interfaz web — backend en Docker (`./start_services.sh full`) | `http://searxng:8080` — siempre el puerto `8080`, incluso si cambiaste `SEARXNG_PORT` |
| Modo CLI — backend en el host (`uv run cli.py`) | `http://localhost:8080` — si cambiaste `SEARXNG_PORT`, usa ese puerto en su lugar (por ejemplo, `http://localhost:8001`). `http://searxng:...` **no** funciona aquí: ese nombre de host solo existe dentro de Docker |

> Para comprobar SearXNG en un navegador, usa siempre el puerto del host: `http://localhost:<SEARXNG_PORT>`. Después de cambiar `.env`, reinicia el backend — el archivo solo se lee al iniciar el proceso.
- **REDIS_BASE_URL**: Mantener sin cambios 
- **WORK_DIR**: Ruta al directorio de trabajo local. AgenticSeek podrá leer e interactuar con estos archivos.
- **OLLAMA_PORT**: Número de puerto para el servicio Ollama.
- **LM_STUDIO_PORT**: Número de puerto para el servicio LM Studio.
- **CUSTOM_ADDITIONAL_LLM_PORT**: Puerto para cualquier servicio LLM adicional personalizado.

**Las claves API son completamente opcionales para quienes optan por ejecutar LLM localmente, que es el objetivo principal de este proyecto. Déjalas en blanco si tienes hardware suficiente.**

### 3. **Iniciar Docker**

Asegúrate de que Docker esté instalado y ejecutándose en tu sistema. Puedes iniciar Docker con los siguientes comandos:

- **Linux/macOS:**  
    Abre una terminal y ejecuta:
    ```sh
    sudo systemctl start docker
    ```
    O inicia Docker Desktop desde el menú de aplicaciones, si está instalado.

- **Windows:**  
    Inicia Docker Desktop desde el menú Inicio.

Puedes verificar si Docker se está ejecutando ejecutando:
```sh
docker info
```
Si ves información sobre tu instalación de Docker, está funcionando correctamente.

Consulta la [Lista de proveedores locales](#lista-de-proveedores-locales) a continuación para obtener un resumen.

Siguiente paso: [Ejecutar AgenticSeek localmente](#iniciar-servicios-y-ejecutar)

*Si tienes problemas, consulta la sección [Solución de problemas](#solución-de-problemas).*
*Si tu hardware no puede ejecutar LLM localmente, consulta [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api).*
*Para explicaciones detalladas de `config.ini`, consulta la [sección Configuración](#configuración).*

---

## Configuración para ejecutar LLM localmente en tu máquina

**Requisitos de hardware:**

Para ejecutar LLM localmente, necesitarás hardware suficiente. Como mínimo, se requiere una GPU capaz de ejecutar Magistral, Qwen o Deepseek 14B. Consulta el FAQ para recomendaciones detalladas de modelo/rendimiento.

**Configura tu proveedor local**  

Inicia tu proveedor local, por ejemplo con ollama:

```sh
ollama serve
```

Consulta la lista de proveedores locales admitidos a continuación.

**Actualizar config.ini**

Cambia el archivo config.ini para establecer provider_name en un proveedor admitido y provider_model en un LLM admitido por tu proveedor. Recomendamos modelos de razonamiento como *Magistral* o *Deepseek*.

Consulta el **FAQ** al final del README para el hardware necesario.

```sh
[MAIN]
is_local = True # Ya sea que ejecutes localmente o con un proveedor remoto.
provider_name = ollama # o lm-studio, openai, etc.
provider_model = deepseek-r1:14b # elige un modelo compatible con tu hardware
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # el nombre de tu IA
recover_last_session = True # recuperar sesión anterior
save_session = True # recordar sesión actual
speak = False # texto a voz
listen = False # voz a texto, solo para CLI, experimental
jarvis_personality = False # usar personalidad más "Jarvis" (experimental)
languages = en zh # Lista de idiomas, TTS usará el primero de la lista por defecto
[BROWSER]
headless_browser = True # mantener sin cambios a menos que uses CLI en el host.
stealth_mode = True # Usa selenium indetectable para reducir la detección del navegador
```

**Advertencia**:

- El formato del archivo `config.ini` no admite comentarios.
No copies y pegues la configuración de ejemplo directamente, ya que los comentarios causarán errores. En su lugar, modifica manualmente el archivo `config.ini` con tu configuración deseada, sin comentarios.

- *NO* establezcas provider_name como `openai` si estás usando LM-studio para ejecutar LLM. Úsalo como `lm-studio`.

- Algunos proveedores (ej: lm-studio) requieren `http://` antes de la IP. Ejemplo: `http://127.0.0.1:1234`

**Lista de proveedores locales**

| Proveedor  | ¿Local? | Descripción                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | Sí    | Ejecuta LLM localmente fácilmente usando ollama |
| lm-studio  | Sí    | Ejecuta LLM localmente con LM studio (establecer `provider_name` = `lm-studio`)|
| openai    | Sí     |  Usa API compatible con openai (ej: servidor llama.cpp)  |

Siguiente paso: [Iniciar servicios y ejecutar AgenticSeek](#iniciar-servicios-y-ejecutar)  

*Si tienes problemas, consulta la sección [Solución de problemas](#solución-de-problemas).*
*Si tu hardware no puede ejecutar LLM localmente, consulta [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api).*
*Para explicaciones detalladas de `config.ini`, consulta la [sección Configuración](#configuración).*

## Configuración para ejecutar con una API

Esta configuración utiliza proveedores de LLM externos basados en la nube. Necesitarás obtener claves API del servicio elegido.

**1. Elige un proveedor de API y obtén una clave API:**

Consulta la [Lista de proveedores de API](#lista-de-proveedores-de-api) a continuación. Visita sus sitios web para registrarte y obtener claves API.

**2. Establece tu clave API como variable de entorno:**

*   **Linux/macOS:**
    Abre una terminal y usa el comando `export`. Es mejor agregarlo al archivo de configuración de tu shell (ej: `~/.bashrc`, `~/.zshrc`) para que sea persistente.
    ```sh
    export PROVIDER_API_KEY="your_api_key_here" 
    # Reemplaza PROVIDER_API_KEY con el nombre de variable específico, ej: OPENAI_API_KEY, GOOGLE_API_KEY
    ```
    Ejemplo de TogetherAI:
    ```sh
    export TOGETHER_API_KEY="xxxxxxxxxxxxxxxxxxxxxx"
    ```
*   **Windows:**
    *   **Símbolo del sistema (temporal para la sesión actual):**
        ```cmd
        set PROVIDER_API_KEY=your_api_key_here
        ```
    *   **PowerShell (temporal para la sesión actual):**
        ```powershell
        $env:PROVIDER_API_KEY="your_api_key_here"
        ```
    *   **Permanente:** Busca "variables de entorno" en la barra de búsqueda de Windows, haz clic en "Editar las variables de entorno del sistema", luego en el botón "Variables de entorno...". Agrega una nueva variable de usuario con el nombre apropiado (ej: `OPENAI_API_KEY`) y tu clave como valor.

    *(Para más detalles, consulta el FAQ: [¿Cómo configuro una clave API?](#cómo-configuro-una-clave-api)).*


**3. Actualiza `config.ini`:**
```ini
[MAIN]
is_local = False
provider_name = openai # o google, deepseek, togetherAI, huggingface
provider_model = gpt-3.5-turbo # o gemini-1.5-flash, deepseek-chat, mistralai/Mixtral-8x7B-Instruct-v0.1, etc.
provider_server_address = # Cuando is_local = False, generalmente se ignora o puede dejarse en blanco para la mayoría de las API
# ... otras configuraciones ...
```
*Advertencia:* Asegúrate de que no haya espacios al final de los valores en config.

**Lista de proveedores de API**

| Proveedor     | `provider_name` | ¿Local? | Descripción                                       | Enlace de clave API (ejemplo)                     |
|--------------|-----------------|--------|---------------------------------------------------|---------------------------------------------|
| OpenAI       | `openai`        | No     | Usa modelos ChatGPT a través de la API de OpenAI.              | [platform.openai.com/signup](https://platform.openai.com/signup) |
| Google Gemini| `google`        | No     | Usa modelos Google Gemini a través de Google AI Studio.    | [aistudio.google.com/keys](https://aistudio.google.com/keys) |
| Deepseek     | `deepseek`      | No     | Usa modelos Deepseek a través de su API.                | [platform.deepseek.com](https://platform.deepseek.com) |
| Hugging Face | `huggingface`   | No     | Usa modelos del Hugging Face Inference API.       | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| TogetherAI   | `togetherAI`    | No     | Usa varios modelos de código abierto a través de la API de TogetherAI.| [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) |

*Nota:*
*   No recomendamos usar `gpt-4o` u otros modelos OpenAI para navegación web compleja y planificación de tareas, ya que la optimización actual de prompts está dirigida a modelos como Deepseek.
*   Las tareas de codificación/bash pueden fallar con Gemini, ya que tiende a ignorar nuestro formato de prompt optimizado para Deepseek r1.
*   Cuando `is_local = False`, `provider_server_address` en `config.ini` generalmente no se usa, ya que los endpoints de API suelen estar codificados en las bibliotecas del proveedor correspondiente.

Siguiente paso: [Iniciar servicios y ejecutar AgenticSeek](#iniciar-servicios-y-ejecutar)

*Si tienes problemas, consulta la sección **Problemas conocidos***

*Para explicaciones detalladas del archivo de configuración, consulta la **sección Configuración**.*

---

## Iniciar servicios y ejecutar

Por defecto, AgenticSeek se ejecuta completamente en Docker.

**Opción 1:** Ejecutar en Docker con interfaz web:

Inicia los servicios necesarios. Esto iniciará todos los servicios del docker-compose.yml, incluyendo:
    - searxng
    - redis (requerido para searxng)
    - frontend
    - backend (si usas `full` para la interfaz web)

```sh
./start_services.sh full # MacOS
start start_services.cmd full # Windows
```

**Advertencia:** Este paso descargará y cargará todas las imágenes de Docker, lo que puede tardar hasta 30 minutos. Después de iniciar los servicios, espera hasta que el servicio backend esté completamente ejecutándose (deberías ver **backend: "GET /health HTTP/1.1" 200 OK** en el registro) antes de enviar cualquier mensaje. En la primera ejecución, el servicio backend puede tardar 5 minutos en iniciarse.

Ve a `http://localhost:3000/` y deberías ver la interfaz web.

*Solución de problemas de inicio de servicios:* Si estos scripts fallan, asegúrate de que Docker Engine esté ejecutándose y que Docker Compose (V2, `docker compose`) esté correctamente instalado. Revisa los mensajes de error en la salida de la terminal. Consulta [FAQ: ¡Ayuda! Obtengo errores al ejecutar AgenticSeek o sus scripts.](#faq-solución-de-problemas)

**Opción 2:** Modo CLI:

Para ejecutar con la interfaz CLI, debes instalar los paquetes en el host:

```sh
./install.sh
./install.bat # windows
```

Luego debes cambiar SEARXNG_BASE_URL en tu archivo `.env` (**no** en `config.ini`) a la dirección mapeada al host, porque en modo CLI el backend se ejecuta en tu máquina, fuera de Docker:

```sh
SEARXNG_BASE_URL="http://localhost:8080"
```

> Si cambiaste `SEARXNG_PORT` en `.env`, usa ese puerto aquí en su lugar (por ejemplo, `http://localhost:8001`). Reinicia `cli.py` después de editar `.env` — el valor se lee al arrancar.

Inicia los servicios necesarios. Esto iniciará algunos servicios del docker-compose.yml, incluyendo:
    - searxng
    - redis (requerido para searxng)
    - frontend

```sh
./start_services.sh # MacOS
start start_services.cmd # Windows
```

Ejecuta: uv run: `uv run python -m ensurepip` para asegurarte de que uv tenga pip habilitado.

Usa CLI: `uv run cli.py`

---

## Uso

Asegúrate de que los servicios estén ejecutándose con `./start_services.sh full` y luego ve a `localhost:3000` para la interfaz web.

También puedes usar voz a texto configurando `listen = True`. Solo para modo CLI.

Para salir, simplemente di/escribe `goodbye`.

Algunos ejemplos de uso:

> *¡Haz un juego de la serpiente en python!*

> *Busca en la web los mejores cafés en Rennes, Francia, y guarda una lista de tres con sus direcciones en rennes_cafes.txt.*

> *Escribe un programa Go para calcular el factorial de un número, guárdalo como factorial.go en tu workspace*

> *Busca en la carpeta summer_pictures todos los archivos JPG, renómbralos con la fecha de hoy y guarda la lista de archivos renombrados en photos_list.txt*

> *Busca en línea películas de ciencia ficción populares de 2024 y elige tres para ver esta noche. Guarda la lista en movie_night.txt.*

> *Busca en la web los últimos artículos de noticias de IA de 2025, selecciona tres y escribe un script Python para extraer títulos y resúmenes. Guarda el script como news_scraper.py y los resúmenes en ai_news.txt en /home/projects*

> *Viernes, busca en la web una API gratuita de precios de acciones, regístrate con supersuper7434567@gmail.com y escribe un script Python para obtener los precios diarios de Tesla usando la API, guardando los resultados en stock_prices.csv*

*Ten en cuenta que el llenado de formularios sigue siendo experimental y puede fallar.*

Después de ingresar tu consulta, AgenticSeek asignará el mejor agente para la tarea.

Como este es un prototipo inicial, el sistema de enrutamiento de agentes puede no asignar siempre el agente correcto a tu consulta.

Por lo tanto, sé muy explícito sobre lo que quieres y cómo la IA podría proceder, por ejemplo, si quieres que realice una búsqueda web, no digas:

`¿Conoces algunos buenos países para viajar solo?`

En su lugar, di:

`Realiza una búsqueda web y descubre cuáles son los mejores países para viajar solo`

---

## **Configuración para ejecutar LLM en tu propio servidor**

Si tienes una computadora potente o un servidor al que puedes acceder, pero quieres usarlo desde tu laptop, puedes optar por ejecutar el LLM en un servidor remoto usando nuestro servidor llm personalizado.

En tu "servidor" que ejecutará el modelo de IA, obtén la dirección IP

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # IP local
curl https://ipinfo.io/ip # IP pública
```

Nota: Para Windows o macOS, usa ipconfig o ifconfig para encontrar la dirección IP.

Clona el repositorio y entra en la carpeta `server/`.

```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/llm_server/
```

Instala los requisitos específicos del servidor:

```sh
pip3 install -r requirements.txt
```

Ejecuta el script del servidor.

```sh
python3 app.py --provider ollama --port 3333
```

Puedes elegir entre usar `ollama` y `llamacpp` como servicio LLM.

Ahora en tu computadora personal:

Cambia el archivo `config.ini` para establecer `provider_name` como `server` y `provider_model` como `deepseek-r1:xxb`.
Establece `provider_server_address` a la dirección IP de la máquina que ejecutará el modelo.

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = http://x.x.x.x:3333
```

Siguiente paso: [Iniciar servicios y ejecutar AgenticSeek](#iniciar-servicios-y-ejecutar)  

---

## Voz a Texto

Advertencia: La voz a texto solo funciona en modo CLI en este momento.

Ten en cuenta que la voz a texto solo funciona en inglés en este momento.

La funcionalidad de voz a texto está deshabilitada por defecto. Para habilitarla, establece listen en True en el archivo config.ini:

```
listen = True
```

Cuando está habilitado, la función de voz a texto escucha una palabra clave de activación, que es el nombre del agente, antes de procesar tu entrada. Puedes personalizar el nombre del agente actualizando el valor `agent_name` en *config.ini*:

```
agent_name = Friday
```

Para un mejor reconocimiento, recomendamos usar un nombre común en inglés como "John" o "Emma" como nombre de agente.

Una vez que veas que comienza a aparecer la transcripción, di el nombre del agente en voz alta para activarlo (ej: "Friday").

Di tu consulta claramente.

Termina tu solicitud con una frase de confirmación para indicar al sistema que proceda. Ejemplos de frases de confirmación incluyen:
```
"do it", "go ahead", "execute", "run", "start", "thanks", "would ya", "please", "okay?", "proceed", "continue", "go on", "do that", "go it", "do you understand?"
```

## Configuración

Ejemplo de configuración:
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = http://127.0.0.1:11434 # Ejemplo de Ollama; LM-Studio usa http://127.0.0.1:1234
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False

jarvis_personality = False
languages = en zh # Lista de idiomas para TTS y enrutamiento potencial.
[BROWSER]
headless_browser = False
stealth_mode = False
```

**Explicación de la configuración de `config.ini`**:

*   **Sección `[MAIN]`:**
    *   `is_local`: `True` si usas proveedores de LLM locales (Ollama, LM-Studio, servidor local compatible con OpenAI) o la opción de servidor autoalojado. `False` si usas API basadas en la nube (OpenAI, Google, etc.).
    *   `provider_name`: Especifica el proveedor de LLM.
        *   Opciones locales: `ollama`, `lm-studio`, `openai` (para servidor local compatible con OpenAI), `server` (para configuración de servidor autoalojado).
        *   Opciones de API: `openai`, `google`, `deepseek`, `huggingface`, `togetherAI`.
    *   `provider_model`: Nombre o ID específico del modelo del proveedor seleccionado (ej: `deepseekcoder:6.7b` para Ollama, `gpt-3.5-turbo` para API de OpenAI, `mistralai/Mixtral-8x7B-Instruct-v0.1` para TogetherAI).
    *   `provider_server_address`: La dirección de tu proveedor de LLM.
        *   Para proveedores locales: ej: `http://127.0.0.1:11434` para Ollama, `http://127.0.0.1:1234` para LM-Studio.
        *   Para el tipo de proveedor `server`: La dirección de tu servidor LLM autoalojado (ej: `http://your_server_ip:3333`).
        *   Para API en la nube (`is_local = False`): Esto generalmente se ignora o puede dejarse en blanco, ya que los endpoints de API suelen ser manejados por las bibliotecas del cliente.
    *   `agent_name`: El nombre del asistente de IA (ej: Friday). Si está habilitado, se utiliza como palabra de activación para voz a texto.
    *   `recover_last_session`: `True` para intentar recuperar el estado de la sesión anterior, `False` para comenzar de nuevo.
    *   `save_session`: `True` para guardar el estado de la sesión actual para una posible recuperación, `False` en caso contrario.
    *   `speak`: `True` para habilitar la salida de voz de texto a voz, `False` para deshabilitar.
    *   `listen`: `True` para habilitar la entrada de voz de voz a texto (solo modo CLI), `False` para deshabilitar.
    *   `work_dir`: **Crítico:** El directorio donde AgenticSeek leerá/escribirá archivos. **Asegúrate de que esta ruta sea válida y accesible en tu sistema.**
    *   `jarvis_personality`: `True` para usar prompts del sistema más al estilo "Jarvis" (experimental), `False` para usar prompts estándar.
    *   `languages`: Lista de idiomas separados por comas (ej: `en, zh, fr`). Se utiliza para la selección de voz TTS (predeterminado el primero) y puede ayudar al enrutador LLM. Para evitar ineficiencias del enrutador, evita usar demasiados idiomas o idiomas muy similares.
*   **Sección `[BROWSER]`:**
    *   `headless_browser`: `True` para ejecutar el navegador automatizado sin una ventana visible (recomendado para interfaz web o uso no interactivo). `False` para mostrar la ventana del navegador (útil para modo CLI o depuración).
    *   `stealth_mode`: `True` para habilitar medidas que dificultan la detección de la automatización del navegador. Puede requerir la instalación manual de extensiones del navegador como anticaptcha.

Esta sección resume los tipos de proveedores de LLM admitidos. Configúralos en `config.ini`.

**Proveedores locales (ejecutándose en tu propio hardware):**

| Nombre del proveedor en config.ini | `is_local` | Descripción                                                                 | Sección de configuración                                                    |
|-------------------------------|------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| `ollama`                      | `True`     | Proporciona LLM localmente fácilmente usando Ollama.                                             | [Configuración para ejecutar LLM localmente en tu máquina](#configuración-para-ejecutar-llm-localmente-en-tu-máquina) |
| `lm-studio`                   | `True`     | Proporciona LLM localmente con LM-Studio.                                          | [Configuración para ejecutar LLM localmente en tu máquina](#configuración-para-ejecutar-llm-localmente-en-tu-máquina) |
| `openai` (para servidor local)   | `True`     | Conéctate a un servidor local que exponga una API compatible con OpenAI (ej: llama.cpp). | [Configuración para ejecutar LLM localmente en tu máquina](#configuración-para-ejecutar-llm-localmente-en-tu-máquina) |
| `server`                      | `False`    | Conéctate al servidor LLM autoalojado de AgenticSeek que se ejecuta en otra máquina. | [Configuración para ejecutar LLM en tu propio servidor](#configuración-para-ejecutar-llm-en-tu-propio-servidor) |

**Proveedores de API (basados en la nube):**

| Nombre del proveedor en config.ini | `is_local` | Descripción                                      | Sección de configuración                                       |
|-------------------------------|------------|--------------------------------------------------|-----------------------------------------------------|
| `openai`                      | `False`    | Usa la API oficial de OpenAI (ej: GPT-3.5, GPT-4). | [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api) |
| `google`                      | `False`    | Usa modelos Google Gemini a través de API.              | [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api) |
| `deepseek`                    | `False`    | Usa la API oficial de Deepseek.                     | [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api) |
| `huggingface`                 | `False`    | Usa Hugging Face Inference API.                  | [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api) |
| `togetherAI`                  | `False`    | Usa varios modelos abiertos a través de la API de TogetherAI.    | [Configuración para ejecutar con una API](#configuración-para-ejecutar-con-una-api) |

---
## Solución de problemas

Si encuentras problemas, esta sección proporciona orientación.

# Problemas conocidos

## Problemas de ChromeDriver

**Ejemplo de error:** `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

### Causa principal
La incompatibilidad de versión de ChromeDriver ocurre cuando:
1. La versión de ChromeDriver que instalaste no coincide con la versión del navegador Chrome
2. En entornos Docker, `undetected_chromedriver` puede descargar su propia versión de ChromeDriver, evitando los binarios montados

### Pasos de solución

#### 1. Verifica tu versión de Chrome
Abre Google Chrome → `Configuración > Acerca de Chrome` para encontrar tu versión (ej: "Versión 134.0.6998.88")

#### 2. Descarga ChromeDriver coincidente

**Para Chrome 115 y versiones más recientes:** Usa [Chrome for Testing API](https://googlechromelabs.github.io/chrome-for-testing/)
- Visita el panel de disponibilidad de Chrome for Testing
- Encuentra tu versión de Chrome o la coincidencia disponible más cercana
- Descarga ChromeDriver para tu sistema operativo (usa Linux64 para entornos Docker)

**Para versiones antiguas de Chrome:** Usa [Descargas heredadas de ChromeDriver](https://chromedriver.chromium.org/downloads)

![Descargar ChromeDriver desde Chrome for Testing](./media/chromedriver_readme.png)

#### 3. Instala ChromeDriver (elige un método)

**Método A: Directorio raíz del proyecto (recomendado para Docker)**
```bash
# Coloca el binario de chromedriver descargado en el directorio raíz del proyecto
cp path/to/downloaded/chromedriver ./chromedriver
chmod +x ./chromedriver  # Hazlo ejecutable en Linux/macOS
```

**Método B: PATH del sistema**
```bash
# Linux/macOS
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Windows: Coloca chromedriver.exe en una carpeta en PATH
```

#### 4. Verifica la instalación
```bash
# Prueba la versión de ChromeDriver
./chromedriver --version
# O si está en PATH:
chromedriver --version
```

### Instrucciones específicas de Docker

⚠️ **Importante para usuarios de Docker:**
- El método de montaje de volúmenes de Docker puede no funcionar con el modo sigiloso (`undetected_chromedriver`)
- **Solución:** Coloca ChromeDriver en el directorio raíz del proyecto como `./chromedriver`
- La aplicación lo detectará automáticamente y usará este binario
- Deberías ver en los registros: `"Using ChromeDriver from project root: ./chromedriver"`

### Consejos para solución de problemas

1. **¿Sigues teniendo incompatibilidad de versión?**
   - Verifica que ChromeDriver sea ejecutable: `ls -la ./chromedriver`
   - Comprueba la versión de ChromeDriver: `./chromedriver --version`
   - Asegúrate de que coincida con tu versión del navegador Chrome

2. **¿Problemas con el contenedor Docker?**
   - Revisa los registros del backend: `docker logs backend`
   - Busca el mensaje: `"Using ChromeDriver from project root"`
   - Si no se encuentra, verifica que el archivo exista y sea ejecutable

3. **Versiones de Chrome for Testing**
   - Usa una coincidencia exacta cuando sea posible
   - Para la versión 134.0.6998.88, usa ChromeDriver 134.0.6998.165 (la versión disponible más cercana)
   - El número de versión principal debe coincidir (134 = 134)

### Matriz de compatibilidad de versiones

| Versión de Chrome | Versión de ChromeDriver | Estado |
|----------------|---------------------|---------|
| 134.0.6998.x   | 134.0.6998.165     | ✅ Disponible |
| 133.0.6943.x   | 133.0.6943.141     | ✅ Disponible |
| 132.0.6834.x   | 132.0.6834.159     | ✅ Disponible |

*Para la compatibilidad más reciente, consulta el [Panel de Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)*

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

Esto sucede si tu navegador y la versión de chromedriver no coinciden.

Necesitas navegar para descargar la versión más reciente:

https://developer.chrome.com/docs/chromedriver/downloads

Si usas Chrome versión 115 o superior, ve a:

https://googlechromelabs.github.io/chrome-for-testing/

y descarga la versión de chromedriver que coincida con tu sistema operativo.

![alt text](./media/chromedriver_readme.png)

Si esta sección está incompleta, abre un issue.

##  Problemas de adaptadores de conexión

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:1234/v1/chat/completions'` (nota: el puerto puede variar)
```

*   **Causa:** Falta el prefijo `http://` en `provider_server_address` para `lm-studio` (u otro servidor local compatible con OpenAI similar) en `config.ini`, o apunta al puerto incorrecto.
*   **Solución:**
    *   Asegúrate de que la dirección incluya `http://`. LM-Studio normalmente usa `http://127.0.0.1:1234` por defecto.
    *   `config.ini` correcto: `provider_server_address = http://127.0.0.1:1234` (o tu puerto real del servidor LM-Studio).

## URL base de SearxNG no proporcionada

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.`
```

Esto puede ocurrir si ejecutas el modo CLI con la URL base de searxng incorrecta.

`SEARXNG_BASE_URL` se configura en `.env` y depende únicamente de **dónde se ejecute el backend**:

**Backend en el host (modo CLI)**: `SEARXNG_BASE_URL="http://localhost:8080"` — si cambiaste `SEARXNG_PORT`, usa ese puerto en su lugar (por ejemplo, `http://localhost:8001`). `http://searxng:...` **no** funciona aquí: ese nombre de host solo se resuelve dentro de Docker.

**Backend en Docker (interfaz web, perfil `full`)**: `SEARXNG_BASE_URL="http://searxng:8080"` — siempre el puerto `8080`, incluso si cambiaste `SEARXNG_PORT`; esa variable solo remapea el lado del host.

> **Nota sobre conflictos de puertos**: Si el puerto `8080` ya está en uso en tu host, establece `SEARXNG_PORT` (por ejemplo, `8001`) en `.env`, y luego:
> - Interfaz web (backend en Docker): mantén `SEARXNG_BASE_URL="http://searxng:8080"` — el puerto interno de Docker no cambia.
> - Modo CLI (backend en el host): establece `SEARXNG_BASE_URL="http://localhost:8001"` — debe coincidir con `SEARXNG_PORT`.
> - Comprobaciones en el navegador: abre `http://localhost:<SEARXNG_PORT>` — lo que responda en el antiguo puerto `8080` es otra aplicación, no el SearXNG de AgenticSeek.
>
> Después de cambiar `.env`, reinicia el backend (`api.py` o `cli.py`) — el archivo solo se lee al iniciar el proceso.

## FAQ

**P: ¿Qué hardware necesito?**  

| Tamaño del modelo  | GPU  | Comentarios                                               |
|-----------|--------|-----------------------------------------------------------|
| 7B        | 8GB VRAM | ⚠️ No recomendado. Rendimiento pobre, alucinaciones frecuentes, los agentes de planificación pueden fallar. |
| 14B        | 12 GB VRAM (ej: RTX 3060) | ✅ Utilizable para tareas simples. Puede tener dificultades con la navegación web y la planificación de tareas. |
| 32B        | 24+ GB VRAM (ej: RTX 4090) | 🚀 Éxito en la mayoría de las tareas, aún puede tener dificultades con la planificación de tareas |
| 70B+        | 48+ GB VRAM | 💪 Excelente. Recomendado para casos de uso avanzados. |

**P: ¿Qué hago si encuentro errores?**  

Asegúrate de que lo local esté ejecutándose (`ollama serve`), que tu `config.ini` coincida con tu proveedor y que las dependencias estén instaladas. Si nada funciona, no dudes en abrir un issue.

**P: ¿Realmente puede ejecutarse 100% localmente?**  

Sí, con proveedores Ollama, lm-studio o server, todos los modelos de voz a texto, LLM y texto a voz se ejecutan localmente. Las opciones no locales (OpenAI u otras API) son opcionales.

**P: ¿Por qué debería usar AgenticSeek cuando tengo Manus?**

A diferencia de Manus, AgenticSeek prioriza la independencia de los sistemas externos, dándote más control, privacidad y evitando costos de API.

**P: ¿Quién está detrás de este proyecto?**

Este proyecto fue creado por mí, con dos amigos como mantenedores y contribuyentes de la comunidad de código abierto en GitHub. Solo somos individuos apasionados, no una startup, ni estamos afiliados a ninguna organización.

Cualquier cuenta de AgenticSeek en X además de mi cuenta personal (https://x.com/Martin993886460) es impostora.

## Contribuir

¡Buscamos desarrolladores para mejorar AgenticSeek! Revisa los issues abiertos o discusiones.

[Guía de contribución](./docs/CONTRIBUTING.md)

## Patrocinadores:

¿Quieres mejorar las capacidades de AgenticSeek con funciones como búsqueda de vuelos, planificación de viajes o obtención de las mejores ofertas de compras? Considera usar SerpApi para crear herramientas personalizadas que desbloqueen más funcionalidades al estilo Jarvis. Con SerpApi, puedes acelerar tu agente para tareas profesionales mientras mantienes el control total.

<a href="https://serpapi.com/"><img src="./media/banners/sponsor_banner_serpapi.png" height="350" alt="SerpApi Banner" ></a>

¡Consulta [Contributing.md](./docs/CONTRIBUTING.md) para aprender cómo integrar herramientas personalizadas!

## Mantenedores:

 > [Fosowl](https://github.com/Fosowl) | Hora de París 

## Agradecimientos especiales:

 > [tcsenpai](https://github.com/tcsenpai) y [plitc](https://github.com/plitc) por ayudar con la dockerización del backend

[![Star History Chart](https://star-history.dera.page/svg?repos=Fosowl/agenticSeek&type=Date)](https://star-history.dera.page/#Fosowl/agenticSeek&Date)
