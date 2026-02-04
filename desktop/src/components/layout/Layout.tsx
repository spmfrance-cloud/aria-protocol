import React, { useState } from "react";
import { motion } from "framer-motion";
import { Sidebar } from "./Sidebar";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <motion.main
        initial={false}
        animate={{ marginLeft: collapsed ? 72 : 240 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="min-h-screen"
      >
        <div className="p-6">{children}</div>
      </motion.main>
    </div>
  );
};

Layout.displayName = "Layout";
