import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import {
  Settings2,
  Cpu,
  Globe,
  Shield,
  Info,
  ExternalLink,
  AlertTriangle,
  Download,
  Trash2,
} from "lucide-react";
import { SettingsSection } from "@/components/settings/SettingsSection";
import { SettingRow } from "@/components/settings/SettingRow";
import { ToggleSwitch } from "@/components/settings/ToggleSwitch";
import {
  SelectDropdown,
  type SelectOption,
} from "@/components/settings/SelectDropdown";
import { SliderInput } from "@/components/settings/SliderInput";
import { Button } from "@/components/ui/Button";
import { useSettings } from "@/hooks/useSettings";
import { supportedLanguages } from "@/i18n";
import { cn } from "@/lib/utils";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

export default function Settings() {
  const { t } = useTranslation();
  const { settings, setSetting } = useSettings();
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const themeOptions: SelectOption[] = [
    { value: "dark", label: t("settings.dark") },
    { value: "light", label: t("settings.light") },
    { value: "system", label: t("settings.system") },
  ];

  const languageOptions: SelectOption[] = supportedLanguages.map((lang) => ({
    value: lang.code,
    label: `${lang.flag} ${lang.name}`,
    icon: lang.flag,
  }));

  const backendOptions: SelectOption[] = [
    { value: "auto", label: t("settings.auto") },
    { value: "native", label: t("settings.native") },
    { value: "simulation", label: t("settings.simulation") },
  ];

  const modelOptions: SelectOption[] = [
    { value: "BitNet-b1.58-large", label: "BitNet-b1.58 (0.7B)" },
    { value: "BitNet-b1.58-2B-4T", label: "BitNet-b1.58-2B-4T (2.4B)" },
    { value: "Llama3-8B-1.58", label: "Llama3-8B-1.58 (8B)" },
  ];

  const handleClearData = () => {
    if (showClearConfirm) {
      localStorage.clear();
      window.location.reload();
    } else {
      setShowClearConfirm(true);
      setTimeout(() => setShowClearConfirm(false), 5000);
    }
  };

  const handleExportData = () => {
    const data = {
      settings,
      conversations: localStorage.getItem("aria-conversations"),
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `aria-export-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6 max-w-[800px]"
    >
      {/* Header */}
      <motion.header variants={item} className="space-y-1">
        <h1 className="text-2xl font-bold text-text-primary">
          {t("settings.title")}
        </h1>
      </motion.header>

      {/* General */}
      <motion.div variants={item}>
        <SettingsSection
          title={t("settings.general")}
          icon={Settings2}
        >
          <SettingRow label={t("settings.theme")}>
            <SelectDropdown
              value={settings.theme}
              options={themeOptions}
              onChange={(v) =>
                setSetting("theme", v as "dark" | "light" | "system")
              }
            />
          </SettingRow>

          <SettingRow label={t("settings.language")}>
            <SelectDropdown
              value={settings.language}
              options={languageOptions}
              onChange={(v) => setSetting("language", v)}
            />
          </SettingRow>

          <SettingRow label={t("settings.startWithSystem")}>
            <ToggleSwitch
              checked={settings.autoStart}
              onChange={(v) => setSetting("autoStart", v)}
            />
          </SettingRow>

          <SettingRow label={t("settings.startMinimized")}>
            <ToggleSwitch
              checked={settings.startMinimized}
              onChange={(v) => setSetting("startMinimized", v)}
            />
          </SettingRow>

          <SettingRow label={t("settings.checkUpdatesAuto")}>
            <ToggleSwitch
              checked={settings.checkUpdates}
              onChange={(v) => setSetting("checkUpdates", v)}
            />
          </SettingRow>
        </SettingsSection>
      </motion.div>

      {/* Inference */}
      <motion.div variants={item}>
        <SettingsSection
          title={t("settings.inference")}
          icon={Cpu}
        >
          <SettingRow label={t("settings.defaultBackend")}>
            <SelectDropdown
              value={settings.backend}
              options={backendOptions}
              onChange={(v) =>
                setSetting("backend", v as "auto" | "native" | "simulation")
              }
            />
          </SettingRow>

          <SettingRow label={t("settings.defaultModel")}>
            <SelectDropdown
              value={settings.defaultModel}
              options={modelOptions}
              onChange={(v) => setSetting("defaultModel", v)}
            />
          </SettingRow>

          <SettingRow label={t("settings.maxCpuUsage")}>
            <SliderInput
              value={settings.maxCpuUsage}
              min={10}
              max={100}
              step={5}
              unit="%"
              onChange={(v) => setSetting("maxCpuUsage", v)}
            />
          </SettingRow>
        </SettingsSection>
      </motion.div>

      {/* Network */}
      <motion.div variants={item}>
        <SettingsSection
          title={t("settings.network")}
          icon={Globe}
        >
          <SettingRow label={t("settings.nodePort")}>
            <input
              type="number"
              value={settings.port}
              onChange={(e) => setSetting("port", Number(e.target.value))}
              className={cn(
                "w-24 h-9 px-3 rounded-lg text-sm font-mono text-center",
                "bg-surface/80 backdrop-blur-sm",
                "border border-border/50",
                "text-text-primary",
                "transition-all duration-200",
                "focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
              )}
            />
          </SettingRow>

          <SettingRow label={t("settings.enableP2P")}>
            <ToggleSwitch
              checked={settings.enableP2P}
              onChange={(v) => setSetting("enableP2P", v)}
            />
          </SettingRow>

          <SettingRow label={t("settings.maxPeers")}>
            <SliderInput
              value={settings.maxPeers}
              min={1}
              max={50}
              onChange={(v) => setSetting("maxPeers", v)}
            />
          </SettingRow>

          <SettingRow label={t("settings.bandwidthLimit")}>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={settings.bandwidthLimit}
                onChange={(e) =>
                  setSetting("bandwidthLimit", Number(e.target.value))
                }
                placeholder="0"
                className={cn(
                  "w-20 h-9 px-3 rounded-lg text-sm font-mono text-center",
                  "bg-surface/80 backdrop-blur-sm",
                  "border border-border/50",
                  "text-text-primary",
                  "transition-all duration-200",
                  "focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
                )}
              />
              <span className="text-xs text-text-secondary">MB/s</span>
            </div>
          </SettingRow>
        </SettingsSection>
      </motion.div>

      {/* Privacy */}
      <motion.div variants={item}>
        <SettingsSection
          title={t("settings.privacy")}
          icon={Shield}
        >
          <SettingRow
            label={t("settings.telemetry")}
            description={t("settings.telemetryDesc")}
          >
            <ToggleSwitch
              checked={settings.telemetry}
              onChange={(v) => setSetting("telemetry", v)}
            />
          </SettingRow>

          <SettingRow
            label={t("settings.dataRetention")}
          >
            <SliderInput
              value={settings.dataRetention}
              min={7}
              max={365}
              step={1}
              onChange={(v) => setSetting("dataRetention", v)}
              unit={` ${t("settings.days")}`}
            />
          </SettingRow>

          <div className="px-6 py-4 space-y-3">
            <div className="flex items-center gap-3">
              <Button
                variant="danger"
                size="sm"
                onClick={handleClearData}
              >
                <Trash2 size={14} />
                {showClearConfirm
                  ? t("settings.clearDataConfirm")
                  : t("settings.clearData")}
              </Button>
              <Button variant="secondary" size="sm" onClick={handleExportData}>
                <Download size={14} />
                {t("settings.exportData")}
              </Button>
            </div>

            <AnimatePresence>
              {showClearConfirm && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex items-center gap-2 text-xs text-warning"
                >
                  <AlertTriangle size={12} />
                  {t("settings.clearDataDesc")}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </SettingsSection>
      </motion.div>

      {/* About */}
      <motion.div variants={item}>
        <SettingsSection title={t("settings.about")} icon={Info}>
          <div className="px-6 py-5">
            <div className="flex items-center gap-4 mb-5">
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{
                  duration: 20,
                  repeat: Infinity,
                  ease: "linear",
                }}
                className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0"
              >
                <span className="text-white font-bold text-2xl">A</span>
              </motion.div>
              <div>
                <h3 className="text-lg font-bold text-text-primary">
                  ARIA Protocol
                </h3>
                <p className="text-sm text-text-secondary">
                  {t("settings.version")} v0.5.1
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" size="sm" onClick={() => {}}>
                {t("settings.checkUpdates")}
              </Button>
              <a
                href="https://github.com/spmfrance-cloud/aria-protocol"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="ghost" size="sm">
                  {t("settings.github")}
                  <ExternalLink size={12} />
                </Button>
              </a>
              <a
                href="https://spmfrance-cloud.github.io/aria-protocol/"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="ghost" size="sm">
                  {t("settings.documentation")}
                  <ExternalLink size={12} />
                </Button>
              </a>
              <a
                href="https://github.com/spmfrance-cloud/aria-protocol/issues"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="ghost" size="sm">
                  {t("settings.reportIssue")}
                  <ExternalLink size={12} />
                </Button>
              </a>
              <Button variant="ghost" size="sm" onClick={() => {}}>
                {t("settings.licenses")}
              </Button>
            </div>
          </div>
        </SettingsSection>
      </motion.div>
    </motion.div>
  );
}
