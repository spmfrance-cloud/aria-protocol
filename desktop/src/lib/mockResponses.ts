// FALLBACK: Mock response used when Tauri backend is unavailable (browser dev mode)
import { SupportedLanguage, detectLanguage } from "./detectLanguage";

interface LocalizedMockResponse {
  pattern: RegExp;
  responses: Record<SupportedLanguage, string[]>;
}

const mockResponses: LocalizedMockResponse[] = [
  {
    // Greetings - all languages
    pattern:
      /\b(hello|hi|hey|bonjour|salut|hola|hallo|olá|ciao|こんにちは|안녕|你好|привет|مرحبا|नमस्ते)\b/iu,
    responses: {
      en: [
        "Hello! I'm your local ARIA assistant, running entirely on your machine with BitNet inference. How can I help you today?\n\nI can assist with:\n- **Understanding ARIA Protocol** and decentralized AI\n- **Model performance** benchmarks and optimization\n- **Technical questions** about 1-bit LLMs\n- **General conversation** and brainstorming",
        "Hey there! Welcome to ARIA's local AI assistant. I'm powered by BitNet and running 100% offline on your hardware — no data leaves your device.\n\nWhat would you like to explore today?",
        "Hi! I'm ARIA's on-device assistant. Everything runs locally with **zero cloud dependency**. Ask me anything about decentralized AI, BitNet models, or just chat freely!",
      ],
      fr: [
        "Bonjour ! Je suis votre assistant ARIA local, fonctionnant entièrement sur votre machine avec l'inférence BitNet. Comment puis-je vous aider aujourd'hui ?\n\nJe peux vous aider avec :\n- **Comprendre le protocole ARIA** et l'IA décentralisée\n- **Performances des modèles** et optimisation\n- **Questions techniques** sur les LLM 1-bit\n- **Conversation générale** et brainstorming",
        "Salut ! Bienvenue sur l'assistant IA local d'ARIA. Je fonctionne avec BitNet, 100% hors ligne sur votre matériel — aucune donnée ne quitte votre appareil.\n\nQue souhaitez-vous explorer aujourd'hui ?",
        "Bonjour ! Je suis l'assistant ARIA sur votre appareil. Tout fonctionne localement, **sans dépendance au cloud**. Posez-moi des questions sur l'IA décentralisée, les modèles BitNet, ou discutons librement !",
      ],
      es: [
        "¡Hola! Soy tu asistente ARIA local, ejecutándome completamente en tu máquina con inferencia BitNet. ¿En qué puedo ayudarte hoy?\n\nPuedo asistirte con:\n- **Entender el Protocolo ARIA** e IA descentralizada\n- **Rendimiento de modelos** y optimización\n- **Preguntas técnicas** sobre LLMs de 1-bit\n- **Conversación general** y lluvia de ideas",
        "¡Hola! Bienvenido al asistente de IA local de ARIA. Funciono con BitNet, 100% sin conexión en tu hardware — ningún dato sale de tu dispositivo.\n\n¿Qué te gustaría explorar hoy?",
      ],
      de: [
        "Hallo! Ich bin dein lokaler ARIA-Assistent und laufe vollständig auf deinem Rechner mit BitNet-Inferenz. Wie kann ich dir heute helfen?\n\nIch kann dir helfen mit:\n- **ARIA-Protokoll verstehen** und dezentralisierte KI\n- **Modell-Performance** und Optimierung\n- **Technische Fragen** zu 1-bit LLMs\n- **Allgemeine Gespräche** und Brainstorming",
        "Hey! Willkommen beim lokalen KI-Assistenten von ARIA. Ich laufe mit BitNet, 100% offline auf deiner Hardware — keine Daten verlassen dein Gerät.\n\nWas möchtest du heute erkunden?",
      ],
      pt: [
        "Olá! Sou seu assistente ARIA local, rodando inteiramente na sua máquina com inferência BitNet. Como posso ajudá-lo hoje?\n\nPosso ajudar com:\n- **Entender o Protocolo ARIA** e IA descentralizada\n- **Performance de modelos** e otimização\n- **Perguntas técnicas** sobre LLMs de 1-bit\n- **Conversa geral** e brainstorming",
        "Oi! Bem-vindo ao assistente de IA local do ARIA. Funciono com BitNet, 100% offline no seu hardware — nenhum dado sai do seu dispositivo.\n\nO que você gostaria de explorar hoje?",
      ],
      it: [
        "Ciao! Sono il tuo assistente ARIA locale, funziono interamente sulla tua macchina con inferenza BitNet. Come posso aiutarti oggi?\n\nPosso assisterti con:\n- **Capire il Protocollo ARIA** e IA decentralizzata\n- **Performance dei modelli** e ottimizzazione\n- **Domande tecniche** sui LLM a 1-bit\n- **Conversazione generale** e brainstorming",
        "Ciao! Benvenuto nell'assistente IA locale di ARIA. Funziono con BitNet, 100% offline sul tuo hardware — nessun dato lascia il tuo dispositivo.\n\nCosa vorresti esplorare oggi?",
      ],
      ja: [
        "こんにちは！私はARIAのローカルアシスタントです。BitNet推論であなたのマシン上で完全に動作しています。今日はどのようにお手伝いできますか？\n\nお手伝いできること：\n- **ARIAプロトコル**と分散型AIの理解\n- **モデルのパフォーマンス**とベンチマーク\n- **1-bit LLM**に関する技術的な質問\n- **一般的な会話**とブレインストーミング",
        "こんにちは！ARIAのローカルAIアシスタントへようこそ。BitNetで動作し、あなたのハードウェア上で100%オフラインで実行されています。データは一切外部に送信されません。\n\n今日は何を探求しますか？",
      ],
      ko: [
        "안녕하세요! 저는 BitNet 추론으로 귀하의 컴퓨터에서 완전히 실행되는 ARIA 로컬 어시스턴트입니다. 오늘 무엇을 도와드릴까요?\n\n도움을 드릴 수 있는 분야:\n- **ARIA 프로토콜** 및 분산형 AI 이해\n- **모델 성능** 벤치마크 및 최적화\n- **1-bit LLM**에 대한 기술적 질문\n- **일반 대화** 및 브레인스토밍",
        "안녕하세요! ARIA의 로컬 AI 어시스턴트에 오신 것을 환영합니다. BitNet으로 구동되며 귀하의 하드웨어에서 100% 오프라인으로 실행됩니다. 데이터는 기기를 떠나지 않습니다.\n\n오늘 무엇을 탐색하고 싶으신가요?",
      ],
      zh: [
        "你好！我是你的ARIA本地助手，通过BitNet推理完全在你的设备上运行。今天我能帮你什么？\n\n我可以帮助你：\n- **了解ARIA协议**和去中心化AI\n- **模型性能**基准测试和优化\n- **技术问题**关于1-bit LLM\n- **日常对话**和头脑风暴",
        "你好！欢迎使用ARIA的本地AI助手。我使用BitNet，100%离线运行在你的硬件上——没有数据会离开你的设备。\n\n今天你想探索什么？",
      ],
      ru: [
        "Привет! Я ваш локальный помощник ARIA, работающий полностью на вашем устройстве с помощью BitNet. Чем могу помочь сегодня?\n\nЯ могу помочь с:\n- **Пониманием протокола ARIA** и децентрализованного ИИ\n- **Производительностью моделей** и оптимизацией\n- **Техническими вопросами** о 1-bit LLM\n- **Общением** и мозговым штурмом",
        "Привет! Добро пожаловать в локальный ИИ-помощник ARIA. Я работаю на BitNet, 100% офлайн на вашем оборудовании — никакие данные не покидают ваше устройство.\n\nЧто бы вы хотели узнать сегодня?",
      ],
      ar: [
        "مرحبًا! أنا مساعد ARIA المحلي الخاص بك، أعمل بالكامل على جهازك باستخدام استدلال BitNet. كيف يمكنني مساعدتك اليوم؟\n\nيمكنني المساعدة في:\n- **فهم بروتوكول ARIA** والذكاء الاصطناعي اللامركزي\n- **أداء النماذج** والتحسين\n- **الأسئلة التقنية** حول نماذج 1-bit LLM\n- **المحادثة العامة** والعصف الذهني",
      ],
      hi: [
        "नमस्ते! मैं आपका स्थानीय ARIA सहायक हूँ, BitNet अनुमान के साथ पूरी तरह से आपकी मशीन पर चल रहा हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?\n\nमैं इनमें मदद कर सकता हूँ:\n- **ARIA प्रोटोकॉल** और विकेंद्रीकृत AI को समझना\n- **मॉडल प्रदर्शन** बेंचमार्क और अनुकूलन\n- **तकनीकी प्रश्न** 1-bit LLM के बारे में\n- **सामान्य बातचीत** और विचार-मंथन",
      ],
    },
  },
  {
    // ARIA / Protocol / Decentralized
    pattern:
      /\b(aria|protocol|decentralized|décentralisé|descentralizado|dezentral|decentralizzato|分散型|탈중앙|去中心化|децентрализ|لامركزي|विकेंद्रीकृत)\b/iu,
    responses: {
      en: [
        "**ARIA Protocol** is a decentralized AI inference network that enables anyone to run and share AI models locally.\n\n### Core Principles\n- **Decentralization**: No single point of failure or control\n- **Privacy**: All inference happens on-device by default\n- **Efficiency**: Built on 1-bit LLMs (BitNet) for minimal resource usage\n- **Accessibility**: Runs on consumer hardware — no GPU required\n\n### Architecture\n```\nUser Request → Local Node → BitNet Inference → Response\n                  ↕\n           ARIA P2P Network\n                  ↕\n            Other Nodes (optional)\n```\n\nThe protocol coordinates distributed inference across a peer-to-peer network while keeping data sovereignty with each node operator.",
        "ARIA Protocol is pioneering **decentralized AI** by leveraging 1-bit quantized models (BitNet) that run efficiently on CPUs.\n\n### Key Features\n- **Local-first**: Models run on your hardware\n- **P2P Network**: Nodes collaborate for larger workloads\n- **Energy efficient**: Up to 71x less energy than FP16 models\n- **Open source**: Fully transparent and community-driven\n\nThe goal is to democratize AI by removing the dependency on centralized cloud providers and expensive GPU infrastructure.",
      ],
      fr: [
        "**Le Protocole ARIA** est un réseau d'inférence IA décentralisé qui permet à quiconque d'exécuter et de partager des modèles IA localement.\n\n### Principes fondamentaux\n- **Décentralisation** : Aucun point unique de défaillance ou de contrôle\n- **Confidentialité** : Toute l'inférence se fait sur l'appareil par défaut\n- **Efficacité** : Basé sur les LLM 1-bit (BitNet) pour une utilisation minimale des ressources\n- **Accessibilité** : Fonctionne sur du matériel grand public — pas de GPU requis\n\n### Architecture\n```\nRequête → Nœud Local → Inférence BitNet → Réponse\n              ↕\n       Réseau P2P ARIA\n              ↕\n       Autres Nœuds (optionnel)\n```\n\nLe protocole coordonne l'inférence distribuée à travers un réseau pair-à-pair tout en gardant la souveraineté des données avec chaque opérateur de nœud.",
      ],
      es: [
        "**El Protocolo ARIA** es una red de inferencia de IA descentralizada que permite a cualquiera ejecutar y compartir modelos de IA localmente.\n\n### Principios fundamentales\n- **Descentralización**: Sin punto único de fallo o control\n- **Privacidad**: Toda la inferencia ocurre en el dispositivo por defecto\n- **Eficiencia**: Construido sobre LLMs de 1-bit (BitNet) para uso mínimo de recursos\n- **Accesibilidad**: Funciona en hardware de consumo — no requiere GPU\n\nEl objetivo es democratizar la IA eliminando la dependencia de proveedores cloud centralizados e infraestructura GPU costosa.",
      ],
      de: [
        "**ARIA-Protokoll** ist ein dezentralisiertes KI-Inferenz-Netzwerk, das es jedem ermöglicht, KI-Modelle lokal auszuführen und zu teilen.\n\n### Kernprinzipien\n- **Dezentralisierung**: Kein einzelner Ausfallpunkt oder Kontrollpunkt\n- **Datenschutz**: Alle Inferenz findet standardmäßig auf dem Gerät statt\n- **Effizienz**: Basiert auf 1-bit LLMs (BitNet) für minimalen Ressourcenverbrauch\n- **Zugänglichkeit**: Läuft auf Consumer-Hardware — keine GPU erforderlich\n\nDas Ziel ist die Demokratisierung von KI durch Beseitigung der Abhängigkeit von zentralisierten Cloud-Anbietern.",
      ],
      pt: [
        "**O Protocolo ARIA** é uma rede de inferência de IA descentralizada que permite a qualquer pessoa executar e compartilhar modelos de IA localmente.\n\n### Princípios fundamentais\n- **Descentralização**: Sem ponto único de falha ou controle\n- **Privacidade**: Toda inferência acontece no dispositivo por padrão\n- **Eficiência**: Construído em LLMs de 1-bit (BitNet) para uso mínimo de recursos\n- **Acessibilidade**: Funciona em hardware comum — não requer GPU\n\nO objetivo é democratizar a IA removendo a dependência de provedores de nuvem centralizados.",
      ],
      it: [
        "**Il Protocollo ARIA** è una rete di inferenza IA decentralizzata che permette a chiunque di eseguire e condividere modelli IA localmente.\n\n### Principi fondamentali\n- **Decentralizzazione**: Nessun singolo punto di fallimento o controllo\n- **Privacy**: Tutta l'inferenza avviene sul dispositivo per impostazione predefinita\n- **Efficienza**: Costruito su LLM a 1-bit (BitNet) per un utilizzo minimo delle risorse\n- **Accessibilità**: Funziona su hardware consumer — nessuna GPU richiesta\n\nL'obiettivo è democratizzare l'IA eliminando la dipendenza dai provider cloud centralizzati.",
      ],
      ja: [
        "**ARIAプロトコル**は、誰でもローカルでAIモデルを実行・共有できる分散型AI推論ネットワークです。\n\n### 基本原則\n- **分散化**: 単一障害点や制御点なし\n- **プライバシー**: すべての推論はデフォルトでデバイス上で実行\n- **効率性**: 最小限のリソース使用のための1-bit LLM（BitNet）基盤\n- **アクセシビリティ**: 一般消費者向けハードウェアで動作 — GPUは不要\n\n目標は、中央集権的なクラウドプロバイダーへの依存を排除してAIを民主化することです。",
      ],
      ko: [
        "**ARIA 프로토콜**은 누구나 AI 모델을 로컬에서 실행하고 공유할 수 있는 분산형 AI 추론 네트워크입니다.\n\n### 핵심 원칙\n- **탈중앙화**: 단일 장애점이나 제어점 없음\n- **프라이버시**: 모든 추론은 기본적으로 기기에서 수행\n- **효율성**: 최소한의 리소스 사용을 위한 1-bit LLM (BitNet) 기반\n- **접근성**: 일반 소비자 하드웨어에서 실행 — GPU 불필요\n\n목표는 중앙 집중식 클라우드 제공업체에 대한 의존성을 제거하여 AI를 민주화하는 것입니다.",
      ],
      zh: [
        "**ARIA协议**是一个去中心化的AI推理网络，使任何人都可以在本地运行和共享AI模型。\n\n### 核心原则\n- **去中心化**: 没有单点故障或控制\n- **隐私**: 所有推理默认在设备上进行\n- **效率**: 基于1-bit LLM（BitNet）实现最小资源使用\n- **可访问性**: 在消费级硬件上运行 — 不需要GPU\n\n目标是通过消除对中心化云提供商的依赖来实现AI民主化。",
      ],
      ru: [
        "**Протокол ARIA** — это децентрализованная сеть AI-инференса, которая позволяет любому запускать и делиться AI-моделями локально.\n\n### Основные принципы\n- **Децентрализация**: Нет единой точки отказа или контроля\n- **Конфиденциальность**: Весь инференс происходит на устройстве по умолчанию\n- **Эффективность**: Построен на 1-bit LLM (BitNet) для минимального использования ресурсов\n- **Доступность**: Работает на потребительском оборудовании — GPU не требуется\n\nЦель — демократизировать ИИ, устранив зависимость от централизованных облачных провайдеров.",
      ],
      ar: [
        "**بروتوكول ARIA** هو شبكة استدلال ذكاء اصطناعي لامركزية تتيح لأي شخص تشغيل ومشاركة نماذج الذكاء الاصطناعي محليًا.\n\n### المبادئ الأساسية\n- **اللامركزية**: لا توجد نقطة فشل أو تحكم واحدة\n- **الخصوصية**: يتم الاستدلال على الجهاز افتراضيًا\n- **الكفاءة**: مبني على نماذج 1-bit LLM (BitNet) لاستخدام موارد أقل\n- **إمكانية الوصول**: يعمل على أجهزة المستهلكين — لا يتطلب GPU",
      ],
      hi: [
        "**ARIA प्रोटोकॉल** एक विकेंद्रीकृत AI अनुमान नेटवर्क है जो किसी को भी AI मॉडल को स्थानीय रूप से चलाने और साझा करने में सक्षम बनाता है।\n\n### मूल सिद्धांत\n- **विकेंद्रीकरण**: कोई एकल विफलता या नियंत्रण बिंदु नहीं\n- **गोपनीयता**: सभी अनुमान डिफ़ॉल्ट रूप से डिवाइस पर होते हैं\n- **दक्षता**: न्यूनतम संसाधन उपयोग के लिए 1-bit LLM (BitNet) पर निर्मित\n- **पहुंच**: उपभोक्ता हार्डवेयर पर चलता है — GPU की आवश्यकता नहीं\n\nलक्ष्य केंद्रीकृत क्लाउड प्रदाताओं पर निर्भरता को हटाकर AI को लोकतांत्रिक बनाना है।",
      ],
    },
  },
  {
    // BitNet / 1-bit / quantization / energy
    pattern:
      /\b(bitnet|1-bit|quantiz|energy|énergie|energía|energie|energia|エネルギー|에너지|能源|энергия|طاقة|ऊर्जा)\b/iu,
    responses: {
      en: [
        "**BitNet** is a revolutionary approach to large language models using **1-bit quantization**.\n\n### How It Works\nTraditional LLMs use 16-bit or 32-bit floating point weights. BitNet constrains weights to just **{-1, 0, 1}**, which means:\n\n```\nTraditional: multiply + accumulate (expensive)\nBitNet:      add/subtract only (cheap & fast)\n```\n\n### Benefits\n- **Memory**: 8-10x reduction in model size\n- **Speed**: Matrix multiplications become simple additions\n- **Energy**: 71.4x less energy consumption\n- **Hardware**: No GPU required — runs on any CPU\n\n### Available Models in ARIA\n1. **BitNet-b1.58-large** (0.7B) — Fast, lightweight\n2. **BitNet-b1.58-2B-4T** (2.4B) — Best balance ⭐\n3. **Llama3-8B-1.58** (8B) — Most capable",
        "Energy efficiency is a **core pillar** of ARIA Protocol.\n\n### The Problem\nTraditional AI inference is energy-intensive:\n- A single ChatGPT query uses ~10x more energy than a Google search\n- Data centers account for 1-2% of global electricity\n\n### ARIA's Solution\nBy using **BitNet 1-bit models**:\n- **71.4x** less energy per token vs FP16\n- **CPU-only** inference — no power-hungry GPUs\n- **Distributed** workload across efficient nodes\n\n| Metric | Traditional | ARIA (BitNet) |\n|--------|------------|---------------|\n| Energy/token | 170 mJ | 2.4 mJ |\n| Hardware | A100 GPU | Laptop CPU |\n\nDecentralized AI doesn't just protect privacy — it's better for the planet.",
      ],
      fr: [
        "**BitNet** est une approche révolutionnaire des grands modèles de langage utilisant la **quantification 1-bit**.\n\n### Comment ça fonctionne\nLes LLM traditionnels utilisent des poids en virgule flottante 16-bit ou 32-bit. BitNet contraint les poids à seulement **{-1, 0, 1}**, ce qui signifie :\n\n```\nTraditionnel: multiplication + accumulation (coûteux)\nBitNet:       addition/soustraction uniquement (rapide)\n```\n\n### Avantages\n- **Mémoire**: Réduction de 8-10x de la taille du modèle\n- **Vitesse**: Les multiplications matricielles deviennent de simples additions\n- **Énergie**: 71.4x moins de consommation d'énergie\n- **Matériel**: Pas de GPU requis — fonctionne sur n'importe quel CPU\n\n### Modèles disponibles dans ARIA\n1. **BitNet-b1.58-large** (0.7B) — Rapide, léger\n2. **BitNet-b1.58-2B-4T** (2.4B) — Meilleur équilibre ⭐\n3. **Llama3-8B-1.58** (8B) — Le plus capable",
      ],
      es: [
        "**BitNet** es un enfoque revolucionario para modelos de lenguaje grandes usando **cuantización de 1-bit**.\n\n### Cómo funciona\nLos LLMs tradicionales usan pesos de punto flotante de 16-bit o 32-bit. BitNet restringe los pesos a solo **{-1, 0, 1}**:\n\n```\nTradicional: multiplicación + acumulación (costoso)\nBitNet:      solo suma/resta (rápido)\n```\n\n### Beneficios\n- **Memoria**: Reducción de 8-10x en tamaño del modelo\n- **Velocidad**: Las multiplicaciones matriciales se convierten en sumas simples\n- **Energía**: 71.4x menos consumo de energía\n- **Hardware**: No requiere GPU — funciona en cualquier CPU",
      ],
      de: [
        "**BitNet** ist ein revolutionärer Ansatz für große Sprachmodelle mit **1-bit-Quantisierung**.\n\n### Wie es funktioniert\nTraditionelle LLMs verwenden 16-bit oder 32-bit Fließkomma-Gewichte. BitNet beschränkt Gewichte auf nur **{-1, 0, 1}**:\n\n```\nTraditionell: Multiplikation + Akkumulation (teuer)\nBitNet:       nur Addition/Subtraktion (schnell)\n```\n\n### Vorteile\n- **Speicher**: 8-10x Reduzierung der Modellgröße\n- **Geschwindigkeit**: Matrixmultiplikationen werden zu einfachen Additionen\n- **Energie**: 71.4x weniger Energieverbrauch\n- **Hardware**: Keine GPU erforderlich — läuft auf jeder CPU",
      ],
      pt: [
        "**BitNet** é uma abordagem revolucionária para modelos de linguagem grandes usando **quantização de 1-bit**.\n\n### Como funciona\nLLMs tradicionais usam pesos de ponto flutuante de 16-bit ou 32-bit. BitNet restringe os pesos a apenas **{-1, 0, 1}**:\n\n### Benefícios\n- **Memória**: Redução de 8-10x no tamanho do modelo\n- **Velocidade**: Multiplicações de matriz se tornam adições simples\n- **Energia**: 71.4x menos consumo de energia\n- **Hardware**: Não requer GPU — funciona em qualquer CPU",
      ],
      it: [
        "**BitNet** è un approccio rivoluzionario ai grandi modelli linguistici usando **quantizzazione a 1-bit**.\n\n### Come funziona\nI LLM tradizionali usano pesi in virgola mobile a 16-bit o 32-bit. BitNet limita i pesi a solo **{-1, 0, 1}**:\n\n### Benefici\n- **Memoria**: Riduzione di 8-10x della dimensione del modello\n- **Velocità**: Le moltiplicazioni di matrici diventano semplici addizioni\n- **Energia**: 71.4x meno consumo energetico\n- **Hardware**: Nessuna GPU richiesta — funziona su qualsiasi CPU",
      ],
      ja: [
        "**BitNet**は、**1-bit量子化**を使用した大規模言語モデルへの革新的なアプローチです。\n\n### 仕組み\n従来のLLMは16-bitまたは32-bitの浮動小数点重みを使用します。BitNetは重みを**{-1, 0, 1}**のみに制限します：\n\n### メリット\n- **メモリ**: モデルサイズが8-10倍削減\n- **速度**: 行列乗算が単純な加算に\n- **エネルギー**: 71.4倍少ない消費電力\n- **ハードウェア**: GPUは不要 — どのCPUでも動作",
      ],
      ko: [
        "**BitNet**은 **1-bit 양자화**를 사용한 대규모 언어 모델에 대한 혁신적인 접근 방식입니다.\n\n### 작동 방식\n전통적인 LLM은 16-bit 또는 32-bit 부동 소수점 가중치를 사용합니다. BitNet은 가중치를 **{-1, 0, 1}**로만 제한합니다:\n\n### 이점\n- **메모리**: 모델 크기 8-10배 감소\n- **속도**: 행렬 곱셈이 단순 덧셈으로 변환\n- **에너지**: 71.4배 적은 에너지 소비\n- **하드웨어**: GPU 불필요 — 모든 CPU에서 실행",
      ],
      zh: [
        "**BitNet**是使用**1-bit量化**的大型语言模型的革命性方法。\n\n### 工作原理\n传统LLM使用16位或32位浮点权重。BitNet将权重限制为仅**{-1, 0, 1}**：\n\n### 优势\n- **内存**: 模型大小减少8-10倍\n- **速度**: 矩阵乘法变成简单加法\n- **能源**: 能耗降低71.4倍\n- **硬件**: 无需GPU — 在任何CPU上运行",
      ],
      ru: [
        "**BitNet** — это революционный подход к большим языковым моделям с использованием **1-bit квантизации**.\n\n### Как это работает\nТрадиционные LLM используют 16-bit или 32-bit веса с плавающей точкой. BitNet ограничивает веса только **{-1, 0, 1}**:\n\n### Преимущества\n- **Память**: Уменьшение размера модели в 8-10 раз\n- **Скорость**: Матричные умножения становятся простыми сложениями\n- **Энергия**: В 71.4 раза меньше потребление энергии\n- **Оборудование**: GPU не требуется — работает на любом CPU",
      ],
      ar: [
        "**BitNet** هو نهج ثوري لنماذج اللغة الكبيرة باستخدام **التكميم 1-bit**.\n\n### كيف يعمل\nتستخدم نماذج LLM التقليدية أوزان النقطة العائمة 16-bit أو 32-bit. يقيد BitNet الأوزان إلى **{-1, 0, 1}** فقط:\n\n### الفوائد\n- **الذاكرة**: تقليل حجم النموذج 8-10 مرات\n- **السرعة**: تصبح عمليات ضرب المصفوفات إضافات بسيطة\n- **الطاقة**: استهلاك طاقة أقل بـ 71.4 مرة\n- **الأجهزة**: لا يتطلب GPU — يعمل على أي CPU",
      ],
      hi: [
        "**BitNet** **1-bit क्वांटाइजेशन** का उपयोग करते हुए बड़े भाषा मॉडल के लिए एक क्रांतिकारी दृष्टिकोण है।\n\n### यह कैसे काम करता है\nपारंपरिक LLM 16-bit या 32-bit फ्लोटिंग पॉइंट वेट का उपयोग करते हैं। BitNet वेट को केवल **{-1, 0, 1}** तक सीमित करता है:\n\n### लाभ\n- **मेमोरी**: मॉडल आकार में 8-10x की कमी\n- **गति**: मैट्रिक्स गुणन सरल जोड़ बन जाते हैं\n- **ऊर्जा**: 71.4x कम ऊर्जा खपत\n- **हार्डवेयर**: GPU की आवश्यकता नहीं — किसी भी CPU पर चलता है",
      ],
    },
  },
  {
    // Benchmark / Performance
    pattern: /\b(benchmark|performance|speed|fast|token|rendimiento|leistung|desempenho|prestazioni|パフォーマンス|성능|性能|производительность)\b/iu,
    responses: {
      en: [
        "Here are the latest **BitNet benchmark results** on consumer hardware:\n\n### Performance Comparison\n| Model | Params | Tokens/s | RAM | Energy |\n|-------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n| Llama3-8B-1.58 | 8B | **15.03 t/s** | 4.2 GB | 5.8 mJ/tok |\n\n### Key Insights\n- 🔋 **71.4x** more energy efficient than FP16 equivalents\n- 💾 **8-10x** smaller memory footprint\n- ⚡ Runs on **CPU only** — no GPU required\n- 📱 Even the 2.4B model fits on most laptops\n\nAll benchmarks measured on a standard laptop CPU (Intel i7-12th gen, 16GB RAM).",
      ],
      fr: [
        "Voici les derniers **résultats de benchmark BitNet** sur du matériel grand public :\n\n### Comparaison des performances\n| Modèle | Params | Tokens/s | RAM | Énergie |\n|--------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n| Llama3-8B-1.58 | 8B | **15.03 t/s** | 4.2 GB | 5.8 mJ/tok |\n\n### Points clés\n- 🔋 **71.4x** plus économe en énergie que les équivalents FP16\n- 💾 **8-10x** moins d'empreinte mémoire\n- ⚡ Fonctionne **uniquement sur CPU** — pas de GPU requis\n- 📱 Même le modèle 2.4B tient sur la plupart des laptops",
      ],
      es: [
        "Aquí están los últimos **resultados de benchmark de BitNet** en hardware de consumo:\n\n### Comparación de rendimiento\n| Modelo | Params | Tokens/s | RAM | Energía |\n|--------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### Puntos clave\n- 🔋 **71.4x** más eficiente en energía que equivalentes FP16\n- 💾 **8-10x** menor huella de memoria\n- ⚡ Funciona **solo en CPU** — no requiere GPU",
      ],
      de: [
        "Hier sind die neuesten **BitNet-Benchmark-Ergebnisse** auf Consumer-Hardware:\n\n### Leistungsvergleich\n| Modell | Params | Tokens/s | RAM | Energie |\n|--------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### Wichtige Erkenntnisse\n- 🔋 **71.4x** energieeffizienter als FP16-Äquivalente\n- 💾 **8-10x** kleinerer Speicherbedarf\n- ⚡ Läuft **nur auf CPU** — keine GPU erforderlich",
      ],
      pt: [
        "Aqui estão os últimos **resultados de benchmark do BitNet** em hardware de consumo:\n\n### Comparação de desempenho\n| Modelo | Params | Tokens/s | RAM | Energia |\n|--------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### Pontos-chave\n- 🔋 **71.4x** mais eficiente em energia que equivalentes FP16\n- 💾 **8-10x** menor uso de memória\n- ⚡ Funciona **apenas em CPU** — não requer GPU",
      ],
      it: [
        "Ecco gli ultimi **risultati benchmark di BitNet** su hardware consumer:\n\n### Confronto prestazioni\n| Modello | Params | Tokens/s | RAM | Energia |\n|---------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### Punti chiave\n- 🔋 **71.4x** più efficiente energeticamente rispetto a FP16\n- 💾 **8-10x** minore impronta di memoria\n- ⚡ Funziona **solo su CPU** — nessuna GPU richiesta",
      ],
      ja: [
        "消費者向けハードウェアでの最新の**BitNetベンチマーク結果**：\n\n### パフォーマンス比較\n| モデル | パラメータ | トークン/秒 | RAM | エネルギー |\n|--------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### 主なポイント\n- 🔋 FP16と比較して**71.4倍**のエネルギー効率\n- 💾 **8-10倍**小さいメモリフットプリント\n- ⚡ **CPUのみ**で動作 — GPUは不要",
      ],
      ko: [
        "소비자 하드웨어에서의 최신 **BitNet 벤치마크 결과**:\n\n### 성능 비교\n| 모델 | 파라미터 | 토큰/초 | RAM | 에너지 |\n|------|--------|---------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### 핵심 포인트\n- 🔋 FP16 대비 **71.4배** 에너지 효율적\n- 💾 **8-10배** 작은 메모리 사용량\n- ⚡ **CPU만으로** 실행 — GPU 불필요",
      ],
      zh: [
        "以下是消费级硬件上的最新**BitNet基准测试结果**：\n\n### 性能比较\n| 模型 | 参数 | 令牌/秒 | RAM | 能耗 |\n|------|------|---------|-----|------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### 关键要点\n- 🔋 比FP16**节能71.4倍**\n- 💾 内存占用**减少8-10倍**\n- ⚡ **仅需CPU**运行 — 无需GPU",
      ],
      ru: [
        "Вот последние **результаты бенчмарков BitNet** на потребительском оборудовании:\n\n### Сравнение производительности\n| Модель | Параметры | Токенов/с | RAM | Энергия |\n|--------|-----------|-----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### Ключевые выводы\n- 🔋 **В 71.4 раза** энергоэффективнее чем FP16\n- 💾 **В 8-10 раз** меньший объем памяти\n- ⚡ Работает **только на CPU** — GPU не требуется",
      ],
      ar: [
        "فيما يلي أحدث **نتائج اختبارات BitNet** على أجهزة المستهلكين:\n\n### مقارنة الأداء\n| النموذج | المعاملات | رمز/ثانية | RAM | الطاقة |\n|---------|----------|-----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65** | 400 MB | 1.2 mJ |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94** | 1.3 GB | 2.4 mJ |\n\n### النقاط الرئيسية\n- 🔋 كفاءة طاقة أعلى **71.4 مرة** من FP16\n- 💾 **8-10 مرات** أقل في استخدام الذاكرة\n- ⚡ يعمل على **CPU فقط** — لا يتطلب GPU",
      ],
      hi: [
        "उपभोक्ता हार्डवेयर पर नवीनतम **BitNet बेंचमार्क परिणाम**:\n\n### प्रदर्शन तुलना\n| मॉडल | पैरामीटर | टोकन/सेकंड | RAM | ऊर्जा |\n|-------|---------|------------|-----|-------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n\n### मुख्य बिंदु\n- 🔋 FP16 की तुलना में **71.4x** अधिक ऊर्जा कुशल\n- 💾 **8-10x** कम मेमोरी उपयोग\n- ⚡ **केवल CPU** पर चलता है — GPU की आवश्यकता नहीं",
      ],
    },
  },
  {
    // Help / capabilities
    pattern: /\b(help|what can|capable|feature|aide|ayuda|hilfe|ajuda|aiuto|ヘルプ|도움|帮助|помощь|مساعدة|मदद)\b/iu,
    responses: {
      en: [
        "Here's what I can help you with as your **local ARIA assistant**:\n\n### Knowledge Areas\n- **ARIA Protocol**: Architecture, roadmap, and features\n- **BitNet Models**: Performance, benchmarks, and optimization\n- **Decentralized AI**: Concepts, benefits, and comparisons\n- **Technical Topics**: 1-bit quantization, P2P networking, inference\n\n### Capabilities\n- 💬 Natural conversation and Q&A\n- 📊 Performance data and benchmarks\n- 🔧 Technical explanations\n- 💡 Ideas and brainstorming\n\n### Important Notes\n- I run **100% locally** on your device\n- No data is sent to any server\n- Responses are generated by your local BitNet model\n- Speed depends on your hardware configuration",
      ],
      fr: [
        "Voici ce que je peux faire en tant que votre **assistant ARIA local** :\n\n### Domaines de connaissance\n- **Protocole ARIA** : Architecture, feuille de route et fonctionnalités\n- **Modèles BitNet** : Performance, benchmarks et optimisation\n- **IA décentralisée** : Concepts, avantages et comparaisons\n- **Sujets techniques** : Quantification 1-bit, réseau P2P, inférence\n\n### Capacités\n- 💬 Conversation naturelle et Q&R\n- 📊 Données de performance et benchmarks\n- 🔧 Explications techniques\n- 💡 Idées et brainstorming\n\n### Notes importantes\n- Je fonctionne **100% localement** sur votre appareil\n- Aucune donnée n'est envoyée à un serveur\n- La vitesse dépend de la configuration de votre matériel",
      ],
      es: [
        "Esto es lo que puedo ayudarte como tu **asistente ARIA local**:\n\n### Áreas de conocimiento\n- **Protocolo ARIA**: Arquitectura, hoja de ruta y características\n- **Modelos BitNet**: Rendimiento, benchmarks y optimización\n- **IA descentralizada**: Conceptos, beneficios y comparaciones\n\n### Capacidades\n- 💬 Conversación natural y preguntas\n- 📊 Datos de rendimiento y benchmarks\n- 🔧 Explicaciones técnicas\n- 💡 Ideas y lluvia de ideas\n\n### Notas importantes\n- Funciono **100% localmente** en tu dispositivo\n- No se envían datos a ningún servidor",
      ],
      de: [
        "Hier ist, womit ich dir als dein **lokaler ARIA-Assistent** helfen kann:\n\n### Wissensbereiche\n- **ARIA-Protokoll**: Architektur, Roadmap und Funktionen\n- **BitNet-Modelle**: Leistung, Benchmarks und Optimierung\n- **Dezentralisierte KI**: Konzepte, Vorteile und Vergleiche\n\n### Fähigkeiten\n- 💬 Natürliche Konversation und Fragen\n- 📊 Leistungsdaten und Benchmarks\n- 🔧 Technische Erklärungen\n- 💡 Ideen und Brainstorming\n\n### Wichtige Hinweise\n- Ich laufe **100% lokal** auf deinem Gerät\n- Keine Daten werden an Server gesendet",
      ],
      pt: [
        "Aqui está o que posso ajudá-lo como seu **assistente ARIA local**:\n\n### Áreas de conhecimento\n- **Protocolo ARIA**: Arquitetura, roadmap e recursos\n- **Modelos BitNet**: Performance, benchmarks e otimização\n- **IA descentralizada**: Conceitos, benefícios e comparações\n\n### Capacidades\n- 💬 Conversa natural e perguntas\n- 📊 Dados de performance e benchmarks\n- 🔧 Explicações técnicas\n- 💡 Ideias e brainstorming\n\n### Notas importantes\n- Funciono **100% localmente** no seu dispositivo\n- Nenhum dado é enviado para servidores",
      ],
      it: [
        "Ecco come posso aiutarti come tuo **assistente ARIA locale**:\n\n### Aree di conoscenza\n- **Protocollo ARIA**: Architettura, roadmap e funzionalità\n- **Modelli BitNet**: Prestazioni, benchmark e ottimizzazione\n- **IA decentralizzata**: Concetti, vantaggi e confronti\n\n### Capacità\n- 💬 Conversazione naturale e domande\n- 📊 Dati sulle prestazioni e benchmark\n- 🔧 Spiegazioni tecniche\n- 💡 Idee e brainstorming\n\n### Note importanti\n- Funziono **100% localmente** sul tuo dispositivo\n- Nessun dato viene inviato a server",
      ],
      ja: [
        "**ローカルARIAアシスタント**としてお手伝いできること：\n\n### 知識領域\n- **ARIAプロトコル**: アーキテクチャ、ロードマップ、機能\n- **BitNetモデル**: パフォーマンス、ベンチマーク、最適化\n- **分散型AI**: コンセプト、利点、比較\n\n### 機能\n- 💬 自然な会話と質疑応答\n- 📊 パフォーマンスデータとベンチマーク\n- 🔧 技術的な説明\n- 💡 アイデアとブレインストーミング\n\n### 重要な注意\n- あなたのデバイスで**100%ローカル**で実行\n- データはサーバーに送信されません",
      ],
      ko: [
        "**로컬 ARIA 어시스턴트**로서 도움을 드릴 수 있는 분야:\n\n### 지식 영역\n- **ARIA 프로토콜**: 아키텍처, 로드맵 및 기능\n- **BitNet 모델**: 성능, 벤치마크 및 최적화\n- **분산형 AI**: 개념, 이점 및 비교\n\n### 기능\n- 💬 자연스러운 대화 및 질문 답변\n- 📊 성능 데이터 및 벤치마크\n- 🔧 기술적 설명\n- 💡 아이디어 및 브레인스토밍\n\n### 중요 사항\n- 귀하의 기기에서 **100% 로컬**로 실행\n- 서버로 데이터가 전송되지 않음",
      ],
      zh: [
        "作为您的**本地ARIA助手**，我可以帮助您：\n\n### 知识领域\n- **ARIA协议**: 架构、路线图和功能\n- **BitNet模型**: 性能、基准测试和优化\n- **去中心化AI**: 概念、优势和比较\n\n### 功能\n- 💬 自然对话和问答\n- 📊 性能数据和基准测试\n- 🔧 技术解释\n- 💡 创意和头脑风暴\n\n### 重要说明\n- 在您的设备上**100%本地**运行\n- 不会向任何服务器发送数据",
      ],
      ru: [
        "Вот чем я могу помочь как ваш **локальный помощник ARIA**:\n\n### Области знаний\n- **Протокол ARIA**: Архитектура, дорожная карта и функции\n- **Модели BitNet**: Производительность, бенчмарки и оптимизация\n- **Децентрализованный ИИ**: Концепции, преимущества и сравнения\n\n### Возможности\n- 💬 Естественный разговор и вопросы\n- 📊 Данные о производительности и бенчмарки\n- 🔧 Технические объяснения\n- 💡 Идеи и мозговой штурм\n\n### Важные примечания\n- Работаю **100% локально** на вашем устройстве\n- Данные не отправляются на серверы",
      ],
      ar: [
        "إليك ما يمكنني مساعدتك به كـ**مساعد ARIA المحلي** الخاص بك:\n\n### مجالات المعرفة\n- **بروتوكول ARIA**: الهندسة المعمارية وخارطة الطريق والميزات\n- **نماذج BitNet**: الأداء والمعايير والتحسين\n- **الذكاء الاصطناعي اللامركزي**: المفاهيم والفوائد والمقارنات\n\n### القدرات\n- 💬 محادثة طبيعية وأسئلة\n- 📊 بيانات الأداء والمعايير\n- 🔧 شروحات تقنية\n- 💡 أفكار وعصف ذهني\n\n### ملاحظات مهمة\n- أعمل **100% محليًا** على جهازك\n- لا يتم إرسال بيانات إلى أي خادم",
      ],
      hi: [
        "आपके **स्थानीय ARIA सहायक** के रूप में मैं इनमें मदद कर सकता हूँ:\n\n### ज्ञान क्षेत्र\n- **ARIA प्रोटोकॉल**: आर्किटेक्चर, रोडमैप और सुविधाएं\n- **BitNet मॉडल**: प्रदर्शन, बेंचमार्क और अनुकूलन\n- **विकेंद्रीकृत AI**: अवधारणाएं, लाभ और तुलना\n\n### क्षमताएं\n- 💬 प्राकृतिक बातचीत और प्रश्न-उत्तर\n- 📊 प्रदर्शन डेटा और बेंचमार्क\n- 🔧 तकनीकी स्पष्टीकरण\n- 💡 विचार और मंथन\n\n### महत्वपूर्ण नोट\n- आपके डिवाइस पर **100% स्थानीय** रूप से चलता है\n- कोई डेटा सर्वर को नहीं भेजा जाता",
      ],
    },
  },
];

