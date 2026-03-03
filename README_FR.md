# AgenticSeek : Une Alternative Privée et Locale à Manus

<p align="center">
<img align="center" src="./media/agentic_seek_logo.png" width="300" height="300" alt="Agentic Seek Logo">
<p>

  English | [中文](./README_CHS.md) | [繁體中文](./README_CHT.md) | [Français](./README_FR.md) | [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md) | [Español](./README_ES.md) | [Türkçe](./README_TR.md)

*Un assistant IA avec reconnaissance vocale qui est une **alternative 100% locale à Manus AI**, navigue de manière autonome sur le web, écrit du code et planifie des tâches tout en gardant toutes les données sur votre appareil. Conçu pour des modèles de raisonnement locaux, il fonctionne entièrement sur votre matériel, garantissant une confidentialité totale et zéro dépendance au cloud.*

[![Visiter AgenticSeek](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460) [![GitHub stars](https://img.shields.io/github/stars/Fosowl/agenticSeek?style=social)](https://github.com/Fosowl/agenticSeek/stargazers)

### Pourquoi choisir AgenticSeek ?

* 🔒 Totalement Local & Privé - Tout fonctionne sur votre machine, sans cloud, sans partage de données. Vos fichiers, conversations et recherches restent privés.

* 🌐 Navigation Web Intelligente - AgenticSeek peut naviguer sur Internet de manière autonome : rechercher, lire, extraire des informations, remplir des formulaires web, le tout sans intervention manuelle.

* 💻 Assistant de Programmation Autonome - Besoin de code ? Il peut écrire, déboguer et exécuter des programmes en Python, C, Go, Java et plus encore, sans supervision.

* 🧠 Sélection Intelligente d'Agents - Vous demandez, il choisit automatiquement le meilleur agent pour la tâche. Comme avoir une équipe d'experts toujours disponible.

* 📋 Planifie et Exécute des Tâches Complexes - De la planification de voyage aux projets complexes, il peut décomposer de grandes tâches en étapes et les compléter en utilisant plusieurs agents IA.

* 🎙️ Prise en Charge Vocale - Voix claire, rapide et futuriste avec reconnaissance vocale, vous permettant de converser comme avec votre IA personnelle de film de science-fiction. (En développement)

### **Démo**

> *Peux-tu rechercher le projet agenticSeek, apprendre quelles compétences sont nécessaires, puis ouvrir CV_candidates.zip et me dire lesquels correspondent le mieux au projet ?*

https://github.com/user-attachments/assets/b8ca60e9-7b3b-4533-840e-08f9ac426316

Avertissement : Cette démonstration et tous les fichiers qui apparaissent (ex: CV_candidates.zip) sont entièrement fictifs. Nous ne sommes pas une entreprise, nous recherchons des contributeurs open source, pas des candidats.

> 🛠⚠️️ **Travail Actif en Cours**

> 🙏 Ce projet a commencé comme un projet parallèle et n'a ni feuille de route ni financement. Il a grandi bien au-delà des attentes en apparaissant dans GitHub Trending. Les contributions, commentaires et de la patience sont profondément appréciés.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

*   **Git:** Pour cloner le dépôt. [Télécharger Git](https://git-scm.com/downloads)
*   **Python 3.10.x:** Python 3.10.x est fortement recommandé. D'autres versions peuvent causer des erreurs de dépendance. [Télécharger Python 3.10](https://www.python.org/downloads/release/python-3100/) (sélectionnez la version 3.10.x).
*   **Docker Engine & Docker Compose:** Pour exécuter des services empaquetés comme SearxNG.
    *   Installer Docker Desktop (inclut Docker Compose V2): [Windows](https://docs.docker.com/desktop/install/windows-install/) | [Mac](https://docs.docker.com/desktop/install/mac-install/) | [Linux](https://docs.docker.com/desktop/install/linux-install/)
    *   Ou installer Docker Engine et Docker Compose séparément sur Linux: [Docker Engine](https://docs.docker.com/engine/install/) | [Docker Compose](https://docs.docker.com/compose/install/) (assurez-vous d'installer Compose V2, par exemple `sudo apt-get install docker-compose-plugin`).

### 1. **Cloner le dépôt et configurer**

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2. Modifier le contenu du fichier .env

```sh
SEARXNG_BASE_URL="http://searxng:8080" # Si vous exécutez en mode CLI sur l'hôte, utilisez http://127.0.0.1:8080
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

Mettez à jour le fichier `.env` selon vos besoins :

- **SEARXNG_BASE_URL**: Gardez inchangé sauf si vous exécutez en mode CLI sur l'hôte.
- **REDIS_BASE_URL**: Gardez inchangé 
- **WORK_DIR**: Chemin vers le répertoire de travail local. AgenticSeek pourra lire et interagir avec ces fichiers.
- **OLLAMA_PORT**: Numéro de port pour le service Ollama.
- **LM_STUDIO_PORT**: Numéro de port pour le service LM Studio.
- **CUSTOM_ADDITIONAL_LLM_PORT**: Port pour tout service LLM personnalisé supplémentaire.

**Les clés API sont complètement optionnelles pour ceux qui choisissent d'exécuter LLM localement, ce qui est l'objectif principal de ce projet. Laissez-les vides si vous avez du matériel suffisant.**

### 3. **Démarrer Docker**

Assurez-vous que Docker est installé et fonctionne sur votre système. Vous pouvez démarrer Docker avec les commandes suivantes :

- **Linux/macOS:**  
    Ouvrez un terminal et exécutez :
    ```sh
    sudo systemctl start docker
    ```
    Ou démarrez Docker Desktop depuis le menu des applications, s'il est installé.

- **Windows:**  
    Démarrez Docker Desktop depuis le menu Démarrer.

Vous pouvez vérifier si Docker fonctionne en exécutant :
```sh
docker info
```
Si vous voyez des informations sur votre installation Docker, cela fonctionne correctement.

Consultez la [Liste des fournisseurs locaux](#liste-des-fournisseurs-locaux) ci-dessous pour un résumé.

Prochaine étape: [Exécuter AgenticSeek localement](#démarrer-les-services-et-exécuter)

*Si vous rencontrez des problèmes, consultez la section [Dépannage](#dépannage).*
*Si votre matériel ne peut pas exécuter LLM localement, consultez [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api).*
*Pour des explications détaillées de `config.ini`, consultez la [section Configuration](#configuration).*

---

## Configuration pour exécuter LLM localement sur votre machine

**Exigences matérielles:**

Pour exécuter LLM localement, vous aurez besoin de matériel suffisant. Au minimum, une GPU capable d'exécuter Magistral, Qwen ou Deepseek 14B est requise. Consultez la FAQ pour des recommandations détaillées de modèle/performance.

**Configurez votre fournisseur local**  

Démarrez votre fournisseur local, par exemple avec ollama:

```sh
ollama serve
```

Consultez la liste des fournisseurs locaux pris en charge ci-dessous.

**Mettre à jour config.ini**

Changez le fichier config.ini pour définir provider_name sur un fournisseur pris en charge et provider_model sur un LLM pris en charge par votre fournisseur. Nous recommandons des modèles de raisonnement comme *Magistral* ou *Deepseek*.

Consultez la **FAQ** à la fin du README pour le matériel nécessaire.

```sh
[MAIN]
is_local = True # Que vous exécutiez localement ou avec un fournisseur distant.
provider_name = ollama # ou lm-studio, openai, etc.
provider_model = deepseek-r1:14b # choisissez un modèle compatible avec votre matériel
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # le nom de votre IA
recover_last_session = True # récupérer la session précédente
save_session = True # mémoriser la session actuelle
speak = False # texte vers parole
listen = False # parole vers texte, uniquement pour CLI, expérimental
jarvis_personality = False # utiliser une personnalité plus "Jarvis" (expérimental)
languages = en zh # Liste des langues, TTS utilisera la première de la liste par défaut
[BROWSER]
headless_browser = True # garder inchangé sauf si vous utilisez CLI sur l'hôte.
stealth_mode = True # Utilise selenium indétectable pour réduire la détection du navigateur
```

**Avertissement**:

- Le format du fichier `config.ini` ne prend pas en charge les commentaires.
Ne copiez et collez pas directement la configuration d'exemple, car les commentaires causeront des erreurs. Modifiez plutôt manuellement le fichier `config.ini` avec votre configuration souhaitée, sans commentaires.

- *NE* définissez PAS provider_name sur `openai` si vous utilisez LM-studio pour exécuter LLM. Utilisez `lm-studio`.

- Certains fournisseurs (ex: lm-studio) nécessitent `http://` avant l'IP. Exemple: `http://127.0.0.1:1234`

**Liste des fournisseurs locaux**

| Fournisseur  | Local ? | Description                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | Oui    | Exécute LLM localement facilement en utilisant ollama |
| lm-studio  | Oui    | Exécute LLM localement avec LM studio (définir `provider_name` = `lm-studio`)|
| openai    | Oui     |  Utilise une API compatible avec openai (ex: serveur llama.cpp)  |

Prochaine étape: [Démarrer les services et exécuter AgenticSeek](#démarrer-les-services-et-exécuter)  

*Si vous rencontrez des problèmes, consultez la section [Dépannage](#dépannage).*
*Si votre matériel ne peut pas exécuter LLM localement, consultez [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api).*
*Pour des explications détaillées de `config.ini`, consultez la [section Configuration](#configuration).*

## Configuration pour exécuter avec une API

Cette configuration utilise des fournisseurs de LLM externes basés sur le cloud. Vous devrez obtenir des clés API du service choisi.

**1. Choisissez un fournisseur d'API et obtenez une clé API:**

Consultez la [Liste des fournisseurs d'API](#liste-des-fournisseurs-dapi) ci-dessous. Visitez leurs sites web pour vous inscrire et obtenir des clés API.

**2. Définissez votre clé API comme variable d'environnement:**

*   **Linux/macOS:**
    Ouvrez un terminal et utilisez la commande `export`. Il est préférable de l'ajouter au fichier de configuration de votre shell (ex: `~/.bashrc`, `~/.zshrc`) pour qu'elle soit persistante.
    ```sh
    export PROVIDER_API_KEY="your_api_key_here" 
    # Remplacez PROVIDER_API_KEY par le nom de variable spécifique, ex: OPENAI_API_KEY, GOOGLE_API_KEY
    ```
    Exemple TogetherAI:
    ```sh
    export TOGETHER_API_KEY="xxxxxxxxxxxxxxxxxxxxxx"
    ```
*   **Windows:**
    *   **Invite de commandes (temporaire pour la session actuelle):**
        ```cmd
        set PROVIDER_API_KEY=your_api_key_here
        ```
    *   **PowerShell (temporaire pour la session actuelle):**
        ```powershell
        $env:PROVIDER_API_KEY="your_api_key_here"
        ```
    *   **Permanent:** Recherchez "variables d'environnement" dans la barre de recherche Windows, cliquez sur "Modifier les variables d'environnement système", puis sur le bouton "Variables d'environnement...". Ajoutez une nouvelle variable utilisateur avec le nom approprié (ex: `OPENAI_API_KEY`) et votre clé comme valeur.

    *(Pour plus de détails, consultez la FAQ: [Comment configurer une clé API ?](#comment-configurer-une-clé-api)).*


**3. Mettez à jour `config.ini`:**
```ini
[MAIN]
is_local = False
provider_name = openai # ou google, deepseek, togetherAI, huggingface
provider_model = gpt-3.5-turbo # ou gemini-1.5-flash, deepseek-chat, mistralai/Mixtral-8x7B-Instruct-v0.1, etc.
provider_server_address = # Lorsque is_local = False, généralement ignoré ou peut être laissé vide pour la plupart des API
# ... autres configurations ...
```
*Avertissement:* Assurez-vous qu'il n'y a pas d'espaces à la fin des valeurs dans config.

**Liste des fournisseurs d'API**

| Fournisseur     | `provider_name` | Local ? | Description                                       | Lien de clé API (exemple)                     |
|--------------|-----------------|--------|---------------------------------------------------|---------------------------------------------|
| OpenAI       | `openai`        | Non     | Utilise les modèles ChatGPT via l'API OpenAI.              | [platform.openai.com/signup](https://platform.openai.com/signup) |
| Google Gemini| `google`        | Non     | Utilise les modèles Google Gemini via Google AI Studio.    | [aistudio.google.com/keys](https://aistudio.google.com/keys) |
| Deepseek     | `deepseek`      | Non     | Utilise les modèles Deepseek via leur API.                | [platform.deepseek.com](https://platform.deepseek.com) |
| Hugging Face | `huggingface`   | Non     | Utilise les modèles du Hugging Face Inference API.       | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| TogetherAI   | `togetherAI`    | Non     | Utilise divers modèles open source via l'API TogetherAI.| [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys) |

*Note:*
*   Nous ne recommandons pas d'utiliser `gpt-4o` ou d'autres modèles OpenAI pour la navigation web complexe et la planification de tâches, car l'optimisation actuelle des prompts cible des modèles comme Deepseek.
*   Les tâches de codage/bash peuvent échouer avec Gemini, car il a tendance à ignorer notre format de prompt optimisé pour Deepseek r1.
*   Lorsque `is_local = False`, `provider_server_address` dans `config.ini` n'est généralement pas utilisé, car les endpoints d'API sont généralement gérés par les bibliothèques du fournisseur correspondant.

Prochaine étape: [Démarrer les services et exécuter AgenticSeek](#démarrer-les-services-et-exécuter)

*Si vous rencontrez des problèmes, consultez la section **Problèmes connus***

*Pour des explications détaillées du fichier de configuration, consultez la **section Configuration**.*

---

## Démarrer les services et exécuter

Par défaut, AgenticSeek s'exécute entièrement dans Docker.

**Option 1:** Exécuter dans Docker avec interface web:

Démarrez les services nécessaires. Cela démarrera tous les services du docker-compose.yml, y compris:
    - searxng
    - redis (requis pour searxng)
    - frontend
    - backend (si vous utilisez `full` pour l'interface web)

```sh
./start_services.sh full # MacOS
start start_services.cmd full # Windows
```

**Avertissement:** Cette étape téléchargera et chargera toutes les images Docker, ce qui peut prendre jusqu'à 30 minutes. Après avoir démarré les services, attendez que le service backend soit complètement opérationnel (vous devriez voir **backend: "GET /health HTTP/1.1" 200 OK** dans les logs) avant d'envoyer des messages. Lors du premier démarrage, le service backend peut prendre 5 minutes pour démarrer.

Allez à `http://localhost:3000/` et vous devriez voir l'interface web.

*Dépannage du démarrage des services:* Si ces scripts échouent, assurez-vous que Docker Engine fonctionne et que Docker Compose (V2, `docker compose`) est correctement installé. Vérifiez les messages d'erreur dans la sortie du terminal. Consultez [FAQ: Aide ! J'obtiens des erreurs lors de l'exécution d'AgenticSeek ou de ses scripts.](#faq-dépannage)

**Option 2:** Mode CLI:

Pour exécuter avec l'interface CLI, vous devez installer les packages sur l'hôte:

```sh
./install.sh
./install.bat # windows
```

Ensuite, vous devez changer SEARXNG_BASE_URL dans `config.ini` en:

```sh
SEARXNG_BASE_URL="http://localhost:8080"
```

Démarrez les services nécessaires. Cela démarrera certains services du docker-compose.yml, y compris:
    - searxng
    - redis (requis pour searxng)
    - frontend

```sh
./start_services.sh # MacOS
start start_services.cmd # Windows
```

Exécutez: uv run: `uv run python -m ensurepip` pour vous assurer que uv a pip activé.

Utilisez CLI: `uv run cli.py`

---

## Utilisation

Assurez-vous que les services fonctionnent avec `./start_services.sh full` puis allez à `localhost:3000` pour l'interface web.

Vous pouvez également utiliser la parole vers texte en définissant `listen = True`. Uniquement pour le mode CLI.

Pour quitter, dites/tapez simplement `goodbye`.

Quelques exemples d'utilisation:

> *Fais un jeu de serpent en python !*

> *Recherche sur le web les meilleurs cafés à Rennes, France, et sauvegarde une liste de trois avec leurs adresses dans rennes_cafes.txt.*

> *Écris un programme Go pour calculer la factorielle d'un nombre, sauvegarde-le comme factorial.go dans ton workspace*

> *Recherche dans le dossier summer_pictures tous les fichiers JPG, renomme-les avec la date d'aujourd'hui et sauvegarde la liste des fichiers renommés dans photos_list.txt*

> *Recherche en ligne les films de science-fiction populaires de 2024 et choisis-en trois à regarder ce soir. Sauvegarde la liste dans movie_night.txt.*

> *Recherche sur le web les derniers articles d'actualité sur l'IA de 2025, sélectionne-en trois et écris un script Python pour extraire les titres et résumés. Sauvegarde le script comme news_scraper.py et les résumés dans ai_news.txt dans /home/projects*

> *Vendredi, recherche sur le web une API gratuite de prix d'actions, inscris-toi avec supersuper7434567@gmail.com et écris un script Python pour obtenir les prix quotidiens de Tesla en utilisant l'API, en sauvegardant les résultats dans stock_prices.csv*

*Notez que le remplissage de formulaires est toujours expérimental et peut échouer.*

Après avoir saisi votre requête, AgenticSeek attribuera le meilleur agent pour la tâche.

Comme il s'agit d'un prototype initial, le système de routage des agents peut ne pas toujours attribuer l'agent correct à votre requête.

Par conséquent, soyez très explicite sur ce que vous voulez et comment l'IA pourrait procéder, par exemple si vous voulez qu'elle effectue une recherche web, ne dites pas:

`Connais-tu de bons pays pour voyager seul ?`

Dites plutôt:

`Effectue une recherche web et découvre quels sont les meilleurs pays pour voyager seul`

---

## **Configuration pour exécuter LLM sur votre propre serveur**

Si vous avez un ordinateur puissant ou un serveur auquel vous pouvez accéder, mais que vous voulez l'utiliser depuis votre ordinateur portable, vous pouvez choisir d'exécuter le LLM sur un serveur distant en utilisant notre serveur llm personnalisé.

Sur votre "serveur" qui exécutera le modèle d'IA, obtenez l'adresse IP

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 # IP locale
curl https://ipinfo.io/ip # IP publique
```

Note: Pour Windows ou macOS, utilisez ipconfig ou ifconfig pour trouver l'adresse IP.

Clonez le dépôt et entrez dans le dossier `server/`.

```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/llm_server/
```

Installez les exigences spécifiques au serveur:

```sh
pip3 install -r requirements.txt
```

Exécutez le script du serveur.

```sh
python3 app.py --provider ollama --port 3333
```

Vous pouvez choisir d'utiliser `ollama` et `llamacpp` comme service LLM.

Maintenant sur votre ordinateur personnel:

Changez le fichier `config.ini` pour définir `provider_name` sur `server` et `provider_model` sur `deepseek-r1:xxb`.
Définissez `provider_server_address` sur l'adresse IP de la machine qui exécutera le modèle.

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:70b
provider_server_address = http://x.x.x.x:3333
```

Prochaine étape: [Démarrer les services et exécuter AgenticSeek](#démarrer-les-services-et-exécuter)  

---

## Parole vers Texte

Avertissement: La speech-to-text ne fonctionne qu'en mode CLI pour le moment.

Notez que la parole vers texte ne fonctionne qu'en anglais pour le moment.

La fonctionnalité de parole vers texte est désactivée par défaut. Pour l'activer, définissez listen sur True dans le fichier config.ini:

```
listen = True
```

Lorsqu'elle est activée, la fonction de parole vers texte écoute un mot-clé de déclenchement, qui est le nom de l'agent, avant de traiter votre entrée. Vous pouvez personnaliser le nom de l'agent en mettant à jour la valeur `agent_name` dans *config.ini*:

```
agent_name = Friday
```

Pour une meilleure reconnaissance, nous recommandons d'utiliser un nom commun en anglais comme "John" ou "Emma" comme nom d'agent.

Une fois que vous voyez la transcription commencer à apparaître, dites le nom de l'agent à haute voix pour le réveiller (ex: "Friday").

Dites votre requête clairement.

Terminez votre demande par une phrase de confirmation pour indiquer au système de continuer. Les exemples de phrases de confirmation incluent:
```
"do it", "go ahead", "execute", "run", "start", "thanks", "would ya", "please", "okay?", "proceed", "continue", "go on", "do that", "go it", "do you understand?"
```

## Configuration

Exemple de configuration:
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:32b
provider_server_address = http://127.0.0.1:11434 # Exemple Ollama; LM-Studio utilise http://127.0.0.1:1234
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False

jarvis_personality = False
languages = en zh # Liste des langues pour TTS et routage potentiel.
[BROWSER]
headless_browser = False
stealth_mode = False
```

**Explication des paramètres de `config.ini`**:

*   **Section `[MAIN]`:**
    *   `is_local`: `True` si vous utilisez des fournisseurs de LLM locaux (Ollama, LM-Studio, serveur local compatible OpenAI) ou l'option de serveur auto-hébergé. `False` si vous utilisez des API basées sur le cloud (OpenAI, Google, etc.).
    *   `provider_name`: Spécifie le fournisseur de LLM.
        *   Options locales: `ollama`, `lm-studio`, `openai` (pour serveur local compatible OpenAI), `server` (pour configuration de serveur auto-hébergé).
        *   Options d'API: `openai`, `google`, `deepseek`, `huggingface`, `togetherAI`.
    *   `provider_model`: Nom ou ID spécifique du modèle du fournisseur sélectionné (ex: `deepseekcoder:6.7b` pour Ollama, `gpt-3.5-turbo` pour API OpenAI, `mistralai/Mixtral-8x7B-Instruct-v0.1` pour TogetherAI).
    *   `provider_server_address`: L'adresse de votre fournisseur de LLM.
        *   Pour les fournisseurs locaux: ex: `http://127.0.0.1:11434` pour Ollama, `http://127.0.0.1:1234` pour LM-Studio.
        *   Pour le type de fournisseur `server`: L'adresse de votre serveur LLM auto-hébergé (ex: `http://your_server_ip:3333`).
        *   Pour les API cloud (`is_local = False`): Ceci est généralement ignoré ou peut être laissé vide, car les endpoints d'API sont généralement gérés par les bibliothèques clientes.
    *   `agent_name`: Le nom de l'assistant IA (ex: Friday). Si activé, utilisé comme mot de déclenchement pour la parole vers texte.
    *   `recover_last_session`: `True` pour tenter de récupérer l'état de la session précédente, `False` pour recommencer.
    *   `save_session`: `True` pour sauvegarder l'état de la session actuelle pour une récupération potentielle, `False` sinon.
    *   `speak`: `True` pour activer la sortie vocale de texte vers parole, `False` pour désactiver.
    *   `listen`: `True` pour activer l'entrée vocale de parole vers texte (uniquement mode CLI), `False` pour désactiver.
    *   `work_dir`: **Critique:** Le répertoire où AgenticSeek lira/écrira des fichiers. **Assurez-vous que ce chemin est valide et accessible sur votre système.**
    *   `jarvis_personality`: `True` pour utiliser des invites système plus "Jarvis-like" (expérimental), `False` pour utiliser des invites standard.
    *   `languages`: Liste de langues séparées par des virgules (ex: `en, zh, fr`). Utilisé pour la sélection de voix TTS (première par défaut) et peut aider le routeur LLM. Pour éviter les inefficacités du routeur, évitez d'utiliser trop de langues ou des langues très similaires.
*   **Section `[BROWSER]`:**
    *   `headless_browser`: `True` pour exécuter le navigateur automatisé sans fenêtre visible (recommandé pour l'interface web ou l'utilisation non interactive). `False` pour afficher la fenêtre du navigateur (utile pour le mode CLI ou le débogage).
    *   `stealth_mode`: `True` pour activer des mesures qui rendent plus difficile la détection de l'automatisation du navigateur. Peut nécessiter l'installation manuelle d'extensions de navigateur comme anticaptcha.

Cette section résume les types de fournisseurs de LLM pris en charge. Configurez-les dans `config.ini`.

**Fournisseurs locaux (fonctionnant sur votre propre matériel):**

| Nom du fournisseur dans config.ini | `is_local` | Description                                                                 | Section de configuration                                                    |
|-------------------------------|------------|-----------------------------------------------------------------------------|------------------------------------------------------------------|
| `ollama`                      | `True`     | Fournit LLM localement facilement en utilisant Ollama.                                             | [Configuration pour exécuter LLM localement sur votre machine](#configuration-pour-exécuter-llm-localement-sur-votre-machine) |
| `lm-studio`                   | `True`     | Fournit LLM localement avec LM-Studio.                                          | [Configuration pour exécuter LLM localement sur votre machine](#configuration-pour-exécuter-llm-localement-sur-votre-machine) |
| `openai` (pour serveur local)   | `True`     | Connectez-vous à un serveur local exposant une API compatible OpenAI (ex: llama.cpp). | [Configuration pour exécuter LLM localement sur votre machine](#configuration-pour-exécuter-llm-localement-sur-votre-machine) |
| `server`                      | `False`    | Connectez-vous au serveur LLM auto-hébergé d'AgenticSeek fonctionnant sur une autre machine. | [Configuration pour exécuter LLM sur votre propre serveur](#configuration-pour-exécuter-llm-sur-votre-propre-serveur) |

**Fournisseurs d'API (basés sur le cloud):**

| Nom du fournisseur dans config.ini | `is_local` | Description                                      | Section de configuration                                       |
|-------------------------------|------------|--------------------------------------------------|-----------------------------------------------------|
| `openai`                      | `False`    | Utilise l'API officielle d'OpenAI (ex: GPT-3.5, GPT-4). | [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api) |
| `google`                      | `False`    | Utilise les modèles Google Gemini via API.              | [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api) |
| `deepseek`                    | `False`    | Utilise l'API officielle de Deepseek.                     | [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api) |
| `huggingface`                 | `False`    | Utilise Hugging Face Inference API.                  | [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api) |
| `togetherAI`                  | `False`    | Utilise divers modèles ouverts via l'API TogetherAI.    | [Configuration pour exécuter avec une API](#configuration-pour-exécuter-avec-une-api) |

---
## Dépannage

Si vous rencontrez des problèmes, cette section fournit des conseils.

# Problèmes connus

## Problèmes de ChromeDriver

**Exemple d'erreur:** `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

### Cause racine
L'incompatibilité de version de ChromeDriver se produit lorsque:
1. La version de ChromeDriver que vous avez installée ne correspond pas à la version du navigateur Chrome
2. Dans les environnements Docker, `undetected_chromedriver` peut télécharger sa propre version de ChromeDriver, contournant les binaires montés

### Étapes de résolution

#### 1. Vérifiez votre version de Chrome
Ouvrez Google Chrome → `Paramètres > À propos de Chrome` pour trouver votre version (ex: "Version 134.0.6998.88")

#### 2. Téléchargez ChromeDriver correspondant

**Pour Chrome 115 et versions ultérieures:** Utilisez [Chrome for Testing API](https://googlechromelabs.github.io/chrome-for-testing/)
- Visitez le tableau de disponibilité de Chrome for Testing
- Trouvez votre version de Chrome ou la correspondance disponible la plus proche
- Téléchargez ChromeDriver pour votre système d'exploitation (utilisez Linux64 pour les environnements Docker)

**Pour les anciennes versions de Chrome:** Utilisez [Téléchargements hérités de ChromeDriver](https://chromedriver.chromium.org/downloads)

![Télécharger ChromeDriver depuis Chrome for Testing](./media/chromedriver_readme.png)

#### 3. Installez ChromeDriver (choisissez une méthode)

**Méthode A: Répertoire racine du projet (recommandé pour Docker)**
```bash
# Placez le binaire chromedriver téléchargé dans le répertoire racine du projet
cp path/to/downloaded/chromedriver ./chromedriver
chmod +x ./chromedriver  # Rendez-le exécutable sur Linux/macOS
```

**Méthode B: PATH système**
```bash
# Linux/macOS
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Windows: Placez chromedriver.exe dans un dossier du PATH
```

#### 4. Vérifiez l'installation
```bash
# Testez la version de ChromeDriver
./chromedriver --version
# Ou s'il est dans PATH:
chromedriver --version
```

### Instructions spécifiques à Docker

⚠️ **Important pour les utilisateurs de Docker:**
- La méthode de montage de volumes Docker peut ne pas fonctionner avec le mode furtif (`undetected_chromedriver`)
- **Solution:** Placez ChromeDriver dans le répertoire racine du projet en tant que `./chromedriver`
- L'application le détectera automatiquement et utilisera ce binaire
- Vous devriez voir dans les logs: `"Using ChromeDriver from project root: ./chromedriver"`

### Conseils de dépannage

1. **Toujours une incompatibilité de version ?**
   - Vérifiez que ChromeDriver est exécutable: `ls -la ./chromedriver`
   - Vérifiez la version de ChromeDriver: `./chromedriver --version`
   - Assurez-vous qu'elle correspond à votre version du navigateur Chrome

2. **Problèmes avec le conteneur Docker ?**
   - Vérifiez les logs du backend: `docker logs backend`
   - Recherchez le message: `"Using ChromeDriver from project root"`
   - S'il n'est pas trouvé, vérifiez que le fichier existe et est exécutable

3. **Versions de Chrome for Testing**
   - Utilisez une correspondance exacte lorsque possible
   - Pour la version 134.0.6998.88, utilisez ChromeDriver 134.0.6998.165 (la version disponible la plus proche)
   - Le numéro de version principal doit correspondre (134 = 134)

### Matrice de compatibilité des versions

| Version de Chrome | Version de ChromeDriver | Statut |
|----------------|---------------------|---------|
| 134.0.6998.x   | 134.0.6998.165     | ✅ Disponible |
| 133.0.6943.x   | 133.0.6943.141     | ✅ Disponible |
| 132.0.6834.x   | 132.0.6834.159     | ✅ Disponible |

*Pour la compatibilité la plus récente, consultez le [Tableau de Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)*

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

Cela se produit si votre navigateur et la version de chromedriver ne correspondent pas.

Vous devez naviguer pour télécharger la dernière version:

https://developer.chrome.com/docs/chromedriver/downloads

Si vous utilisez Chrome version 115 ou supérieure, allez à:

https://googlechromelabs.github.io/chrome-for-testing/

et téléchargez la version de chromedriver correspondant à votre système d'exploitation.

![alt text](./media/chromedriver_readme.png)

Si cette section est incomplète, ouvrez un issue.

##  Problèmes d'adaptateurs de connexion

```
Exception: Provider lm-studio failed: HTTP request failed: No connection adapters were found for '127.0.0.1:1234/v1/chat/completions'` (note: le port peut varier)
```

*   **Cause:** Il manque le préfixe `http://` dans `provider_server_address` pour `lm-studio` (ou un autre serveur local compatible OpenAI similaire) dans `config.ini`, ou il pointe vers le mauvais port.
*   **Solution:**
    *   Assurez-vous que l'adresse inclut `http://`. LM-Studio utilise généralement `http://127.0.0.1:1234` par défaut.
    *   `config.ini` correct: `provider_server_address = http://127.0.0.1:1234` (ou votre port réel du serveur LM-Studio).

## URL de base de SearxNG non fournie

```
raise ValueError("SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.")
ValueError: SearxNG base URL must be provided either as an argument or via the SEARXNG_BASE_URL environment variable.`
```

Cela peut se produire si vous exécutez le mode CLI avec une URL de base de searxng incorrecte.

SEARXNG_BASE_URL doit différer selon que vous exécutez dans Docker ou sur l'hôte:

**Exécution sur l'hôte:** `SEARXNG_BASE_URL="http://localhost:8080"`

**Exécution complètement dans Docker (interface web):** `SEARXNG_BASE_URL="http://searxng:8080"`

## FAQ

**Q: De quel matériel ai-je besoin ?**  

| Taille du modèle  | GPU  | Commentaires                                               |
|-----------|--------|-----------------------------------------------------------|
| 7B        | 8GB VRAM | ⚠️ Non recommandé. Performances médiocres, hallucinations fréquentes, les agents de planification peuvent échouer. |
| 14B        | 12 GB VRAM (ex: RTX 3060) | ✅ Utilisable pour des tâches simples. Peut avoir des difficultés avec la navigation web et la planification de tâches. |
| 32B        | 24+ GB VRAM (ex: RTX 4090) | 🚀 Réussit la plupart des tâches, peut encore avoir des difficultés avec la planification de tâches |
| 70B+        | 48+ GB VRAM | 💪 Excellent. Recommandé pour les cas d'utilisation avancés. |

**Q: Que faire si je rencontre des erreurs ?**  

Assurez-vous que le local fonctionne (`ollama serve`), que votre `config.ini` correspond à votre fournisseur et que les dépendances sont installées. Si rien ne fonctionne, n'hésitez pas à ouvrir un issue.

**Q: Peut-il vraiment fonctionner à 100% localement ?**  

Oui, avec les fournisseurs Ollama, lm-studio ou server, tous les modèles de parole vers texte, LLM et texte vers parole fonctionnent localement. Les options non locales (OpenAI ou autres API) sont optionnelles.

**Q: Pourquoi devrais-je utiliser AgenticSeek quand j'ai Manus ?**

Contrairement à Manus, AgenticSeek privilégie l'indépendance des systèmes externes, vous donnant plus de contrôle, de confidentialité et évitant les coûts d'API.

**Q: Qui est derrière ce projet ?**

Ce projet a été créé par moi, avec deux amis comme mainteneurs et des contributeurs de la communauté open source sur GitHub. Nous sommes juste des individus passionnés, pas une startup, ni affiliés à aucune organisation.

Tout compte AgenticSeek sur X autre que mon compte personnel (https://x.com/Martin993886460) est un imposteur.

## Contribuer

Nous recherchons des développeurs pour améliorer AgenticSeek ! Consultez les problèmes ouverts ou les discussions.

[Guide de contribution](./docs/CONTRIBUTING.md)

## Sponsors:

Vous voulez améliorer les capacités d'AgenticSeek avec des fonctionnalités comme la recherche de vols, la planification de voyages ou l'obtention des meilleures offres d'achat ? Envisagez d'utiliser SerpApi pour créer des outils personnalisés qui débloquent plus de fonctionnalités de type Jarvis. Avec SerpApi, vous pouvez accélérer votre agent pour des tâches professionnelles tout en gardant le contrôle total.

<a href="https://serpapi.com/"><img src="./media/banners/sponsor_banner_serpapi.png" height="350" alt="SerpApi Banner" ></a>

Consultez [Contributing.md](./docs/CONTRIBUTING.md) pour apprendre comment intégrer des outils personnalisés !

### **Sponsors**:

- [tatra-labs](https://github.com/tatra-labs)

## Mainteneurs:

 > [Fosowl](https://github.com/Fosowl) | Heure de Paris 

 > [antoineVIVIES](https://github.com/antoineVIVIES) | Heure de Taipei 

## Remerciements spéciaux:

 > [tcsenpai](https://github.com/tcsenpai) et [plitc](https://github.com/plitc) pour avoir aidé à la dockerisation du backend

[![Star History Chart](https://api.star-history.com/svg?repos=Fosowl/agenticSeek&type=Date)](https://www.star-history.com/#Fosowl/agenticSeek&Date)
