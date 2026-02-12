import { useState } from "react";
import { motion } from "framer-motion";
import {
  Button,
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  Input,
  Badge,
  Progress,
} from "@/components/ui";

const SearchIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" />
    <path
      d="M11 11L14 14"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

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

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <motion.section variants={item} className="space-y-4">
      <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
      {children}
    </motion.section>
  );
}

export default function DesignSystem() {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(67);

  const handleLoadingDemo = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="max-w-5xl space-y-10"
    >
      {/* Header */}
      <motion.header variants={item} className="space-y-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <span className="text-white font-bold text-lg">A</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gradient">
              ARIA Desktop
            </h1>
            <p className="text-sm text-text-secondary">
              Design System Preview — v0.5.5
            </p>
          </div>
        </div>
      </motion.header>

      {/* Color Palette */}
      <Section title="Color Palette">
        <div className="grid grid-cols-5 gap-3">
          {[
            { name: "Background", color: "bg-background", hex: "#0a0a0f" },
            { name: "Surface", color: "bg-surface", hex: "#12121a" },
            { name: "Primary", color: "bg-primary", hex: "#6366f1" },
            { name: "Accent", color: "bg-accent", hex: "#22d3ee" },
            { name: "Success", color: "bg-success", hex: "#10b981" },
            { name: "Warning", color: "bg-warning", hex: "#f59e0b" },
            { name: "Error", color: "bg-error", hex: "#ef4444" },
            { name: "Border", color: "bg-border", hex: "#1e1e2e" },
            { name: "Text", color: "bg-text-primary", hex: "#f8fafc" },
            {
              name: "Text Sec.",
              color: "bg-text-secondary",
              hex: "#94a3b8",
            },
          ].map(({ name, color, hex }) => (
            <div key={name} className="space-y-1.5">
              <div
                className={`h-12 rounded-lg ${color} border border-border/50`}
              />
              <p className="text-xs text-text-secondary">{name}</p>
              <p className="text-xs font-mono text-text-secondary/70">
                {hex}
              </p>
            </div>
          ))}
        </div>
      </Section>

      {/* Buttons */}
      <Section title="Buttons">
        <Card>
          <CardContent className="space-y-6">
            <div>
              <p className="text-sm text-text-secondary mb-3">Variants</p>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Danger</Button>
              </div>
            </div>

            <div>
              <p className="text-sm text-text-secondary mb-3">Sizes</p>
              <div className="flex flex-wrap items-center gap-3">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>

            <div>
              <p className="text-sm text-text-secondary mb-3">States</p>
              <div className="flex flex-wrap items-center gap-3">
                <Button loading={loading} onClick={handleLoadingDemo}>
                  {loading ? "Loading..." : "Click to load"}
                </Button>
                <Button disabled>Disabled</Button>
                <Button variant="secondary" loading>
                  Processing
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Cards */}
      <Section title="Cards">
        <div className="grid grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <h3 className="font-semibold">Standard Card</h3>
              <p className="text-sm text-text-secondary">
                With glassmorphism and gradient border on hover
              </p>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-text-secondary">
                This card features a frosted glass effect with backdrop blur
                and a subtle gradient border that appears on hover.
              </p>
            </CardContent>
            <CardFooter className="gap-2">
              <Button size="sm" variant="ghost">
                Cancel
              </Button>
              <Button size="sm">Confirm</Button>
            </CardFooter>
          </Card>

          <Card glow>
            <CardHeader>
              <h3 className="font-semibold">Glow Card</h3>
              <p className="text-sm text-text-secondary">
                With primary glow effect on hover
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-text-secondary">Status</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-text-secondary">Model</span>
                  <span className="text-sm font-mono">ARIA-1B</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-text-secondary">
                    Inference
                  </span>
                  <span className="text-sm font-mono text-accent">
                    42 tok/s
                  </span>
                </div>
                <Progress value={85} color="accent" size="sm" />
              </div>
            </CardContent>
          </Card>
        </div>
      </Section>

      {/* Inputs */}
      <Section title="Inputs">
        <Card>
          <CardContent>
            <div className="grid grid-cols-2 gap-6">
              <Input label="Model Name" placeholder="Enter model name..." />
              <Input
                label="Search"
                placeholder="Search models..."
                icon={<SearchIcon />}
              />
              <Input
                label="API Key"
                type="password"
                placeholder="sk-..."
                error="Invalid API key format"
              />
              <Input
                label="Disabled"
                placeholder="Not available"
                disabled
              />
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Badges */}
      <Section title="Badges">
        <Card>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Badge>Default</Badge>
              <Badge variant="success">Active</Badge>
              <Badge variant="warning">Pending</Badge>
              <Badge variant="error">Error</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="success">v0.5.5</Badge>
              <Badge variant="default">BitNet</Badge>
              <Badge variant="outline">1-bit</Badge>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Progress */}
      <Section title="Progress">
        <Card>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <Progress value={progress} color="primary" showLabel />
              <Progress value={45} color="accent" showLabel size="sm" />
              <Progress value={85} color="success" showLabel />
              <Progress value={30} color="warning" showLabel size="lg" />
              <Progress value={15} color="error" showLabel />
            </div>

            <div className="flex gap-3">
              <Button
                size="sm"
                variant="secondary"
                onClick={() =>
                  setProgress((p) => Math.max(0, p - 10))
                }
              >
                -10%
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() =>
                  setProgress((p) => Math.min(100, p + 10))
                }
              >
                +10%
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setProgress(0)}
              >
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Typography */}
      <Section title="Typography">
        <Card>
          <CardContent className="space-y-4">
            <div>
              <h1 className="text-3xl font-bold">Heading 1 — Inter Bold</h1>
              <h2 className="text-2xl font-semibold">
                Heading 2 — Inter Semibold
              </h2>
              <h3 className="text-xl font-medium">
                Heading 3 — Inter Medium
              </h3>
              <p className="text-base text-text-secondary">
                Body text — Inter Regular, secondary color
              </p>
              <p className="text-sm text-text-secondary/70">
                Small text — 14px, muted
              </p>
            </div>
            <div className="font-mono space-y-1">
              <p className="text-sm">
                <span className="text-accent">const</span>{" "}
                <span className="text-text-primary">model</span> ={" "}
                <span className="text-success">"ARIA-1B-BitNet"</span>;
              </p>
              <p className="text-sm">
                <span className="text-accent">const</span>{" "}
                <span className="text-text-primary">speed</span> ={" "}
                <span className="text-warning">42.5</span>;{" "}
                <span className="text-text-secondary">// tok/s</span>
              </p>
            </div>
            <p className="text-xl font-bold text-gradient">
              Gradient text with primary-to-accent
            </p>
          </CardContent>
        </Card>
      </Section>

      {/* Footer */}
      <motion.footer
        variants={item}
        className="text-center text-sm text-text-secondary/50 pb-8"
      >
        ARIA Protocol Desktop App — v0.5.5
      </motion.footer>
    </motion.div>
  );
}