// Default responses when no pattern matches
const defaultResponses: Record<SupportedLanguage, string[]> = {
  en: [
    "That's an interesting question! As a local AI running on ARIA Protocol with BitNet inference, I can share some thoughts.\n\nDecentralized AI is fundamentally about giving individuals control over their AI interactions. Unlike centralized services, everything here runs on your hardware — your data never leaves your device.\n\nWould you like to know more about how ARIA achieves this, or do you have a specific topic in mind?",
    "Great question! Let me think about that from the perspective of decentralized AI.\n\nOne of the key advantages of running models locally through ARIA is that we can have these conversations with **complete privacy**. No logs, no tracking, no data collection.\n\nThe BitNet model powering this conversation uses only ~1.3 GB of RAM and runs entirely on your CPU. That's the power of 1-bit quantization.\n\nIs there anything specific about ARIA or local AI you'd like to explore?",
    "I appreciate the question! Here's my take on it.\n\nThe shift toward **local AI inference** is one of the most significant trends in the AI space. Projects like ARIA Protocol are proving that you don't need massive data centers to run capable language models.\n\nWith BitNet's 1-bit architecture:\n- Models are **8-10x smaller** than traditional ones\n- Inference is **71x more energy efficient**\n- Everything runs on **consumer hardware**\n\nWhat else would you like to discuss?",
  ],
  fr: [
    "Excellente question ! En tant qu'IA locale fonctionnant sur le protocole ARIA avec l'inférence BitNet, voici mon point de vue.\n\nL'IA décentralisée consiste fondamentalement à donner aux individus le contrôle de leurs interactions avec l'IA. Contrairement aux services centralisés, tout fonctionne ici sur votre matériel — vos données ne quittent jamais votre appareil.\n\nVoulez-vous en savoir plus sur la façon dont ARIA réalise cela, ou avez-vous un sujet spécifique en tête ?",
    "Bonne question ! Laissez-moi y réfléchir du point de vue de l'IA décentralisée.\n\nL'un des principaux avantages de l'exécution de modèles localement via ARIA est que nous pouvons avoir ces conversations en **toute confidentialité**. Pas de journaux, pas de suivi, pas de collecte de données.\n\nLe modèle BitNet qui alimente cette conversation n'utilise que ~1.3 Go de RAM et fonctionne entièrement sur votre CPU. C'est la puissance de la quantification 1-bit.\n\nY a-t-il quelque chose de spécifique sur ARIA ou l'IA locale que vous aimeriez explorer ?",
    "J'apprécie la question ! Voici mon avis.\n\nLe passage vers **l'inférence IA locale** est l'une des tendances les plus significatives dans l'espace IA. Des projets comme le protocole ARIA prouvent qu'il n'est pas nécessaire d'avoir des centres de données massifs pour exécuter des modèles de langage performants.\n\nAvec l'architecture 1-bit de BitNet :\n- Les modèles sont **8-10x plus petits** que les modèles traditionnels\n- L'inférence est **71x plus économe en énergie**\n- Tout fonctionne sur du **matériel grand public**\n\nDe quoi d'autre aimeriez-vous discuter ?",
  ],
  es: [
    "¡Excelente pregunta! Como IA local funcionando en el Protocolo ARIA con inferencia BitNet, puedo compartir algunas ideas.\n\nLa IA descentralizada se trata fundamentalmente de dar a los individuos control sobre sus interacciones con la IA. A diferencia de los servicios centralizados, todo aquí funciona en tu hardware — tus datos nunca salen de tu dispositivo.\n\n¿Te gustaría saber más sobre cómo ARIA logra esto, o tienes algún tema específico en mente?",
    "¡Buena pregunta! Déjame pensarlo desde la perspectiva de la IA descentralizada.\n\nUna de las principales ventajas de ejecutar modelos localmente a través de ARIA es que podemos tener estas conversaciones con **completa privacidad**. Sin registros, sin seguimiento, sin recopilación de datos.\n\nEl modelo BitNet que impulsa esta conversación usa solo ~1.3 GB de RAM y funciona completamente en tu CPU.\n\n¿Hay algo específico sobre ARIA o la IA local que te gustaría explorar?",
  ],
  de: [
    "Interessante Frage! Als lokale KI, die auf dem ARIA-Protokoll mit BitNet-Inferenz läuft, kann ich einige Gedanken teilen.\n\nDezentralisierte KI geht grundlegend darum, Einzelpersonen die Kontrolle über ihre KI-Interaktionen zu geben. Anders als bei zentralisierten Diensten läuft hier alles auf deiner Hardware — deine Daten verlassen nie dein Gerät.\n\nMöchtest du mehr darüber erfahren, wie ARIA das erreicht, oder hast du ein bestimmtes Thema im Sinn?",
    "Gute Frage! Lass mich das aus der Perspektive dezentralisierter KI betrachten.\n\nEiner der Hauptvorteile des lokalen Ausführens von Modellen über ARIA ist, dass wir diese Gespräche mit **vollständiger Privatsphäre** führen können. Keine Logs, kein Tracking, keine Datensammlung.\n\nDas BitNet-Modell, das dieses Gespräch antreibt, verwendet nur ~1.3 GB RAM und läuft vollständig auf deiner CPU.\n\nGibt es etwas Bestimmtes über ARIA oder lokale KI, das du erkunden möchtest?",
  ],
  pt: [
    "Excelente pergunta! Como uma IA local rodando no Protocolo ARIA com inferência BitNet, posso compartilhar algumas reflexões.\n\nA IA descentralizada é fundamentalmente sobre dar aos indivíduos controle sobre suas interações com IA. Diferente de serviços centralizados, tudo aqui roda no seu hardware — seus dados nunca saem do seu dispositivo.\n\nGostaria de saber mais sobre como o ARIA consegue isso, ou tem algum tópico específico em mente?",
    "Boa pergunta! Deixe-me pensar nisso da perspectiva da IA descentralizada.\n\nUma das principais vantagens de rodar modelos localmente através do ARIA é que podemos ter essas conversas com **total privacidade**. Sem logs, sem rastreamento, sem coleta de dados.\n\nO modelo BitNet que alimenta esta conversa usa apenas ~1.3 GB de RAM e roda inteiramente na sua CPU.\n\nHá algo específico sobre ARIA ou IA local que você gostaria de explorar?",
  ],
  it: [
    "Ottima domanda! Come IA locale che funziona sul Protocollo ARIA con inferenza BitNet, posso condividere alcuni pensieri.\n\nL'IA decentralizzata riguarda fondamentalmente il dare agli individui il controllo sulle loro interazioni con l'IA. A differenza dei servizi centralizzati, tutto qui funziona sul tuo hardware — i tuoi dati non lasciano mai il tuo dispositivo.\n\nVorresti saperne di più su come ARIA raggiunge questo, o hai un argomento specifico in mente?",
    "Buona domanda! Lasciami riflettere dal punto di vista dell'IA decentralizzata.\n\nUno dei principali vantaggi dell'esecuzione di modelli localmente tramite ARIA è che possiamo avere queste conversazioni con **completa privacy**. Nessun log, nessun tracciamento, nessuna raccolta dati.\n\nIl modello BitNet che alimenta questa conversazione usa solo ~1.3 GB di RAM e funziona interamente sulla tua CPU.\n\nC'è qualcosa di specifico su ARIA o sull'IA locale che vorresti esplorare?",
  ],
  ja: [
    "興味深い質問ですね！BitNet推論を使用してARIAプロトコル上で動作するローカルAIとして、いくつかの考えを共有できます。\n\n分散型AIは基本的に、個人がAIとのインタラクションをコントロールできるようにすることです。中央集権型サービスとは異なり、ここではすべてがあなたのハードウェア上で動作します — データはデバイスを離れることはありません。\n\nARIAがこれをどのように実現しているかについてもっと知りたいですか、それとも特定のトピックがありますか？",
    "良い質問です！分散型AIの観点から考えてみましょう。\n\nARIAを通じてローカルでモデルを実行する主な利点の1つは、**完全なプライバシー**でこれらの会話ができることです。ログなし、トラッキングなし、データ収集なし。\n\nこの会話を動かしているBitNetモデルは約1.3 GBのRAMしか使用せず、完全にCPU上で動作します。\n\nARIAやローカルAIについて探求したい特定のことはありますか？",
  ],
  ko: [
    "흥미로운 질문입니다! BitNet 추론으로 ARIA 프로토콜에서 실행되는 로컬 AI로서 몇 가지 생각을 공유할 수 있습니다.\n\n분산형 AI는 근본적으로 개인이 AI 상호작용을 제어할 수 있게 하는 것입니다. 중앙 집중식 서비스와 달리, 여기서는 모든 것이 귀하의 하드웨어에서 실행됩니다 — 데이터는 절대 기기를 떠나지 않습니다.\n\nARIA가 이를 어떻게 달성하는지 더 알고 싶으신가요, 아니면 특정 주제가 있으신가요?",
    "좋은 질문입니다! 분산형 AI의 관점에서 생각해 보겠습니다.\n\nARIA를 통해 로컬에서 모델을 실행하는 주요 이점 중 하나는 **완전한 프라이버시**로 이러한 대화를 할 수 있다는 것입니다. 로그 없음, 추적 없음, 데이터 수집 없음.\n\n이 대화를 구동하는 BitNet 모델은 약 1.3GB RAM만 사용하고 완전히 CPU에서 실행됩니다.\n\nARIA나 로컬 AI에 대해 탐구하고 싶은 특정 사항이 있으신가요?",
  ],
  zh: [
    "这是个有趣的问题！作为使用BitNet推理在ARIA协议上运行的本地AI，我可以分享一些想法。\n\n去中心化AI的核心是让个人控制他们与AI的交互。与中心化服务不同，这里的一切都在您的硬件上运行——您的数据永远不会离开您的设备。\n\n您想了解更多关于ARIA如何实现这一点的信息，还是有特定的话题想讨论？",
    "好问题！让我从去中心化AI的角度来思考。\n\n通过ARIA本地运行模型的主要优势之一是，我们可以在**完全隐私**的情况下进行这些对话。没有日志，没有跟踪，没有数据收集。\n\n驱动这次对话的BitNet模型只使用约1.3 GB RAM，完全在您的CPU上运行。\n\n有什么关于ARIA或本地AI的特定内容您想探索吗？",
  ],
  ru: [
    "Интересный вопрос! Как локальный ИИ, работающий на протоколе ARIA с инференсом BitNet, могу поделиться некоторыми мыслями.\n\nДецентрализованный ИИ — это фундаментально о том, чтобы дать людям контроль над их взаимодействием с ИИ. В отличие от централизованных сервисов, здесь всё работает на вашем оборудовании — ваши данные никогда не покидают ваше устройство.\n\nХотите узнать больше о том, как ARIA достигает этого, или у вас есть конкретная тема?",
    "Хороший вопрос! Позвольте мне подумать об этом с точки зрения децентрализованного ИИ.\n\nОдно из ключевых преимуществ локального запуска моделей через ARIA — мы можем вести эти разговоры с **полной конфиденциальностью**. Никаких логов, никакого отслеживания, никакого сбора данных.\n\nМодель BitNet, обеспечивающая этот разговор, использует всего ~1.3 ГБ ОЗУ и работает полностью на вашем CPU.\n\nЕсть что-то конкретное об ARIA или локальном ИИ, что вы хотели бы изучить?",
  ],
  ar: [
    "سؤال مثير للاهتمام! كذكاء اصطناعي محلي يعمل على بروتوكول ARIA مع استدلال BitNet، يمكنني مشاركة بعض الأفكار.\n\nالذكاء الاصطناعي اللامركزي يتعلق أساسًا بمنح الأفراد السيطرة على تفاعلاتهم مع الذكاء الاصطناعي. على عكس الخدمات المركزية، كل شيء هنا يعمل على أجهزتك — بياناتك لا تغادر جهازك أبدًا.\n\nهل تريد معرفة المزيد عن كيفية تحقيق ARIA لهذا، أم لديك موضوع محدد في ذهنك؟",
  ],
  hi: [
    "दिलचस्प सवाल! BitNet अनुमान के साथ ARIA प्रोटोकॉल पर चलने वाले स्थानीय AI के रूप में, मैं कुछ विचार साझा कर सकता हूँ।\n\nविकेंद्रीकृत AI मूल रूप से व्यक्तियों को उनके AI इंटरैक्शन पर नियंत्रण देने के बारे में है। केंद्रीकृत सेवाओं के विपरीत, यहाँ सब कुछ आपके हार्डवेयर पर चलता है — आपका डेटा कभी भी आपके डिवाइस को नहीं छोड़ता।\n\nक्या आप जानना चाहेंगे कि ARIA यह कैसे प्राप्त करता है, या आपके मन में कोई विशिष्ट विषय है?",
  ],
};

export function getMockResponse(prompt: string): string {
  const lang = detectLanguage(prompt);
  const lowerPrompt = prompt.toLowerCase();

  for (const mock of mockResponses) {
    if (mock.pattern.test(lowerPrompt)) {
      const langResponses = mock.responses[lang] || mock.responses["en"];
      const idx = Math.floor(Math.random() * langResponses.length);
      return langResponses[idx];
    }
  }

  const langDefaults = defaultResponses[lang] || defaultResponses["en"];
  const idx = Math.floor(Math.random() * langDefaults.length);
  return langDefaults[idx];
}

export function generateTitle(firstMessage: string): string {
  const cleaned = firstMessage.trim().slice(0, 60);

  if (
    /\b(hello|hi|hey|bonjour|salut|hola|hallo|olá|ciao|こんにちは|안녕|你好|привет|مرحبا|नमस्ते)\b/iu.test(
      cleaned
    )
  ) {
    return "New conversation";
  }

  const sentence = cleaned.split(/[.!?]/)[0].trim();
  if (sentence.length > 40) {
    return sentence.slice(0, 40) + "...";
  }
  return sentence || "New conversation";
}
