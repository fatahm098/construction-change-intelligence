"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import type { LLMKeySource, LLMSettings, LLMTestResult } from "@/lib/types";
import {
  ApiError,
  fetchLLMSettings,
  testLLMConnection,
  updateLLMSettings,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import {
  Settings2,
  KeyRound,
  Save,
  PlugZap,
  Loader2,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  Lock,
  AlertCircle,
  Trash2,
} from "lucide-react";

const PROVIDER_OPTIONS: { value: string; label: string }[] = [
  { value: "openai", label: "OpenAI / OpenAI-compatible" },
  { value: "ollama", label: "Ollama (lokal)" },
  { value: "local", label: "Local (tanpa LLM)" },
];

const SOURCE_META: Record<LLMKeySource, { label: string; className: string }> = {
  db: { label: "Tersimpan di DB", className: "text-secondary border-secondary/30 bg-secondary/10" },
  env: { label: "Dari environment", className: "text-primary border-primary/30 bg-primary/10" },
  none: { label: "Belum ada", className: "text-error border-error/30 bg-error-container/15" },
};

export default function SettingsPage() {
  const { user, authEnabled } = useAuth();

  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  // Form state
  const [provider, setProvider] = useState("openai");
  const [model, setModel] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [embeddingModel, setEmbeddingModel] = useState("");
  const [apiKey, setApiKey] = useState("");

  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<LLMTestResult | null>(null);

  const applySettings = (s: LLMSettings) => {
    setSettings(s);
    setProvider(s.provider);
    setModel(s.model);
    setBaseUrl(s.base_url);
    setEmbeddingModel(s.embedding_model);
    setApiKey("");
  };

  const load = async () => {
    setLoading(true);
    setLoadError(null);
    setForbidden(false);
    try {
      applySettings(await fetchLLMSettings());
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        setForbidden(true);
      } else {
        setLoadError(err instanceof Error ? err.message : "Gagal memuat pengaturan LLM.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const resetFeedback = () => {
    setNotice(null);
    setFormError(null);
    setTestResult(null);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    resetFeedback();
    setSaving(true);
    try {
      const updated = await updateLLMSettings({
        provider,
        model,
        base_url: baseUrl,
        embedding_model: embeddingModel,
        // Hanya kirim api_key bila diisi — undefined berarti key tersimpan tetap dipakai.
        ...(apiKey ? { api_key: apiKey } : {}),
      });
      applySettings(updated);
      setNotice("Pengaturan tersimpan.");
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Gagal menyimpan pengaturan.");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteKey = async () => {
    if (!window.confirm("Hapus API key tersimpan? Tindakan ini tidak bisa dibatalkan.")) return;
    resetFeedback();
    setDeleting(true);
    try {
      const updated = await updateLLMSettings({ api_key: "" });
      applySettings(updated);
      setNotice("API key dihapus.");
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Gagal menghapus API key.");
    } finally {
      setDeleting(false);
    }
  };

  const handleTest = async () => {
    resetFeedback();
    setTesting(true);
    try {
      setTestResult(await testLLMConnection());
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Gagal menguji koneksi.");
    } finally {
      setTesting(false);
    }
  };

  const busy = saving || testing || deleting;
  const sourceMeta = settings ? SOURCE_META[settings.source] : null;

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Settings2 className="w-5 h-5 text-primary" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                Pengaturan
              </span>
              <h1 className="text-sm font-semibold text-on-surface">API Key LLM</h1>
            </div>
          </div>
          {settings && sourceMeta && (
            <span
              className={`rounded border px-2.5 py-1 font-mono text-[10px] ${sourceMeta.className}`}
            >
              Sumber key: {sourceMeta.label}
            </span>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="mx-auto max-w-2xl space-y-4">
          {/* Security note */}
          <div className="flex items-start gap-2 rounded-lg border border-secondary/25 bg-secondary/5 px-3 py-2.5">
            <ShieldCheck className="w-4 h-4 text-secondary mt-0.5 shrink-0" />
            <p className="text-xs text-on-surface-variant">
              API key disimpan <span className="text-secondary font-medium">terenkripsi di server</span> dan
              tidak pernah dikirim ke browser. Kolom key di bawah bersifat tulis-saja (write-only).
            </p>
          </div>

          {loading && (
            <div className="flex items-center gap-2 text-sm text-on-surface-variant">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              Memuat pengaturan…
            </div>
          )}

          {forbidden && (
            <div className="rounded-lg border border-error/30 bg-error-container/15 p-4">
              <div className="flex items-center gap-2 text-error">
                <Lock className="w-4 h-4" />
                <span className="text-sm font-semibold">Akses ditolak</span>
              </div>
              <p className="mt-1.5 text-xs text-on-surface-variant">
                Halaman pengaturan hanya untuk admin. Silakan masuk dengan akun admin.
              </p>
              <Link
                href="/login"
                className="mt-3 inline-block rounded bg-primary px-3 py-1.5 text-xs font-semibold text-on-primary-container hover:bg-primary-container"
              >
                Ke halaman login
              </Link>
            </div>
          )}

          {loadError && !forbidden && (
            <div className="flex items-start gap-2 rounded-lg border border-error/30 bg-error-container/15 px-3 py-2.5 text-xs text-error">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <div className="flex-1">
                <p>{loadError}</p>
                <button onClick={load} className="mt-2 text-error underline">
                  Coba lagi
                </button>
              </div>
            </div>
          )}

          {!loading && !forbidden && !loadError && settings && (
            <form
              onSubmit={handleSave}
              className="space-y-4 rounded-lg border border-surface-container-high bg-surface-container-low p-4"
            >
              {/* Provider */}
              <div>
                <label className="mb-1 block text-[11px] font-medium text-on-surface-variant">
                  Provider LLM
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface focus:border-primary focus:outline-none"
                >
                  {PROVIDER_OPTIONS.map((p) => (
                    <option key={p.value} value={p.value}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Model */}
              <div>
                <label className="mb-1 block text-[11px] font-medium text-on-surface-variant">
                  Model
                </label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="mis. gpt-4o-mini"
                  className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
                />
              </div>

              {/* Embedding model */}
              <div>
                <label className="mb-1 block text-[11px] font-medium text-on-surface-variant">
                  Embedding Model
                </label>
                <input
                  type="text"
                  value={embeddingModel}
                  onChange={(e) => setEmbeddingModel(e.target.value)}
                  placeholder="mis. text-embedding-3-small"
                  className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
                />
              </div>

              {/* Base URL */}
              <div>
                <label className="mb-1 block text-[11px] font-medium text-on-surface-variant">
                  Base URL
                </label>
                <input
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  placeholder="https://api.openai.com/v1"
                  className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
                />
                <p className="mt-1 text-[10px] text-on-surface-variant/50">
                  Bisa diarahkan ke endpoint OpenAI-compatible (DeepSeek, Groq, OpenRouter, dsb.) atau
                  host Ollama.
                </p>
              </div>

              {/* API Key (write-only) */}
              <div>
                <label className="mb-1 flex items-center gap-1.5 text-[11px] font-medium text-on-surface-variant">
                  <KeyRound className="w-3.5 h-3.5" />
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  autoComplete="new-password"
                  placeholder={
                    settings.has_api_key
                      ? `${settings.api_key_masked || "••••••••"} — isi untuk mengganti`
                      : "Belum ada key. Tempel API key di sini."
                  }
                  className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
                />
                <div className="mt-1.5 flex items-center justify-between gap-2">
                  <p className="text-[10px] text-on-surface-variant/50">
                    Kosongkan bila tidak ingin mengubah key tersimpan.
                  </p>
                  {settings.has_api_key && (
                    <button
                      type="button"
                      onClick={handleDeleteKey}
                      disabled={busy}
                      className="flex items-center gap-1 rounded border border-error/30 px-2 py-1 text-[10px] font-medium text-error transition-colors hover:bg-error/10 disabled:opacity-50"
                    >
                      {deleting ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <Trash2 className="w-3 h-3" />
                      )}
                      Hapus key
                    </button>
                  )}
                </div>
              </div>

              {/* Feedback */}
              {notice && (
                <div className="flex items-center gap-2 rounded border border-secondary/30 bg-secondary/10 px-3 py-2 text-xs text-secondary">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {notice}
                </div>
              )}
              {formError && (
                <div className="flex items-start gap-2 rounded border border-error/30 bg-error-container/15 px-3 py-2 text-xs text-error">
                  <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                  {formError}
                </div>
              )}
              {testResult && (
                <div
                  className={`flex items-start gap-2 rounded border px-3 py-2 text-xs ${
                    testResult.ok
                      ? "border-secondary/30 bg-secondary/10 text-secondary"
                      : "border-error/30 bg-error-container/15 text-error"
                  }`}
                >
                  {testResult.ok ? (
                    <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                  ) : (
                    <XCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                  )}
                  <span>
                    {testResult.ok ? "Koneksi berhasil" : "Koneksi gagal"}
                    {testResult.model ? ` (${testResult.model})` : ""}: {testResult.message}
                  </span>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-2 pt-1">
                <button
                  type="submit"
                  disabled={busy}
                  className="flex items-center gap-1.5 rounded bg-primary px-4 py-2 text-sm font-semibold text-on-primary-container transition-colors hover:bg-primary-container disabled:opacity-50"
                >
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  Simpan
                </button>
                <button
                  type="button"
                  onClick={handleTest}
                  disabled={busy}
                  className="flex items-center gap-1.5 rounded border border-outline-variant/40 bg-surface-container-high px-4 py-2 text-sm font-medium text-on-surface transition-colors hover:bg-surface-bright disabled:opacity-50"
                >
                  {testing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <PlugZap className="w-4 h-4 text-primary" />
                  )}
                  Uji Koneksi
                </button>
              </div>
            </form>
          )}

          {!authEnabled && !forbidden && (
            <p className="text-[11px] text-on-surface-variant/50">
              Catatan: auth backend sedang nonaktif (auth_enabled=false). Bila endpoint pengaturan
              dilindungi admin, aktifkan auth dan masuk sebagai admin.
              {user ? ` Login saat ini: ${user.email}.` : ""}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
