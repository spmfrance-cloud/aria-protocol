# ARIA Protocol — Guide Pas à Pas
## GitHub + Claude Code

---

# PARTIE 1 : PUBLIER SUR GITHUB

## Étape 1 : Créer ton compte GitHub (si pas déjà fait)

1. Va sur https://github.com
2. Clique "Sign up"
3. Utilise anthony.murgo@outlook.com
4. Choisis un username (suggestion : `anthonymurgo` ou `aria-protocol`)
5. Confirme ton email

## Étape 2 : Installer Git sur ton PC

### Windows :
1. Télécharge Git : https://git-scm.com/download/win
2. Installe avec les options par défaut
3. Ouvre "Git Bash" (installé avec Git)

### Mac :
1. Ouvre Terminal
2. Tape : `git --version` (ça proposera d'installer si pas présent)

### Linux :
```bash
sudo apt install git
```

## Étape 3 : Configurer Git avec ton identité

Ouvre un terminal (Git Bash sur Windows) et tape :

```bash
git config --global user.name "Anthony MURGO"
git config --global user.email "anthony.murgo@outlook.com"
```

## Étape 4 : Créer le repository sur GitHub

1. Va sur https://github.com/new
2. Repository name : `aria-protocol`
3. Description : `ARIA - Autonomous Responsible Intelligence Architecture. A peer-to-peer protocol for efficient, ethical, and decentralized AI inference.`
4. Choisis **Public**
5. NE COCHE PAS "Add a README" (on a déjà le nôtre)
6. License : None (on a déjà notre fichier LICENSE)
7. Clique "Create repository"

## Étape 5 : Extraire l'archive et pousser le code

Après avoir téléchargé `aria-protocol-v0.1.0.tar.gz` depuis Claude :

### Windows (Git Bash) :
```bash
# Va dans ton dossier Téléchargements (adapte le chemin si besoin)
cd ~/Downloads

# Extraire l'archive
tar -xzf aria-protocol-v0.1.0.tar.gz

# Entrer dans le dossier
cd aria-protocol

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit historique
git commit -m "ARIA Protocol v0.1.0 - Initial release

A peer-to-peer protocol for efficient, ethical, and decentralized AI inference.
Combining 1-bit model architectures, P2P distribution, and blockchain provenance.

Author: Anthony MURGO
License: MIT"

# Connecter à GitHub (remplace TON_USERNAME par ton username GitHub)
git remote add origin https://github.com/TON_USERNAME/aria-protocol.git

# Pousser le code
git branch -M main
git push -u origin main
```

GitHub te demandera tes identifiants. Tu peux soit :
- Utiliser un Personal Access Token (recommandé) : va dans GitHub > Settings > Developer settings > Personal access tokens > Generate new token
- Ou utiliser GitHub CLI : https://cli.github.com

## Étape 6 : Vérifier

Va sur `https://github.com/TON_USERNAME/aria-protocol` — tu devrais voir tous tes fichiers avec le README affiché.

---

# PARTIE 2 : INSTALLER CLAUDE CODE

## Étape 1 : Installer Node.js

Claude Code nécessite Node.js 18+.

1. Va sur https://nodejs.org
2. Télécharge la version LTS (Long Term Support)
3. Installe avec les options par défaut
4. Vérifie dans un terminal :
```bash
node --version   # Doit afficher v18+ ou v20+
npm --version    # Doit afficher un numéro
```

## Étape 2 : Installer Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

## Étape 3 : Lancer Claude Code dans ton projet

```bash
# Va dans le dossier du projet
cd ~/Downloads/aria-protocol   # ou là où tu l'as extrait

# Lance Claude Code
claude
```

La première fois, Claude Code te demandera ta clé API Anthropic.
- Va sur https://console.anthropic.com
- Crée un compte si nécessaire
- Génère une API key
- Colle-la quand demandé

---

# PARTIE 3 : PROMPTS CLAUDE CODE

## Comment utiliser ces prompts

1. Lance `claude` dans le dossier aria-protocol
2. Copie-colle chaque prompt un par un
3. Laisse Claude Code travailler
4. Vérifie le résultat
5. Commit après chaque étape réussie :
   ```bash
   git add . && git commit -m "description de ce qui a été fait"
   git push
   ```

---

## PROMPT 1 : Structure professionnelle du projet

```
Examine le projet ARIA Protocol dans ce dossier. C'est un protocole P2P pour 
l'inférence IA distribuée utilisant des modèles 1-bit sur CPU.

Restructure le projet de manière professionnelle :

1. Ajoute un pyproject.toml avec les métadonnées du projet :
   - name: aria-protocol
   - version: 0.1.0  
   - author: Anthony MURGO <anthony.murgo@outlook.com>
   - license: MIT
   - python_requires: >=3.10
   - Dépendances : asyncio, aiohttp, cryptography

2. Ajoute un .gitignore pour Python

3. Ajoute un dossier tests/ avec un fichier test pour chaque module :
   - tests/test_consent.py
   - tests/test_ledger.py
   - tests/test_inference.py
   - tests/test_proof.py
   - tests/test_node.py
   Chaque test doit couvrir les fonctions principales du module.

4. Ajoute un Makefile avec les commandes :
   - make install (pip install -e .)
   - make test (pytest)
   - make demo (python examples/demo.py)

5. Vérifie que tous les tests passent.

Conserve tout le code existant tel quel, ajoute seulement la structure autour.
```

---

## PROMPT 2 : Vrai networking P2P avec asyncio

```
Dans le projet ARIA Protocol, remplace le networking simulé dans 
aria/network.py par une vraie implémentation réseau utilisant asyncio 
et aiohttp (ou websockets).

Voici ce que je veux :

1. Chaque ARIANode doit pouvoir écouter sur un port (WebSocket server)
2. Les nodes doivent pouvoir se connecter les uns aux autres
3. Implémente le protocole de messages existant (ping, peer_announce, 
   shard_announce, inference_request) sur de vrais WebSockets
4. Ajoute un mécanisme de bootstrap : un node peut se connecter à une 
   liste de peers connus pour découvrir le réseau
5. Implémente le heartbeat : les nodes s'envoient un ping toutes les 
   30 secondes pour rester vivants

Mets à jour le node.py pour utiliser le vrai networking.
Mets à jour examples/demo.py pour lancer 3 vrais nodes sur localhost 
avec des ports différents (8765, 8766, 8767) et faire une vraie 
communication réseau entre eux.

Assure-toi que la démo fonctionne en lançant les 3 nodes comme des 
tâches asyncio concurrentes.

Le tout doit rester simple et lisible. Pas de framework externe lourd.
```

---

## PROMPT 3 : Vrai pipeline d'inférence distribuée

```
Dans le projet ARIA Protocol, améliore aria/inference.py pour 
implémenter un vrai pipeline d'inférence distribuée :

1. Quand un node reçoit une requête et ne possède qu'un shard du modèle,
   il doit :
   a. Traiter ses couches locales
   b. Envoyer les activations intermédiaires au node suivant dans le pipeline
   c. Le dernier node retourne le résultat au demandeur

2. Implémente le routage de pipeline : le network.py doit savoir quel 
   node possède quels shards et construire la chaîne complète 
   (node1:L0-7 → node2:L8-15 → node3:L16-23)

3. Ajoute la sérialisation/désérialisation des activations intermédiaires 
   (utilise msgpack ou simplement json avec base64 pour les flottants)

4. Ajoute un timeout : si un node dans la chaîne ne répond pas en 5 secondes,
   le système bascule sur une réplique (fallback)

Mets à jour la démo pour montrer une inférence qui traverse réellement 
les 3 nodes du réseau.
```

---

## PROMPT 4 : CLI (Command Line Interface)

```
Ajoute une interface en ligne de commande (CLI) au projet ARIA Protocol 
en utilisant argparse ou click.

Commandes :

1. aria node start --port 8765 --cpu 25 --schedule "08:00-22:00"
   → Lance un node ARIA avec les paramètres de consentement donnés

2. aria node status
   → Affiche les stats du node (inférences, tokens gagnés, énergie, peers)

3. aria network peers
   → Liste les peers connectés

4. aria infer "What is AI?" --model aria-2b-1bit
   → Envoie une requête d'inférence au réseau

5. aria ledger stats
   → Affiche les statistiques du ledger (blocks, inférences, validation)

6. aria ledger verify
   → Vérifie l'intégrité de la chaîne

Ajoute le entry_point dans pyproject.toml pour que "aria" soit une 
commande disponible après installation.
```

---

## PROMPT 5 : API compatible OpenAI

```
Ajoute un serveur API HTTP dans aria/api.py qui est compatible avec 
l'API OpenAI chat completions.

1. Endpoint POST /v1/chat/completions qui accepte :
   {
     "model": "aria-2b-1bit",
     "messages": [{"role": "user", "content": "Hello"}],
     "max_tokens": 100,
     "temperature": 0.7,
     "stream": false
   }

2. La réponse doit suivre exactement le format OpenAI :
   {
     "id": "aria-xxx",
     "object": "chat.completion",
     "model": "aria-2b-1bit",
     "choices": [{"message": {"role": "assistant", "content": "..."}}],
     "usage": {"prompt_tokens": X, "completion_tokens": Y, "total_tokens": Z}
   }

3. Ajoute un header custom X-ARIA-Provenance avec le hash de l'inference 
   record pour la traçabilité

4. Ajoute un endpoint GET /v1/models qui liste les modèles disponibles

5. Ajoute un endpoint GET /aria/stats qui retourne les stats du réseau

Utilise aiohttp pour le serveur HTTP. Ajoute la commande CLI :
aria api start --port 3000

L'objectif : n'importe quel outil compatible OpenAI (continue.dev, 
Cursor, etc.) peut utiliser ARIA comme backend en changeant juste l'URL.
```

---

## PROMPT 6 : Dashboard web simple

```
Crée un dashboard web minimaliste pour ARIA dans aria/dashboard.py.

Un seul fichier HTML servi par le même serveur aiohttp que l'API.

Le dashboard doit afficher en temps réel (polling toutes les 2 secondes) :

1. Nombre de nodes connectés
2. Nombre total d'inférences
3. Énergie totale consommée vs GPU equivalent (avec pourcentage d'économie)
4. Tokens ARIA distribués
5. Liste des dernières 10 inférences (timestamp, node, latency, energy)
6. Status de la blockchain (blocks, valid/invalid)

Design : sombre, minimaliste, utilise uniquement HTML/CSS/JS vanilla.
Pas de framework front-end. Un seul fichier HTML inline.

Le dashboard est accessible sur GET /dashboard quand le serveur API tourne.
```

---

## PROMPT 7 : Intégration BitNet (avancé)

```
Ajoute une intégration optionnelle avec bitnet.cpp dans aria/inference.py.

1. Si bitnet.cpp est installé sur le système, utilise-le pour la vraie 
   inférence 1-bit. Sinon, utilise le mode simulation existant.

2. Ajoute une fonction qui :
   a. Vérifie si bitnet.cpp est disponible dans le PATH
   b. Télécharge un petit modèle 1-bit depuis HuggingFace 
      (BitNet b1.58 2B4T) si pas déjà présent
   c. Lance l'inférence via bitnet.cpp en subprocess
   d. Parse le résultat et le retourne dans notre format InferenceResult

3. Ajoute la commande CLI : aria model download aria-2b-1bit
   qui télécharge le modèle dans ~/.aria/models/

4. Le fallback vers la simulation doit être transparent.

Documente clairement comment installer bitnet.cpp en prérequis optionnel.
```

---

## PROMPT 8 : Documentation complète

```
Génère la documentation complète du projet ARIA Protocol :

1. docs/architecture.md — Explication détaillée de l'architecture 3 couches
2. docs/getting-started.md — Guide de démarrage rapide (5 minutes)
3. docs/api-reference.md — Référence complète de l'API Python et HTTP
4. docs/contributing.md — Guide de contribution pour les développeurs
5. docs/security.md — Modèle de menaces et mesures de sécurité

Mets à jour le README.md pour pointer vers ces docs.

Style : technique mais accessible. Un développeur junior doit pouvoir 
comprendre et commencer à contribuer en 30 minutes.

Auteur partout : Anthony MURGO
```

---

# PARTIE 4 : WORKFLOW QUOTIDIEN

Après chaque session Claude Code, fais :

```bash
# Vérifier les changements
git status
git diff

# Committer
git add .
git commit -m "Description claire de ce qui a été fait"

# Pousser sur GitHub
git push
```

## Ordre recommandé des prompts :

1. Structure (Prompt 1) — 15 min
2. Tests (déjà dans Prompt 1) — 0 min
3. Vrai networking (Prompt 2) — 30 min
4. Pipeline distribué (Prompt 3) — 30 min
5. CLI (Prompt 4) — 20 min
6. API OpenAI (Prompt 5) — 20 min
7. Dashboard (Prompt 6) — 15 min
8. BitNet (Prompt 7) — 30 min
9. Documentation (Prompt 8) — 15 min

Total estimé : ~3 heures de travail avec Claude Code.

---

# PARTIE 5 : APRÈS LA PUBLICATION

## Rendre le projet visible

1. **GitHub Topics** : Va dans Settings du repo, ajoute les topics :
   `ai`, `decentralized`, `p2p`, `inference`, `1-bit`, `blockchain`, 
   `protocol`, `cpu`, `efficient-ai`, `open-source`

2. **GitHub About** : Ajoute la description et le lien vers le whitepaper

3. **Releases** : Va dans Releases > Create release
   - Tag : v0.1.0
   - Title : ARIA Protocol v0.1.0 - Genesis
   - Upload le PDF du whitepaper comme asset
   - Description :
   ```
   Initial release of the ARIA Protocol.
   
   Includes:
   - Whitepaper: "ARIA: A Peer-to-Peer Efficient AI Inference Protocol"
   - Reference implementation in Python (~800 lines)
   - Working demo with 3 nodes, provenance ledger, and energy tracking
   
   Author: Anthony MURGO
   License: MIT
   ```

## Où partager

1. **Hacker News** : https://news.ycombinator.com/submit
   - Title : "Show HN: ARIA – A P2P protocol for 1-bit AI inference on CPUs"
   - URL : lien GitHub

2. **Reddit** :
   - r/MachineLearning (flair: [Project])
   - r/decentralization
   - r/cryptocurrency (pour l'aspect blockchain)
   - r/selfhosted

3. **Twitter/X** :
   Thread suggested :
   "I just open-sourced ARIA Protocol — a P2P system for running AI 
   on regular CPUs using 1-bit models.
   
   No GPU needed. 77% less energy. Every inference is traceable on-chain.
   
   3 new ideas:
   🔥 Proof of Useful Work (mining = inference)
   ⚡ Proof of Sobriety (every joule counted)
   🤝 Consent Contracts (your device, your rules)
   
   Whitepaper + working code: [link]
   MIT licensed. Fork it. Build on it."

4. **LinkedIn** : Post professionnel avec ton background

5. **arXiv** (optionnel) : Soumettre le whitepaper sur arxiv.org 
   catégorie cs.DC (Distributed Computing) ou cs.AI

---

Anthony MURGO — ARIA Protocol, 2026
