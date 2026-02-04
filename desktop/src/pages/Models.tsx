import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { Box, Search } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { ModelCard } from "@/components/models/ModelCard";
import { ModelDetails } from "@/components/models/ModelDetails";
import { ModelStats } from "@/components/models/ModelStats";
import { useModels } from "@/hooks/useModels";
import type { ModelInfo } from "@/hooks/useModels";
import { cn } from "@/lib/utils";

type Tab = "available" | "installed";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

const cardItem = {
  hidden: { opacity: 0, y: 16, scale: 0.97 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.4, ease: "easeOut" },
  },
};

export default function Models() {
  const { t } = useTranslation();
  const {
    models,
    getModelState,
    getInstalledModels,
    downloadModel,
    cancelDownload,
    removeModel,
  } = useModels();

  const [activeTab, setActiveTab] = useState<Tab>("available");
  const [search, setSearch] = useState("");
  const [selectedModel, setSelectedModel] = useState<ModelInfo | null>(null);
  const [showRemoveConfirm, setShowRemoveConfirm] = useState<string | null>(
    null
  );

  const installedModels = getInstalledModels();
  const installedCount = installedModels.length;

  const filteredModels = useMemo(() => {
    let list = models;

    if (activeTab === "installed") {
      list = list.filter((m) => getModelState(m.id).status === "installed");
    }

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (m) =>
          m.name.toLowerCase().includes(q) ||
          m.params.toLowerCase().includes(q)
      );
    }

    return list;
  }, [models, activeTab, search, getModelState]);

  const handleRemove = (modelId: string) => {
    if (showRemoveConfirm === modelId) {
      removeModel(modelId);
      setShowRemoveConfirm(null);
      if (selectedModel?.id === modelId) {
        setSelectedModel(null);
      }
    } else {
      setShowRemoveConfirm(modelId);
      setTimeout(() => setShowRemoveConfirm(null), 3000);
    }
  };

  return (
    <>
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-6 max-w-[1400px]"
      >
        {/* Header */}
        <motion.header variants={item} className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-text-primary">
              {t("models.title")}
            </h1>
            <Badge variant="default">
              <Box size={12} />
              {installedCount} {t("models.installed").toLowerCase()}
            </Badge>
          </div>
          <p className="text-sm text-text-secondary">
            Download and manage BitNet models for local inference
          </p>
        </motion.header>

        {/* Tabs + Search */}
        <motion.div
          variants={item}
          className="flex flex-col sm:flex-row sm:items-center gap-4"
        >
          {/* Tabs */}
          <div className="flex items-center p-1 rounded-lg bg-surface/60 border border-border/40">
            {([
              { value: "available" as Tab, labelKey: "models.available" },
              { value: "installed" as Tab, labelKey: "models.installed" },
            ]).map((tab) => (
              <button
                key={tab.value}
                onClick={() => setActiveTab(tab.value)}
                className={cn(
                  "relative px-4 py-2 text-sm font-medium rounded-md transition-all duration-200",
                  activeTab === tab.value
                    ? "text-text-primary"
                    : "text-text-secondary hover:text-text-primary"
                )}
              >
                {activeTab === tab.value && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute inset-0 rounded-md bg-primary/15 border border-primary/20"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{t(tab.labelKey)}</span>
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="flex-1 max-w-xs">
            <Input
              placeholder={t("models.searchModels")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              icon={<Search size={16} />}
              iconPosition="left"
            />
          </div>
        </motion.div>

        {/* Content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Model cards */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab + search}
                variants={container}
                initial="hidden"
                animate="show"
                className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4"
              >
                {filteredModels.length > 0 ? (
                  filteredModels.map((model) => {
                    const state = getModelState(model.id);
                    return (
                      <motion.div key={model.id} variants={cardItem}>
                        <ModelCard
                          model={model}
                          state={state}
                          onDownload={() => downloadModel(model.id)}
                          onCancel={() => cancelDownload(model.id)}
                          onRemove={() => handleRemove(model.id)}
                          onClick={() => setSelectedModel(model)}
                        />

                        {/* Remove confirmation overlay */}
                        <AnimatePresence>
                          {showRemoveConfirm === model.id && (
                            <motion.div
                              initial={{ opacity: 0, y: -4 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -4 }}
                              className="mt-2 p-2 rounded-lg bg-error-muted border border-error/20 text-center"
                            >
                              <p className="text-xs text-error mb-1.5">
                                Click Remove again to confirm
                              </p>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    );
                  })
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="col-span-full text-center py-16"
                  >
                    <Box
                      size={40}
                      className="mx-auto text-text-secondary/30 mb-3"
                    />
                    <p className="text-sm text-text-secondary">
                      {activeTab === "installed"
                        ? t("models.noModels")
                        : "No models found"}
                    </p>
                    {activeTab === "installed" && (
                      <button
                        onClick={() => setActiveTab("available")}
                        className="text-sm text-primary hover:text-primary-hover mt-2 transition-colors"
                      >
                        Browse available models
                      </button>
                    )}
                  </motion.div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Sidebar stats */}
          <motion.div variants={item} className="lg:col-span-1">
            <ModelStats models={models} />
          </motion.div>
        </div>
      </motion.div>

      {/* Model details drawer */}
      <AnimatePresence>
        {selectedModel && (
          <ModelDetails
            model={selectedModel}
            state={getModelState(selectedModel.id)}
            onClose={() => setSelectedModel(null)}
            onDownload={() => downloadModel(selectedModel.id)}
            onCancel={() => cancelDownload(selectedModel.id)}
            onRemove={() => handleRemove(selectedModel.id)}
          />
        )}
      </AnimatePresence>
    </>
  );
}
