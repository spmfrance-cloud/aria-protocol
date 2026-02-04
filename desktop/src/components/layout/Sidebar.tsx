import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Box,
  MessageSquare,
  Zap,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/models", label: "Models", icon: Box },
  { path: "/chat", label: "Chat", icon: MessageSquare },
  { path: "/energy", label: "Energy", icon: Zap },
  { path: "/settings", label: "Settings", icon: Settings },
] as const;

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const location = useLocation();

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className={cn(
        "fixed left-0 top-0 bottom-0 z-40",
        "bg-surface/90 backdrop-blur-xl",
        "border-r border-border/50",
        "flex flex-col",
        "select-none"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-border/50">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-lg">A</span>
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <h1 className="text-base font-bold text-gradient whitespace-nowrap">
                ARIA Desktop
              </h1>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive =
            path === "/"
              ? location.pathname === "/"
              : location.pathname.startsWith(path);

          return (
            <NavLink key={path} to={path}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                  "relative flex items-center gap-3 rounded-lg",
                  "transition-all duration-200",
                  collapsed ? "px-0 py-3 justify-center" : "px-3 py-2.5",
                  isActive
                    ? "bg-gradient-to-r from-primary/20 to-accent/10 text-text-primary"
                    : "text-text-secondary hover:text-text-primary hover:bg-surface"
                )}
              >
                {/* Active indicator glow */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-gradient-to-r from-primary/20 to-accent/10 border border-primary/20"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}

                <Icon
                  size={20}
                  className={cn(
                    "relative z-10 flex-shrink-0 transition-colors duration-200",
                    isActive && "text-primary"
                  )}
                />

                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      transition={{ duration: 0.15 }}
                      className="relative z-10 text-sm font-medium whitespace-nowrap"
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.div>
            </NavLink>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="px-2 pb-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onToggle}
          className={cn(
            "w-full flex items-center justify-center gap-2 rounded-lg",
            "py-2 text-text-secondary hover:text-text-primary",
            "hover:bg-surface transition-all duration-200"
          )}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-xs"
              >
                Collapse
              </motion.span>
            )}
          </AnimatePresence>
        </motion.button>
      </div>

      {/* Version */}
      <div className="px-4 py-3 border-t border-border/50">
        <AnimatePresence>
          {!collapsed ? (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs text-text-secondary/50 text-center"
            >
              ARIA Protocol v0.5.0
            </motion.p>
          ) : (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs text-text-secondary/50 text-center"
            >
              v0.5
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  );
};

Sidebar.displayName = "Sidebar";
