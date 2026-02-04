interface MockResponse {
  pattern: RegExp;
  responses: string[];
}

const mockResponses: MockResponse[] = [
  {
    pattern: /\b(hello|hi|hey|bonjour|salut)\b/i,
    responses: [
      "Hello! I'm your local ARIA assistant, running entirely on your machine with BitNet inference. How can I help you today?\n\nI can assist with:\n- **Understanding ARIA Protocol** and decentralized AI\n- **Model performance** benchmarks and optimization\n- **Technical questions** about 1-bit LLMs\n- **General conversation** and brainstorming",
      "Hey there! Welcome to ARIA's local AI assistant. I'm powered by BitNet and running 100% offline on your hardware — no data leaves your device.\n\nWhat would you like to explore today?",
      "Hi! I'm ARIA's on-device assistant. Everything runs locally with **zero cloud dependency**. Ask me anything about decentralized AI, BitNet models, or just chat freely!",
    ],
  },
  {
    pattern: /\b(aria|protocol|decentralized)\b/i,
    responses: [
      "**ARIA Protocol** is a decentralized AI inference network that enables anyone to run and share AI models locally.\n\n### Core Principles\n- **Decentralization**: No single point of failure or control\n- **Privacy**: All inference happens on-device by default\n- **Efficiency**: Built on 1-bit LLMs (BitNet) for minimal resource usage\n- **Accessibility**: Runs on consumer hardware — no GPU required\n\n### Architecture\n```\nUser Request → Local Node → BitNet Inference → Response\n                  ↕\n           ARIA P2P Network\n                  ↕\n            Other Nodes (optional)\n```\n\nThe protocol coordinates distributed inference across a peer-to-peer network while keeping data sovereignty with each node operator.",
      "ARIA Protocol is pioneering **decentralized AI** by leveraging 1-bit quantized models (BitNet) that run efficiently on CPUs.\n\n### Key Features\n- **Local-first**: Models run on your hardware\n- **P2P Network**: Nodes collaborate for larger workloads\n- **Energy efficient**: Up to 71x less energy than FP16 models\n- **Open source**: Fully transparent and community-driven\n\nThe goal is to democratize AI by removing the dependency on centralized cloud providers and expensive GPU infrastructure.",
    ],
  },
  {
    pattern: /\b(benchmark|performance|speed|fast|token)\b/i,
    responses: [
      "Here are the latest **BitNet benchmark results** on consumer hardware:\n\n### Performance Comparison\n| Model | Params | Tokens/s | RAM | Energy |\n|-------|--------|----------|-----|--------|\n| BitNet-b1.58-large | 0.7B | **89.65 t/s** | 400 MB | 1.2 mJ/tok |\n| BitNet-b1.58-2B-4T | 2.4B | **36.94 t/s** | 1.3 GB | 2.4 mJ/tok |\n| Llama3-8B-1.58 | 8B | **15.03 t/s** | 4.2 GB | 5.8 mJ/tok |\n\n### Key Insights\n- 🔋 **71.4x** more energy efficient than FP16 equivalents\n- 💾 **8-10x** smaller memory footprint\n- ⚡ Runs on **CPU only** — no GPU required\n- 📱 Even the 2.4B model fits on most laptops\n\nAll benchmarks measured on a standard laptop CPU (Intel i7-12th gen, 16GB RAM).",
      "**Performance benchmarks** for BitNet models in ARIA:\n\n### BitNet-b1.58-2B-4T (Recommended)\n- **Throughput**: 36.94 tokens/second\n- **Time to first token**: 120ms\n- **Memory usage**: 1.3 GB RAM\n- **Energy**: 2.4 mJ per token\n\nCompared to traditional FP16 models:\n- **71x** less energy per token\n- **8x** less memory required\n- **No GPU** needed — pure CPU inference\n\nThe 1-bit quantization in BitNet replaces multiply operations with simple additions, making inference dramatically faster and more efficient on standard hardware.",
    ],
  },
  {
    pattern: /\b(bitnet|1-bit|quantiz|model)\b/i,
    responses: [
      "**BitNet** is a revolutionary approach to large language models using **1-bit quantization**.\n\n### How It Works\nTraditional LLMs use 16-bit or 32-bit floating point weights. BitNet constrains weights to just **{-1, 0, 1}**, which means:\n\n```\nTraditional: multiply + accumulate (expensive)\nBitNet:      add/subtract only (cheap & fast)\n```\n\n### Benefits\n- **Memory**: 8-10x reduction in model size\n- **Speed**: Matrix multiplications become simple additions\n- **Energy**: 71.4x less energy consumption\n- **Hardware**: No GPU required — runs on any CPU\n\n### Available Models in ARIA\n1. **BitNet-b1.58-large** (0.7B) — Fast, lightweight\n2. **BitNet-b1.58-2B-4T** (2.4B) — Best balance ⭐\n3. **Llama3-8B-1.58** (8B) — Most capable",
      "**1-bit LLMs (BitNet)** represent a paradigm shift in AI inference.\n\nInstead of storing weights as 16-bit floats (`-0.3421, 1.2845, ...`), BitNet uses ternary values: **-1, 0, or 1**.\n\nThis seemingly simple change has massive implications:\n- Multiplications become additions → **faster inference**\n- Each weight needs ~1.58 bits → **smaller models**\n- Simpler operations → **lower energy consumption**\n\nResearch from Microsoft shows BitNet-b1.58 matches full-precision models in quality while being dramatically more efficient. ARIA Protocol builds on this to make AI accessible to everyone.",
    ],
  },
  {
    pattern: /\b(energy|green|sustainable|carbon|environment)\b/i,
    responses: [
      "Energy efficiency is a **core pillar** of ARIA Protocol.\n\n### The Problem\nTraditional AI inference is energy-intensive:\n- A single ChatGPT query uses ~10x more energy than a Google search\n- Training GPT-4 consumed an estimated 50 GWh\n- Data centers account for 1-2% of global electricity\n\n### ARIA's Solution\nBy using **BitNet 1-bit models**:\n- **71.4x** less energy per token vs FP16\n- **CPU-only** inference — no power-hungry GPUs\n- **Distributed** workload across efficient nodes\n\n### Real Numbers\n| Metric | Traditional | ARIA (BitNet) |\n|--------|------------|---------------|\n| Energy/token | 170 mJ | 2.4 mJ |\n| Hardware | A100 GPU | Laptop CPU |\n| Cost/1M tokens | ~$0.06 | ~$0.001 |\n\nDecentralized AI doesn't just protect privacy — it's better for the planet.",
    ],
  },
  {
    pattern: /\b(help|what can|capable|feature)\b/i,
    responses: [
      "Here's what I can help you with as your **local ARIA assistant**:\n\n### Knowledge Areas\n- **ARIA Protocol**: Architecture, roadmap, and features\n- **BitNet Models**: Performance, benchmarks, and optimization\n- **Decentralized AI**: Concepts, benefits, and comparisons\n- **Technical Topics**: 1-bit quantization, P2P networking, inference\n\n### Capabilities\n- 💬 Natural conversation and Q&A\n- 📊 Performance data and benchmarks\n- 🔧 Technical explanations\n- 💡 Ideas and brainstorming\n\n### Important Notes\n- I run **100% locally** on your device\n- No data is sent to any server\n- Responses are generated by your local BitNet model\n- Speed depends on your hardware configuration",
    ],
  },
];

