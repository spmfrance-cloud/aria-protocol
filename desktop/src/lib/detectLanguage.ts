/**
 * Simple language detection utility based on patterns and Unicode ranges.
 * No external dependencies - designed for local, lightweight detection.
 */

export type SupportedLanguage =
  | "en"
  | "fr"
  | "es"
  | "de"
  | "pt"
  | "it"
  | "ja"
  | "ko"
  | "zh"
  | "ru"
  | "ar"
  | "hi";

// Unicode range detection for non-Latin scripts
const scriptPatterns: Array<{
  lang: SupportedLanguage;
  pattern: RegExp;
  priority: number;
}> = [
  // Japanese: Hiragana, Katakana, and some CJK with Japanese particles
  {
    lang: "ja",
    pattern: /[\u3040-\u309F\u30A0-\u30FF]|[\u4E00-\u9FFF].*[はがのをにでもへとや]/u,
    priority: 100,
  },
  // Korean: Hangul syllables and Jamo
  {
    lang: "ko",
    pattern: /[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]/u,
    priority: 100,
  },
  // Chinese: CJK characters (when no Japanese indicators)
  { lang: "zh", pattern: /[\u4E00-\u9FFF]{2,}/u, priority: 90 },
  // Russian/Cyrillic
  { lang: "ru", pattern: /[\u0400-\u04FF]/u, priority: 100 },
  // Arabic
  { lang: "ar", pattern: /[\u0600-\u06FF\u0750-\u077F]/u, priority: 100 },
  // Hindi/Devanagari
  { lang: "hi", pattern: /[\u0900-\u097F]/u, priority: 100 },
];

// Common words/patterns for Latin-script languages
const latinKeywords: Record<SupportedLanguage, string[]> = {
  fr: [
    // Articles and determiners
    "le",
    "la",
    "les",
    "un",
    "une",
    "des",
    "du",
    "au",
    "aux",
    // Pronouns
    "je",
    "tu",
    "il",
    "elle",
    "nous",
    "vous",
    "ils",
    "elles",
    "ce",
    "cette",
    // Common verbs
    "est",
    "sont",
    "suis",
    "avez",
    "avoir",
    "faire",
    "peut",
    "peux",
    // Prepositions and conjunctions
    "pour",
    "avec",
    "dans",
    "sur",
    "par",
    "mais",
    "donc",
    "que",
    "qui",
    // Question words
    "comment",
    "pourquoi",
    "quoi",
    "quel",
    "quelle",
    "quand",
    // Common words
    "bonjour",
    "salut",
    "merci",
    "oui",
    "non",
    "bien",
    "très",
    "plus",
    "aussi",
    "ça",
    "cela",
    "ceci",
  ],
  es: [
    // Articles and determiners
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "unos",
    "unas",
    // Pronouns
    "yo",
    "tú",
    "él",
    "ella",
    "nosotros",
    "ustedes",
    "ellos",
    // Common verbs
    "es",
    "son",
    "está",
    "están",
    "tengo",
    "tiene",
    "puede",
    "hacer",
    // Prepositions and conjunctions
    "para",
    "con",
    "por",
    "pero",
    "como",
    "sobre",
    "entre",
    // Question words
    "qué",
    "cómo",
    "cuál",
    "cuándo",
    "dónde",
    "por qué",
    // Common words
    "hola",
    "gracias",
    "sí",
    "muy",
    "bien",
    "más",
    "también",
    "ahora",
  ],
  de: [
    // Articles and determiners
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "einer",
    "eines",
    "einem",
    "einen",
    // Pronouns
    "ich",
    "du",
    "er",
    "sie",
    "wir",
    "ihr",
    // Common verbs
    "ist",
    "sind",
    "bin",
    "habe",
    "hat",
    "haben",
    "kann",
    "werden",
    // Prepositions and conjunctions
    "für",
    "mit",
    "auf",
    "und",
    "oder",
    "aber",
    "weil",
    "wenn",
    "dass",
    // Question words
    "was",
    "wie",
    "warum",
    "wann",
    "wo",
    "wer",
    // Common words
    "hallo",
    "danke",
    "ja",
    "nein",
    "gut",
    "sehr",
    "auch",
    "noch",
    "schon",
  ],
  pt: [
    // Articles and determiners
    "o",
    "a",
    "os",
    "as",
    "um",
    "uma",
    "uns",
    "umas",
    // Pronouns
    "eu",
    "tu",
    "ele",
    "ela",
    "nós",
    "vocês",
    "eles",
    "elas",
    // Common verbs
    "é",
    "são",
    "está",
    "estão",
    "tenho",
    "tem",
    "pode",
    "fazer",
    // Prepositions and conjunctions
    "para",
    "com",
    "por",
    "mas",
    "como",
    "sobre",
    "entre",
    // Question words
    "como",
    "quando",
    "onde",
    "por que",
    "qual",
    // Common words
    "olá",
    "obrigado",
    "obrigada",
    "sim",
    "não",
    "muito",
    "bem",
    "mais",
    "também",
  ],
  it: [
    // Articles and determiners
    "il",
    "lo",
    "la",
    "i",
    "gli",
    "le",
    "un",
    "una",
    "uno",
    // Pronouns
    "io",
    "tu",
    "lui",
    "lei",
    "noi",
    "voi",
    "loro",
    // Common verbs
    "è",
    "sono",
    "ho",
    "hai",
    "ha",
    "hanno",
    "può",
    "fare",
    // Prepositions and conjunctions
    "per",
    "con",
    "ma",
    "che",
    "come",
    "su",
    "tra",
    // Question words
    "come",
    "perché",
    "quando",
    "dove",
    "quale",
    "chi",
    // Common words
    "ciao",
    "grazie",
    "sì",
    "molto",
    "bene",
    "più",
    "anche",
    "ancora",
  ],
  en: [
    // Articles and determiners
    "the",
    "a",
    "an",
    // Pronouns
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    // Common verbs
    "is",
    "are",
    "am",
    "was",
    "were",
    "have",
    "has",
    "had",
    "can",
    "could",
    "would",
    "should",
    // Prepositions and conjunctions
    "in",
    "on",
    "at",
    "to",
    "for",
    "with",
    "and",
    "but",
    "or",
    // Question words
    "what",
    "how",
    "why",
    "when",
    "where",
    "who",
    // Common words
    "hello",
    "hi",
    "hey",
    "thanks",
    "thank",
    "yes",
    "no",
    "please",
    "very",
    "just",
    "also",
  ],
  // These are detected by Unicode patterns, but we include some common words as fallback
  ja: ["です", "ます", "ありがとう", "こんにちは", "はい", "いいえ"],
  ko: ["안녕", "감사", "네", "아니요", "입니다", "합니다"],
  zh: ["你好", "谢谢", "是", "不", "的", "了", "吗"],
  ru: ["привет", "спасибо", "да", "нет", "это", "как", "что", "почему"],
  ar: ["مرحبا", "شكرا", "نعم", "لا", "هل", "ما", "كيف", "لماذا"],
  hi: ["नमस्ते", "धन्यवाद", "हाँ", "नहीं", "क्या", "कैसे", "क्यों"],
};

