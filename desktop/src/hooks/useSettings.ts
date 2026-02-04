import { useState, useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";

export interface Settings {
  theme: "dark" | "light" | "system";
  language: string;
  backend: "auto" | "native" | "simulation";
  defaultModel: string;
  maxCpuUsage: number;
  port: number;
  enableP2P: boolean;
  maxPeers: number;
  bandwidthLimit: number;
  autoStart: boolean;
  startMinimized: boolean;
  checkUpdates: boolean;
  telemetry: boolean;
  dataRetention: number;
}

const STORAGE_KEY = "aria-settings";

const defaultSettings: Settings = {
  theme: "dark",
  language: "en",
  backend: "auto",
  defaultModel: "BitNet-b1.58-2B-4T",
  maxCpuUsage: 50,
  port: 8765,
  enableP2P: true,
  maxPeers: 10,
  bandwidthLimit: 0,
  autoStart: false,
  startMinimized: false,
  checkUpdates: true,
  telemetry: false,
  dataRetention: 30,
};

function loadSettings(): Settings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return { ...defaultSettings, ...JSON.parse(stored) };
    }
  } catch {
    // ignore parse errors
  }
  return { ...defaultSettings };
}

function saveSettings(settings: Settings) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch {
    // ignore storage errors
  }
}

export function useSettings() {
  const { i18n } = useTranslation();
  const [settings, setSettingsState] = useState<Settings>(() => {
    const loaded = loadSettings();
    // Sync language from i18n detected language on first load
    const detectedLang = i18n.language?.split("-")[0] || "en";
    if (!localStorage.getItem(STORAGE_KEY)) {
      loaded.language = detectedLang;
    }
    return loaded;
  });

  // Apply RTL for Arabic
  useEffect(() => {
    document.documentElement.dir = settings.language === "ar" ? "rtl" : "ltr";
  }, [settings.language]);

  const setSetting = useCallback(
    <K extends keyof Settings>(key: K, value: Settings[K]) => {
      setSettingsState((prev) => {
        const next = { ...prev, [key]: value };
        saveSettings(next);

        if (key === "language") {
          i18n.changeLanguage(value as string);
          localStorage.setItem("aria-language", value as string);
        }

        return next;
      });
    },
    [i18n]
  );

  const getSetting = useCallback(
    <K extends keyof Settings>(key: K): Settings[K] => {
      return settings[key];
    },
    [settings]
  );

  const resetSettings = useCallback(() => {
    const reset = { ...defaultSettings };
    saveSettings(reset);
    setSettingsState(reset);
    i18n.changeLanguage(reset.language);
    localStorage.setItem("aria-language", reset.language);
  }, [i18n]);

  return {
    settings,
    getSetting,
    setSetting,
    resetSettings,
  };
}
