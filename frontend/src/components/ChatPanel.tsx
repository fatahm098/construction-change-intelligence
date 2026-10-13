"use client";

import React, { useRef, useState, useEffect } from "react";
import { ChatSource } from "@/lib/types";
import { Send, Sparkles, Bot, User, FileText, Loader2 } from "lucide-react";

export interface ChatMessageItem {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

interface ChatPanelProps {
  messages: ChatMessageItem[];
  onSend: (question: string) => Promise<void>;
  loading: boolean;
  disabled?: boolean;
}

const SUGGESTIONS = [
  "Apa syarat pengajuan Variation Order?",
  "Berapa mutu beton untuk kolom?",
  "Bagaimana aturan Extension of Time?",
];

export function ChatPanel({ messages, onSend, loading, disabled }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    await onSend(q);
  };

  return (
    <div className="flex flex-col h-full bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-surface-container-high flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-primary" />
        <div>
          <span className="font-mono text-[10px] text-primary tracking-wider uppercase font-semibold">
            Tanya Dokumen (RAG)
          </span>
          <p className="text-[10px] text-on-surface-variant/60">
            Jawaban bersitasi dari dokumen proyek — tanpa mengarang angka
          </p>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-3">
            <Bot className="w-10 h-10 text-primary/40" />
            <p className="text-sm text-on-surface-variant">
              Tanyakan apa saja tentang dokumen proyek.
            </p>
            <div className="flex flex-col gap-1.5 w-full max-w-md mt-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => onSend(s)}
                  disabled={disabled || loading}
                  className="text-left text-xs px-3 py-2 rounded bg-surface-container border border-surface-container-high hover:border-primary/40 hover:bg-surface-container-high/60 transition-colors text-on-surface-variant disabled:opacity-40"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2.5 ${msg.role === "user" ? "justify-end" : ""}`}>
            {msg.role === "assistant" && (
              <div className="w-6 h-6 rounded-full bg-primary/15 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5 text-primary" />
              </div>
            )}
            <div className={`flex flex-col gap-1.5 max-w-[85%] ${msg.role === "user" ? "items-end" : ""}`}>
              <div
                className={`px-3 py-2 rounded-lg text-xs leading-relaxed whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-secondary-container/20 border border-secondary/20 text-on-surface"
                    : "bg-surface-container border border-surface-container-high text-on-surface"
                }`}
              >
                {msg.content}
              </div>

              {/* Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {msg.sources.map((src, j) => (
                    <span
                      key={j}
                      title={src.snippet}
                      className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20 font-mono text-[9px] text-primary"
                    >
                      <FileText className="w-2.5 h-2.5" />
                      {src.filename}
                      {src.page ? ` hal.${src.page}` : ""}
                      <span className="text-primary/50">{src.score.toFixed(2)}</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
            {msg.role === "user" && (
              <div className="w-6 h-6 rounded-full bg-secondary/15 flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5 text-secondary" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5">
            <div className="w-6 h-6 rounded-full bg-primary/15 flex items-center justify-center shrink-0">
              <Bot className="w-3.5 h-3.5 text-primary" />
            </div>
            <div className="px-3 py-2 rounded-lg bg-surface-container border border-surface-container-high">
              <Loader2 className="w-3.5 h-3.5 text-primary animate-spin" />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-3 border-t border-surface-container-high">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            rows={1}
            placeholder={disabled ? "Unggah dokumen terlebih dahulu..." : "Tulis pertanyaan..."}
            disabled={disabled}
            className="flex-1 resize-none bg-surface-container-lowest border border-outline-variant/40 rounded px-3 py-2 text-xs text-on-surface placeholder:text-on-surface-variant/40 focus:outline-none focus:border-primary disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || disabled || !input.trim()}
            className="p-2 rounded bg-secondary-container hover:bg-secondary text-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