const defaultResponses = [
  "That's an interesting question! As a local AI running on ARIA Protocol with BitNet inference, I can share some thoughts.\n\nDecentralized AI is fundamentally about giving individuals control over their AI interactions. Unlike centralized services, everything here runs on your hardware — your data never leaves your device.\n\nWould you like to know more about how ARIA achieves this, or do you have a specific topic in mind?",
  "Great question! Let me think about that from the perspective of decentralized AI.\n\nOne of the key advantages of running models locally through ARIA is that we can have these conversations with **complete privacy**. No logs, no tracking, no data collection.\n\nThe BitNet model powering this conversation uses only ~1.3 GB of RAM and runs entirely on your CPU. That's the power of 1-bit quantization.\n\nIs there anything specific about ARIA or local AI you'd like to explore?",
  "I appreciate the question! Here's my take on it.\n\nThe shift toward **local AI inference** is one of the most significant trends in the AI space. Projects like ARIA Protocol are proving that you don't need massive data centers to run capable language models.\n\nWith BitNet's 1-bit architecture:\n- Models are **8-10x smaller** than traditional ones\n- Inference is **71x more energy efficient**\n- Everything runs on **consumer hardware**\n\nWhat else would you like to discuss?",
  "Interesting topic! Let me share some thoughts.\n\nThe ARIA ecosystem is designed around three core principles:\n1. **Privacy**: Your conversations stay on your device\n2. **Efficiency**: BitNet models maximize performance per watt\n3. **Decentralization**: No single entity controls the network\n\nThis approach makes AI more accessible and democratic. Instead of relying on cloud APIs with usage limits and privacy concerns, you run everything locally.\n\nFeel free to ask about any specific aspect — I'm here to help!",
];

export function getMockResponse(prompt: string): string {
  const lowerPrompt = prompt.toLowerCase();

  for (const mock of mockResponses) {
    if (mock.pattern.test(lowerPrompt)) {
      const idx = Math.floor(Math.random() * mock.responses.length);
      return mock.responses[idx];
    }
  }

  const idx = Math.floor(Math.random() * defaultResponses.length);
  return defaultResponses[idx];
}

export function generateTitle(firstMessage: string): string {
  const cleaned = firstMessage.trim().slice(0, 60);

  if (/\b(hello|hi|hey|bonjour|salut)\b/i.test(cleaned)) {
    return "New conversation";
  }

  // Use the first sentence or first N words
  const sentence = cleaned.split(/[.!?]/)[0].trim();
  if (sentence.length > 40) {
    return sentence.slice(0, 40) + "...";
  }
  return sentence || "New conversation";
}
