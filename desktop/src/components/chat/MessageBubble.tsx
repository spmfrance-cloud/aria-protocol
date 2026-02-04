import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { User } from "lucide-react";
import type { Message } from "@/hooks/useChat";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

function renderMarkdown(text: string): React.ReactNode[] {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeLines: string[] = [];
  let codeLang = "";
  let blockIndex = 0;

  const processInline = (line: string, key: string): React.ReactNode => {
    // Process inline formatting: bold, italic, inline code
    const parts: React.ReactNode[] = [];
    // Match: **bold**, *italic*, `code`, [text](url)
    const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(line)) !== null) {
      // Text before match
      if (match.index > lastIndex) {
        parts.push(line.slice(lastIndex, match.index));
      }

      if (match[2]) {
        // **bold**
        parts.push(
          <strong key={`${key}-b-${match.index}`} className="font-semibold text-text-primary">
            {match[2]}
          </strong>
        );
      } else if (match[3]) {
        // *italic*
        parts.push(
          <em key={`${key}-i-${match.index}`} className="italic">
            {match[3]}
          </em>
        );
      } else if (match[4]) {
        // `inline code`
        parts.push(
          <code
            key={`${key}-c-${match.index}`}
            className="px-1.5 py-0.5 rounded bg-background/80 text-accent font-mono text-[0.85em]"
          >
            {match[4]}
          </code>
        );
      }

      lastIndex = match.index + match[0].length;
    }

    // Remaining text
    if (lastIndex < line.length) {
      parts.push(line.slice(lastIndex));
    }

    return parts.length > 0 ? <>{parts}</> : line;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code block start/end
    if (line.startsWith("```")) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeLang = line.slice(3).trim();
        codeLines = [];
        continue;
      } else {
        inCodeBlock = false;
        elements.push(
          <div
            key={`code-${blockIndex++}`}
            className="my-2 rounded-lg overflow-hidden border border-border/50"
          >
            {codeLang && (
              <div className="px-3 py-1 bg-background/60 text-[10px] text-text-secondary font-mono uppercase tracking-wider">
                {codeLang}
              </div>
            )}
            <pre className="px-3 py-2.5 bg-background/40 overflow-x-auto">
              <code className="text-sm font-mono text-text-primary/90 leading-relaxed">
                {codeLines.join("\n")}
              </code>
            </pre>
          </div>
        );
        continue;
      }
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    // Empty line → spacing
    if (line.trim() === "") {
      elements.push(<div key={`space-${i}`} className="h-2" />);
      continue;
    }

    // Headers
    if (line.startsWith("### ")) {
      elements.push(
        <h3
          key={`h3-${i}`}
          className="text-sm font-semibold text-text-primary mt-3 mb-1"
        >
          {processInline(line.slice(4), `h3-${i}`)}
        </h3>
      );
      continue;
    }

    if (line.startsWith("## ")) {
      elements.push(
        <h2
          key={`h2-${i}`}
          className="text-base font-semibold text-text-primary mt-3 mb-1"
        >
          {processInline(line.slice(3), `h2-${i}`)}
        </h2>
      );
      continue;
    }

    // Table rows
    if (line.includes("|") && line.trim().startsWith("|")) {
      // Collect table
      const tableLines: string[] = [line];
      while (
        i + 1 < lines.length &&
        lines[i + 1].includes("|") &&
        lines[i + 1].trim().startsWith("|")
      ) {
        i++;
        tableLines.push(lines[i]);
      }

      const rows = tableLines
        .filter((l) => !l.match(/^\|[\s-:|]+\|$/)) // skip separator
        .map((l) =>
          l
            .split("|")
            .map((c) => c.trim())
            .filter(Boolean)
        );

      if (rows.length > 0) {
        elements.push(
          <div
            key={`table-${blockIndex++}`}
            className="my-2 overflow-x-auto rounded-lg border border-border/50"
          >
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-background/40">
                  {rows[0].map((cell, ci) => (
                    <th
                      key={ci}
                      className="px-3 py-1.5 text-left font-medium text-text-secondary text-xs"
                    >
                      {processInline(cell, `th-${ci}`)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.slice(1).map((row, ri) => (
                  <tr key={ri} className="border-t border-border/30">
                    {row.map((cell, ci) => (
                      <td
                        key={ci}
                        className="px-3 py-1.5 text-text-primary/80 text-xs"
                      >
                        {processInline(cell, `td-${ri}-${ci}`)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      continue;
    }

    // List items
    if (line.match(/^[-•] /)) {
      elements.push(
        <div key={`li-${i}`} className="flex items-start gap-2 py-0.5 pl-1">
          <span className="text-primary mt-1.5 text-[6px]">●</span>
          <span className="text-sm leading-relaxed">
            {processInline(line.slice(2), `li-${i}`)}
          </span>
        </div>
      );
      continue;
    }

    // Numbered list
    if (line.match(/^\d+\.\s/)) {
      const num = line.match(/^(\d+)\./)?.[1];
      const rest = line.replace(/^\d+\.\s/, "");
      elements.push(
        <div key={`ol-${i}`} className="flex items-start gap-2 py-0.5 pl-1">
          <span className="text-primary text-xs font-mono mt-0.5 min-w-[1rem] text-right">
            {num}.
          </span>
          <span className="text-sm leading-relaxed">
            {processInline(rest, `ol-${i}`)}
          </span>
        </div>
      );
      continue;
    }

    // Normal paragraph
    elements.push(
      <p key={`p-${i}`} className="text-sm leading-relaxed">
        {processInline(line, `p-${i}`)}
      </p>
    );
  }

  return elements;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isStreaming = false,
}) => {
  const [showTime, setShowTime] = useState(false);
  const isUser = message.role === "user";

  const timeAgo = useMemo(
    () =>
      formatDistanceToNow(message.timestamp, { addSuffix: true }),
    [message.timestamp]
  );

  const renderedContent = useMemo(
    () => (isUser ? null : renderMarkdown(message.content)),
    [message.content, isUser]
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 30,
      }}
      className={cn(
        "flex items-start gap-3 px-4 py-3 group",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      onMouseEnter={() => setShowTime(true)}
      onMouseLeave={() => setShowTime(false)}
    >
      {/* Avatar */}
      {isUser ? (
        <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
          <User size={16} className="text-primary" />
        </div>
      ) : (
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-xs">A</span>
        </div>
      )}

      {/* Content */}
      <div
        className={cn(
          "relative max-w-[75%] min-w-0",
          isUser ? "items-end" : "items-start"
        )}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3",
            isUser
              ? "bg-primary/15 border border-primary/20 rounded-tr-sm"
              : "bg-surface border border-border/50 rounded-tl-sm"
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          ) : (
            <div className="space-y-0.5">
              {renderedContent}
              {isStreaming && (
                <motion.span
                  className="inline-block w-0.5 h-4 bg-primary ml-0.5 align-middle"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                />
              )}
            </div>
          )}
        </div>

        {/* Timestamp */}
        <motion.div
          initial={false}
          animate={{ opacity: showTime ? 1 : 0, y: showTime ? 0 : -4 }}
          transition={{ duration: 0.15 }}
          className={cn(
            "absolute -bottom-5 text-[10px] text-text-secondary/50 whitespace-nowrap",
            isUser ? "right-0" : "left-0"
          )}
        >
          {timeAgo}
        </motion.div>
      </div>
    </motion.div>
  );
};

MessageBubble.displayName = "MessageBubble";
