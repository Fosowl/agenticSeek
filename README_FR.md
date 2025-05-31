<p align="center">
<img align="center" src="./media/whale_readme.jpg">
<p>

--------------------------------------------------------------------------------
[English](./README.md) | [繁體中文](./README_CHT.md) | [日本語](./README_JP.md) | Français| [日本語](./README_JP.md) | [Português (Brasil)](./README_PTBR.md)

# AgenticSeek: Une IA comme Manus mais à base d'agents DeepSeek R1 fonctionnant en local.

Une alternative **entièrement locale** à Manus AI, un assistant IA qui code, explore votre système de fichiers, navigue sur le web et corrige ses erreurs, tout cela sans envoyer la moindre donnée dans le cloud. Cet agent autonome fonctionne entièrement sur votre hardware, garantissant la confidentialité de vos données.

[![Visit AgenticSeek](https://img.shields.io/static/v1?label=Website&message=AgenticSeek&color=blue&style=flat-square)](https://fosowl.github.io/agenticSeek.html) ![License](https://img.shields.io/badge/license-GPL--3.0-green) [![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289DA?logo=discord&logoColor=white)](https://discord.gg/8hGDaME3TC) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/fosowl.svg?style=social&label=Update%20%40Fosowl)](https://x.com/Martin993886460)

> 🛠️ **En cours de développement** – On cherche activement des contributeurs!

https://github.com/user-attachments/assets/4bd5faf6-459f-4f94-bd1d-238c4b331469

> *Recherche sur le web des activités à faire à Paris*

> *Code le jeu snake en python*

> *J'aimerais que tu trouve une api météo et que tu me code une application qui affiche la météo à Toulouse*



## Fonctionnalités:

- **100% Local**: Fonctionne en local sur votre PC. Vos données restent les vôtres. 

- **Accès à vos Fichiers**: Utilise bash pour naviguer et manipuler vos fichiers.

- **Codage semi-autonome**: Peut écrire, déboguer et exécuter du code en Python, C, Golang et d'autres langages à venir. 

- **Routage d'Agent**: Sélectionne automatiquement l’agent approprié pour la tâche. 

- **Planification**: Pour les taches complexe utilise plusieurs agents.

- **Navigation Web Autonome**: Navigation web autonome.

- **Memoire efficace**: Gestion efficace de la mémoire et des sessions. 

---

## **Installation**

Assurez-vous d’avoir installé le pilote Chrome, Docker et Python 3.10.

Nous vous conseillons fortement d'utiliser exactement Python 3.10 pour l'installation. Des erreurs de dépendances pourraient survenir autrement.

Pour les problèmes liés au pilote Chrome, consultez la section Chromedriver.

### 1️⃣ Cloner le repo et configurer

```sh
git clone https://github.com/Fosowl/agenticSeek.git
cd agenticSeek
mv .env.example .env
```

### 2 **Créer un environnement virtuel**

```sh
python3 -m venv agentic_seek_env
source agentic_seek_env/bin/activate     
# Sur Windows: agentic_seek_env\Scripts\activate
```

### 3️⃣ **Installation**

**Automatique:**

```sh
./install.sh
```

**Manuel:**

**Note : Pour tous les systèmes d'exploitation, assurez-vous que le ChromeDriver que vous installez correspond à la version de Chrome installée. Exécutez `google-chrome --version`. Consultez les problèmes connus si vous avez Chrome >135**

- *Linux*:

Mettre à jour la liste des paquets : `sudo apt update`

Installer les dépendances : `sudo apt install -y alsa-utils portaudio19-dev python3-pyaudio libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1`

Installer ChromeDriver correspondant à la version de votre navigateur Chrome :
`sudo apt install -y chromium-chromedriver`

Installer les prérequis : `pip3 install -r requirements.txt`

- *macOS*:

Mettre à jour brew : `brew update`

Installer chromedriver : `brew install --cask chromedriver`

Installer portaudio : `brew install portaudio`

Mettre à jour pip : `python3 -m pip install --upgrade pip`

Mettre à jour wheel : `pip3 install --upgrade setuptools wheel`

Installer les prérequis : `pip3 install -r requirements.txt`

- *Windows*:

Installer pyreadline3 : `pip install pyreadline3`

Installer portaudio manuellement (par exemple, via vcpkg ou des binaires précompilés) puis exécutez : `pip install pyaudio`

Télécharger et installer chromedriver manuellement depuis : https://sites.google.com/chromium.org/driver/getting-started

Placez chromedriver dans un répertoire inclus dans votre PATH.

Installer les prérequis : `pip3 install -r requirements.txt`


## Faire fonctionner sur votre machine 

**Nous recommandons d’utiliser au minimum DeepSeek 14B, les modèles plus petits ont du mal avec l’utilisation des outils et oublient rapidement le contexte.**

Lancer votre provider local, par exemple avec ollama:
```sh
ollama serve
```

**Configurer le config.ini**

Modifiez le fichier config.ini pour définir provider_name sur un fournisseur supporté et provider_model sur un LLM compatible avec votre fournisseur. Nous recommandons des modèles de raisonnement comme *Qwen* ou *Deepseek*.

Consultez la section **FAQ** à la fin du README pour connaître le matériel requis.

```sh
[MAIN]
is_local = True # Si vous exécutez localement ou avec un fournisseur distant.
provider_name = ollama # ou lm-studio, openai, etc..
provider_model = deepseek-r1:14b # choisissez un modèle adapté à votre matériel
provider_server_address = 127.0.0.1:11434
agent_name = Jarvis # nom de votre IA
recover_last_session = True # récupérer ou non la session précédente
save_session = True # mémoriser ou non la session actuelle
speak = True # synthèse vocale
listen = False # reconnaissance vocale, uniquement pour CLI
work_dir =  /Users/mlg/Documents/workspace # L'espace de travail pour AgenticSeek.
jarvis_personality = False # Utiliser une personnalité plus "Jarvis", non recommandé avec des petits modèles
languages = en fr # Liste des langages, la synthèse vocale utilisera par défaut la première langue de la liste
[BROWSER]
headless_browser = True # Utiliser ou non le navigateur sans interface graphique, recommandé uniquement avec l'interface web.
stealth_mode = True # Utiliser selenium non détectable pour réduire la détection du navigateur
```

Remarque : Certains fournisseurs (ex : lm-studio) nécessitent `http://` devant l'adresse IP. Par exemple `http://127.0.0.1:1234`



**Liste des provideurs locaux**

| Fournisseur | Local ? | Description                                               |
|-------------|---------|-----------------------------------------------------------|
| ollama      | Oui     | Exécutez des LLM localement avec facilité en utilisant ollama comme fournisseur LLM |
| lm-studio   | Oui     | Exécutez un LLM localement avec LM studio (définissez `provider_name` sur `lm-studio`) |
| openai      | Oui     | Utilisez une API local compatible avec openai |


### **Démarrer les services & Exécuter**

Activez votre environnement Python si nécessaire.
```sh
source agentic_seek_env/bin/activate
```

Démarrez les services requis. Cela lancera tous les services définis dans le fichier docker-compose.yml, y compris :
    - searxng
    - redis (nécessaire pour searxng)
    - frontend

```sh
sudo ./start_services.sh # MacOS
start ./start_services.cmd # Windows
```

**Option 1 :** Exécuter avec l'interface CLI.

```sh
python3 cli.py
```

**Option 2 :** Exécuter avec l'interface Web.

Démarrez le backend.

```sh
python3 api.py
```

Allez sur `http://localhost:3000/` et vous devriez voir l'interface web.

Veuillez noter que l'interface web ne diffuse pas les messages en continu pour le moment.


Voyez la section **Utilisation** si vous ne comprenez pas comment l’utiliser

Voyez la section **Problèmes** connus si vous rencontrez des problèmes

Voyez la section **Exécuter avec une API** si votre matériel ne peut pas exécuter DeepSeek localement

Voyez la section **Configuration** pour une explication détaillée du fichier de configuration.

---

## Utilisation

Assurez-vous que les services sont en cours d’exécution avec ./start_services.sh et lancez AgenticSeek avec le CLI ou l'interface Web.

**CLI:**
Vous verrez un prompt : ">>> "  
Cela indique qu’AgenticSeek attend que vous saisissiez des instructions.  
Vous pouvez également utiliser la reconnaissance vocale en définissant `listen = True` dans la configuration.  
Pour quitter, dites simplement `goodbye`.  

**Interface:**

Assurez-vous d'avoir bien démarré le backend avec `python3 api.py`.  
Allez sur `localhost:3000` où vous verrez une interface web.  
Tapez simplement votre message et patientez.  
Si vous n'avez pas d'interface sur `localhost:3000`, c'est que vous n'avez pas démarré les services avec `start_services.sh`.

Voici quelques exemples d’utilisation :

### Programmation

> *Aide-moi avec la multiplication de matrices en Golang*

> *Initalize un nouveau project python, setup le readme, gitignore etc.. et fait un premier commit*

> *Fais un jeu snake en Python*

### Recherche web

> *Fais une recherche sur le web pour trouver des startups technologiques au Japon qui travaillent sur des recherches avancées en IA*

> *Peux-tu trouver sur internet qui a créé agenticSeek ?*

> *Peux-tu trouver sur quel site je peux acheter une RTX 4090 à bas prix ?*

### Fichier

> *Hé, peux-tu trouver où est contrat.pdf ? Je l’ai perdu*

> *Montre-moi combien d’espace il me reste sur mon disque*

> *Trouve et lis le fichier README.md et suis les instructions d’installation*

### Conversation

> *Parle-moi de la France*

> *Quel est le sens de la vie ?*

> *Donne moi une recette simple pour ce midi j'ai pas d'inspi*

Après avoir saisi votre requête, AgenticSeek attribuera le meilleur agent pour la tâche.

Le système de routage des agents peut parfois ne pas toujours attribuer le bon agent en fonction de votre requête.

Par conséquent, vous devez être assez explicite sur ce que vous voulez et sur la manière dont l’IA doit procéder. Par exemple, si vous voulez qu’elle effectue une recherche sur le web, ne dites pas :

Connait-tu de bons pays pour voyager seul ?

Dites plutôt :

Fait une recherche sur le web, quels sont les meilleurs pays pour voyager seul?

---

## **Exécuter le LLM sur votre propre serveur**  

Si vous disposez d’un ordinateur puissant ou d’un serveur que vous voulez utiliser, mais que vous souhaitez y accéder depuis votre ordinateur portable, vous avez la possibilité d’exécuter le LLM sur un serveur distant.

### 1️⃣  **Configurer et démarrer les scripts du serveur** 

Sur votre "serveur" qui exécutera le modèle IA, obtenez l’adresse IP

```sh
ip a | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1
```

Remarque : Pour Windows ou macOS, utilisez respectivement ipconfig ou ifconfig pour trouver l’adresse IP.

Clonez le dépôt et entrez dans le dossier server/.


```sh
git clone --depth 1 https://github.com/Fosowl/agenticSeek.git
cd agenticSeek/server/
```

Installez les dépendances spécifiques au serveur :

```sh
pip3 install -r requirements.txt
```

Exécutez le script du serveur.

```sh
python3 app.py --provider ollama --port 3333
```

Vous avez le choix entre utiliser ollama et llamacpp comme service LLM.

### 2️⃣ **Lancer** 

Maintenant, sur votre ordinateur personnel :

Modifiez le fichier config.ini pour définir provider_name sur server et provider_model sur deepseek-r1:14b.

Définissez provider_server_address sur l’adresse IP de la machine qui exécutera le modèle.

```sh
[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:14b
provider_server_address = x.x.x.x:3333
```

Ensuite, exécutez avec le CLI ou l'interface graphique comme expliqué dans la section pour les fournisseurs locaux.

## **Exécuter avec une API externe**  

AVERTISSEMENT : Assurez-vous qu’il n’y a pas d’espace en fin de ligne dans la configuration.

```sh
[MAIN]
is_local = False
provider_name = openai
provider_model = gpt-4o
provider_server_address = 127.0.0.1:5000 # n'importe pas
```

**Liste de provideurs API**
| Fournisseur  | Local ? | Description                                               |
|--------------|---------|-----------------------------------------------------------|
| openai       | Non  | Utilise l'API ChatGPT                                     |
| deepseek-api | Non     | API Deepseek (non privé)                                  |
| huggingface  | Non     | API Hugging-Face (non privé)                              |
| togetherAI   | Non     | Utilise l'API Together AI (non privé)                     |
| google       | Non     | Utilise l'API Google Gemini (non privé)                  |
| modelscope  | Non     | API ModelScope (non privé)                              |

Ensuite, exécutez avec le CLI ou l'interface graphique comme expliqué dans la section pour les fournisseurs locaux.

## Config

Exemple de configuration :
```
[MAIN]
is_local = True
provider_name = ollama
provider_model = deepseek-r1:1.5b
provider_server_address = 127.0.0.1:11434
agent_name = Friday
recover_last_session = False
save_session = False
speak = False
listen = False
work_dir =  /Users/mlg/Documents/ai_folder
jarvis_personality = False
languages = en fr
[BROWSER]
headless_browser = False
stealth_mode = False
```

**Explication du fichier config.ini**:

`is_local` -> Exécute l’agent localement (True) ou sur un serveur distant (False).

`provider_name` -> Le fournisseur à utiliser (parmi : ollama, server, lm-studio, deepseek-api).

`provider_model` -> Le modèle utilisé, par exemple, deepseek-r1:1.5b.

`provider_server_address` -> Adresse du serveur, par exemple, 127.0.0.1:11434 pour local. Définissez n’importe quoi pour une API non locale.

`agent_name` -> Nom de l’agent, par exemple, Friday. Utilisé comme mot déclencheur pour la reconnaissance vocale.

`recover_last_session` -> Reprend la dernière session (True) ou non (False).

`save_session` -> Sauvegarde les données de la session (True) ou non (False).

`speak` -> Active la sortie vocale (True) ou non (False).

`listen` -> Écoute les entrées vocales (True) ou non (False).

`work_dir` -> Dossier auquel l’IA aura accès, par exemple : /Users/user/Documents/.

`jarvis_personality` -> Utilise une personnalité inspiré de Jarvis (True) ou non (False). Cela utilise simplement une prompt alternative. Marche moins bien en français.

`headless_browser` -> Exécute le navigateur sans fenêtre visible (True) ou non (False).

`stealth_mode` -> Rend la détection des bots plus difficile. Le seul inconvénient est que vous devez installer manuellement l’extension anticaptcha.

`languages` -> La liste de languages supportés (nécessaire pour le routage d'agents). Plus la liste est longue. Plus un nombre important de modèles sera téléchargés.

## Providers

Le tableau ci-dessous montre les LLM providers disponibles :

| Provider  | Local? | Description                                               |
|-----------|--------|-----------------------------------------------------------|
| ollama    | Yes    | Exécutez des LLM localement avec facilité en utilisant Ollama comme fournisseur LLM 
| server    | Yes    | Hébergez le modèle sur une autre machine, exécutez sur votre machine locale 
| lm-studio  | Yes    | Exécutez un LLM localement avec LM Studio (définissez provider_name sur lm-studio) 
| openai    | No     | Utilise l'API ChatGPT (pas privé) |
| deepseek-api  | No     | Utilise l'API Deepseek (pas privé) |
| huggingface| No    | Utilise Hugging-Face (pas privé) |
| together| No    | Utilise l'api Together AI |
| modelscope| No    | Utilise ModelScope (pas privé) |

Pour sélectionner un provider LLM, modifiez le config.ini :

```
is_local = False
provider_name = openai
provider_model = gpt-4o
provider_server_address = 127.0.0.1:5000
```

`is_local` : doit être True pour tout LLM exécuté localement, sinon False.

`provider_name` : Sélectionnez le fournisseur à utiliser par son nom, voir la liste des fournisseurs ci-dessus.

`provider_model` : Définissez le modèle à utiliser par l’agent.

`provider_server_address` : peut être défini sur n’importe quoi si vous n’utilisez pas le fournisseur server.

# Problèmes connus 

## Problèmes avec Chromedriver

Erreur #1:**incompatibilité**

`Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

Cela se produit s’il y a une incompatibilité entre votre navigateur et la version de chromedriver.

Vous devez naviguer pour télécharger la dernière version :

https://developer.chrome.com/docs/chromedriver/downloads

Si vous utilisez Chrome version 115 ou plus récent, allez sur :

https://googlechromelabs.github.io/chrome-for-testing/

Et téléchargez la version de chromedriver correspondant à votre système d’exploitation.

![alt text](./media/chromedriver_readme.png)

Si cette section est incomplète, merci de faire une nouvelle issue sur github.

## FAQ
**Q: Quel matériel est nécessaire ?**  

| Taille du Modèle  | GPU  | Commentaire                                               |
|--------------------|------|----------------------------------------------------------|
| 7B                | 8 Go VRAM | ⚠️ Non recommandé. Performances médiocres, hallucinations fréquentes, et l'agent planificateur échouera probablement. |
| 14B               | 12 Go VRAM (par ex. RTX 3060) | ✅ Utilisable pour des tâches simples. Peut rencontrer des difficultés avec la navigation web et les tâches de planification. |
| 32B               | 24+ Go VRAM (par ex. RTX 4090) | 🚀 Réussite avec la plupart des tâches, peut encore avoir des difficultés avec la planification des tâches. |
| 70B+              | 48+ Go VRAM (par ex. Mac Studio) | 💪 Excellent. Recommandé pour des cas d'utilisation avancés. |

**Q: Pourquoi deepseek et pas un autre modèle**  

DeepSeek R1 excelle dans le raisonnement et l’utilisation d’outils pour sa taille. Nous pensons que c’est un choix solide pour nos besoins, bien que d’autres modèles fonctionnent également (bien que moins bien pour un nombre équivalent de paramètres).

**Q: J'ai une erreur quand je lance le programme, je fait quoi?**  

Assurez-vous qu’Ollama est en cours d’exécution (ollama serve), que votre config.ini correspond à votre fournisseur, et que les dépendances sont installées. Si cela ne fonctionne pas, n’hésitez pas à signaler un problème.

**Q: C'est vraiment 100% local?**  

Oui, avec les fournisseurs Ollama, lm-studio ou Server, toute la reconnaissance vocale, le LLM et la synthèse vocale fonctionnent localement. Les options non locales (OpenAI ou autres API) sont facultatives.

**Q: En quoi c'est supérieur à Manus**

Il ne l'est certainement pas, mais nous privilégions l’exécution locale et la confidentialité par rapport à une approche basée sur le cloud. C’est une alternative plus accessible et surtout moins cher !

## Contribution

Nous recherchons des développeurs pour améliorer AgenticSeek ! Consultez la section "issues" github ou les discussions.

[![Star History Chart](https://api.star-history.com/svg?repos=Fosowl/agenticSeek&type=Date)](https://www.star-history.com/#Fosowl/agenticSeek&Date)

[Guide du contributeur](./docs/CONTRIBUTING.md)

## Mainteneurs:
 > [Fosowl](https://github.com/Fosowl)
 > [steveh8758](https://github.com/steveh8758)
 > [antoineVIVIES](https://github.com/antoineVIVIES) | Taipei Time 