/**
 * Detects the language of the given text.
 * Uses Unicode range detection for non-Latin scripts first,
 * then keyword matching for Latin-script languages.
 *
 * @param text - The text to analyze
 * @returns The detected language code
 */
export function detectLanguage(text: string): SupportedLanguage {
  if (!text || text.trim().length === 0) {
    return "en";
  }

  const normalizedText = text.toLowerCase().trim();

  // Step 1: Check for non-Latin scripts using Unicode patterns
  // This is the most reliable detection method
  for (const { lang, pattern } of scriptPatterns) {
    if (pattern.test(normalizedText)) {
      // For Chinese vs Japanese disambiguation
      if (lang === "zh") {
        // If we find Japanese-specific characters, it's Japanese
        const hasHiragana = /[\u3040-\u309F]/.test(normalizedText);
        const hasKatakana = /[\u30A0-\u30FF]/.test(normalizedText);
        if (hasHiragana || hasKatakana) {
          continue; // Skip Chinese, let Japanese pattern match
        }
      }
      return lang;
    }
  }

  // Step 2: Score Latin-script languages by keyword matching
  const scores: Partial<Record<SupportedLanguage, number>> = {};
  const words = normalizedText
    .split(/[\s,.!?;:'"()[\]{}]+/)
    .filter((w) => w.length > 0);

  // Latin languages to check (prioritize non-English first)
  const latinLangs: SupportedLanguage[] = ["fr", "es", "de", "pt", "it", "en"];

  for (const lang of latinLangs) {
    scores[lang] = 0;
    const keywords = latinKeywords[lang];

    for (const word of words) {
      if (keywords.includes(word)) {
        // Weight by word specificity (longer words are more distinctive)
        scores[lang]! += word.length > 3 ? 2 : 1;
      }
    }
  }

  // Find the language with the highest score
  let bestLang: SupportedLanguage = "en";
  let bestScore = 0;

  for (const [lang, score] of Object.entries(scores)) {
    if (score !== undefined && score > bestScore) {
      bestScore = score;
      bestLang = lang as SupportedLanguage;
    }
  }

  // Only return non-English if we have reasonable confidence
  // (at least 2 matching keywords, or 1 distinctive keyword)
  if (bestLang !== "en" && bestScore >= 2) {
    return bestLang;
  }

  // If English also has a score, check if it's competitive
  if (scores["en"] && scores["en"] >= 2) {
    return "en";
  }

  // Default fallback
  return "en";
}
