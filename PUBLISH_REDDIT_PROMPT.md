# 🚀 ARIA Protocol v0.5.2 — Publication Reddit r/LocalLLaMA

## Contexte

Tu es dans le repo ARIA Protocol (`C:\Users\antho\Documents\aria-protocol`).
L'utilisateur (Anthony) est connecté sur Reddit (compte `anthonymu`) dans Microsoft Edge (profil "Personnel").
Le post HN est déjà live : https://news.ycombinator.com/item?id=46904770
Le thread Twitter est déjà live : https://x.com/MurgoAnthony/status/2019510218410061852

## Mission

Publier un post texte sur **r/LocalLLaMA** avec le contenu v0.5.2.

⚠️ Le compte a peu de karma. Le post risque d'être filtré par AutoModerator. C'est attendu — on publie quand même.

## Stack technique

Utilise **Playwright** avec **Chromium** en mode **persistent context** pour réutiliser les cookies/sessions Edge.

```bash
pip install playwright
playwright install chromium
```

Profil Edge : `C:\Users\antho\AppData\Local\Microsoft\Edge\User Data`

**IMPORTANT :** Toutes les fenêtres Edge doivent être fermées avant de lancer Playwright. Demande à l'utilisateur si nécessaire.

## Données du post

### Subreddit
`r/LocalLLaMA`

### Flair
Sélectionner **"New Model"** ou **"Resources"** ou **"Discussion"** si disponible. Si aucun flair obligatoire, ne pas en mettre.

### Titre
```
ARIA Protocol v0.5.2: P2P distributed inference with real 1-bit models — 120 tok/s (0.7B) and 36 tok/s (2.4B) on CPU only
```

### Corps du post (texte intégral)
```
Hey r/LocalLLaMA,

Quick update on ARIA Protocol — we just shipped v0.5.2 with a subprocess backend that calls llama-cli directly from bitnet.cpp, and we finally have proper comparative benchmarks with real models.

### What changed

The big addition is a **subprocess backend** that spawns llama-cli.exe (from Microsoft's bitnet.cpp build) as a child process for each inference. This sits alongside our native DLL backend (ctypes bindings) and simulation mode, giving us 3 backends total. The subprocess approach is slower than native due to process spawn overhead, but it's dead simple to set up — just point it at your bitnet.cpp build directory.

### Benchmark results

Tested on AMD Ryzen 9 7845HX, 8 threads, subprocess backend:

| Model | Params | Avg tok/s | Avg latency | Energy* |
|-------|--------|-----------|-------------|---------|
| BitNet-b1.58-large | 0.7B | **120.25** | 588 ms | ~8.8 J total (5 inferences) |
| BitNet-b1.58-2B-4T | 2.4B | **36.62** | 2,120 ms | ~31.8 J total (3 inferences) |

*Energy estimated via CPU-time × TDP/threads — not a direct hardware measurement. These are upper-bound estimates, not RAPL readings.

The 0.7B model hits 120 tok/s which is solidly usable for real-time applications. The 2.4B model at 36 tok/s is more than enough for interactive use cases.

### The stack

- **Inference:** Python calling llama-cli from bitnet.cpp (Microsoft Research's 1-bit runtime)
- **Networking:** WebSocket-based P2P with pipeline parallelism for model sharding
- **Consensus:** Blockchain provenance ledger + Proof of Useful Work (every computation is useful)
- **API:** OpenAI-compatible, drop-in replacement

### Why 1-bit?

You all know this already, but for the newcomers: 1-bit quantization (ternary weights: -1, 0, +1) makes inference memory-bound instead of compute-bound. No floating-point math needed. A 2.4B model fits in ~1.3 GB of RAM. This is what makes CPU-only inference viable — and it's why distributing across a P2P network makes sense. Scale out across machines, not up within one.

### Roadmap

- **v0.6.0** — Testnet alpha with public bootstrap nodes
- **v0.7.0** — Node reputation system and anti-Sybil mechanisms
- **v0.8.0** — Mobile nodes (iOS/Android with on-device inference)

MIT licensed, Python 3.10+, 176 tests passing.

- GitHub: https://github.com/spmfrance-cloud/aria-protocol
- Benchmark results: `benchmarks/results/`

Happy to answer any questions. If you've compiled bitnet.cpp, you can run the benchmarks yourself in about 2 minutes.
```

## Procédure

1. Naviguer vers `https://www.reddit.com/r/LocalLLaMA/submit`
2. Vérifier que l'utilisateur est connecté (chercher `anthonymu` dans la page)
3. Si Reddit redirige vers une nouvelle interface de soumission (`https://www.reddit.com/r/LocalLLaMA/submit?type=text`), c'est OK
4. Sélectionner le type **"Text"** (pas Link, pas Image)
5. Remplir le champ titre avec le titre ci-dessus
6. Remplir le champ corps avec le texte intégral ci-dessus
7. Le corps supporte le Markdown Reddit — les `###`, `**bold**`, tables `|` et listes `-` fonctionnent
8. Sélectionner un flair si requis par le subreddit (essayer "Resources" ou "New Model" ou "Discussion")
9. NE PAS cocher "Send me post reply notifications" si l'option existe (optionnel)
10. Screenshot AVANT soumission → `screenshots/reddit_before_submit.png`
11. Cliquer sur "Post" / "Submit"
12. Attendre 5 secondes
13. Screenshot APRÈS soumission → `screenshots/reddit_after_submit.png`
14. Vérifier le résultat :
    - Si le post est visible → capturer l'URL et afficher
    - Si message "post is awaiting moderator approval" → c'est normal, capturer le message
    - Si erreur "you are doing that too much" → attendre et réessayer
    - Si erreur karma/account age → capturer le message d'erreur

## Notes sur l'interface Reddit

- Reddit a deux interfaces : Old Reddit et New Reddit. Le script va probablement tomber sur New Reddit.
- Sur New Reddit, le composeur de post a des onglets : **Text**, **Images & Video**, **Link**, **Poll**. Sélectionner **Text**.
- Le champ de texte est un éditeur rich text. Pour coller du Markdown, il faut basculer en mode **Markdown** (chercher un bouton "Markdown Mode" ou un toggle "Fancy Pants Editor" / "Markdown").
- **CRITIQUE :** Si l'éditeur est en mode "Fancy Pants" (WYSIWYG), les tables Markdown ne seront pas rendues correctement. Il FAUT basculer en mode Markdown avant de coller le texte.
- Le champ titre a une limite de 300 caractères (le titre fait ~120 caractères, c'est OK).

## Gestion d'erreurs

- Si Playwright ne peut pas ouvrir le profil Edge → demander de fermer Edge
- Si pas connecté → alerter l'utilisateur
- Si le post est filtré/removed → c'est attendu (karma faible), capturer le message et informer l'utilisateur
- Si flair obligatoire et aucun ne correspond → essayer "Discussion"
- Si rate limited ("you are doing that too much") → attendre le temps indiqué et réessayer
- Créer `screenshots/` si le dossier n'existe pas

## Résultat attendu

```
✅ Reddit r/LocalLLaMA: [URL du post]
   Status: Published / Awaiting moderation / Filtered
📸 Screenshots sauvegardés dans ./screenshots/
```

Si le post est filtré, afficher :
```
⚠️ Post soumis mais probablement filtré (karma faible).
   Action suggérée : contacter les mods de r/LocalLLaMA via modmail
   pour demander l'approbation manuelle du post.
   Lien modmail : https://www.reddit.com/message/compose?to=/r/LocalLLaMA
```
