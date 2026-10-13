"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Boxes, LogIn, UserPlus, Loader2, AlertCircle, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, register, user, authEnabled } = useAuth();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setNotice(null);
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
        router.push("/change-intel");
      } else {
        await register(email, password, fullName || undefined);
        setNotice("Akun dibuat. Silakan masuk.");
        setMode("login");
        setPassword("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex h-full w-full items-center justify-center p-6 bg-surface">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="flex items-center gap-2 mb-6 justify-center">
          <Boxes className="w-6 h-6 text-primary" />
          <div className="flex flex-col">
            <span className="font-mono text-xs text-primary tracking-widest uppercase font-semibold">
              Margin Guardian
            </span>
            <span className="font-mono text-[9px] text-on-surface-variant/60 tracking-wider">
              Civil Engineering AI
            </span>
          </div>
        </div>

        <div className="rounded-lg border border-surface-container-high bg-surface-container-low p-6">
          <div className="flex items-center gap-2 mb-1">
            {mode === "login" ? (
              <LogIn className="w-4 h-4 text-primary" />
            ) : (
              <UserPlus className="w-4 h-4 text-primary" />
            )}
            <h1 className="text-base font-semibold text-on-surface">
              {mode === "login" ? "Masuk ke Akun" : "Buat Akun Baru"}
            </h1>
          </div>
          <p className="text-xs text-on-surface-variant/70 mb-5">
            {mode === "login"
              ? "Gunakan email dan password terdaftar."
              : "User pertama yang mendaftar otomatis menjadi admin."}
          </p>

          {user && (
            <div className="mb-4 flex items-center gap-2 rounded border border-secondary/30 bg-secondary/10 px-3 py-2 text-xs text-secondary">
              <ShieldCheck className="w-3.5 h-3.5" />
              Sudah masuk sebagai {user.email}
            </div>
          )}

          {!authEnabled && (
            <div className="mb-4 rounded border border-surface-container-high bg-surface-container/60 px-3 py-2 text-[11px] text-on-surface-variant/70">
              Auth belum diaktifkan di backend (auth_enabled=false). Login bersifat opsional.
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === "register" && (
              <div>
                <label className="block text-[11px] font-medium text-on-surface-variant mb-1">
                  Nama Lengkap
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Opsional"
                  className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
                />
              </div>
            )}

            <div>
              <label className="block text-[11px] font-medium text-on-surface-variant mb-1">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="nama@perusahaan.com"
                className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-[11px] font-medium text-on-surface-variant mb-1">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimal 8 karakter"
                className="w-full rounded border border-surface-container-high bg-surface-container px-3 py-2 text-sm text-on-surface placeholder:text-on-surface-variant/40 focus:border-primary focus:outline-none"
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded border border-error/30 bg-error/10 px-3 py-2 text-xs text-error">
                <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            {notice && (
              <div className="rounded border border-secondary/30 bg-secondary/10 px-3 py-2 text-xs text-secondary">
                {notice}
              </div>
            )}

            <button
              type="submit"
              disabled={busy}
              className="flex w-full items-center justify-center gap-2 rounded bg-primary px-4 py-2 text-sm font-semibold text-on-primary-container transition-colors hover:bg-primary-container disabled:opacity-50"
            >
              {busy && <Loader2 className="w-4 h-4 animate-spin" />}
              {mode === "login" ? "Masuk" : "Daftar"}
            </button>
          </form>

          <div className="mt-4 text-center text-xs text-on-surface-variant/70">
            {mode === "login" ? (
              <>
                Belum punya akun?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setMode("register");
                    setError(null);
                  }}
                  className="text-primary hover:underline"
                >
                  Daftar
                </button>
              </>
            ) : (
              <>
                Sudah punya akun?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setMode("login");
                    setError(null);
                  }}
                  className="text-primary hover:underline"
                >
                  Masuk
                </button>
              </>
            )}
          </div>
        </div>

        <div className="mt-4 text-center">
          <Link href="/change-intel" className="text-xs text-on-surface-variant/60 hover:text-primary">
            Lanjut tanpa login →
          </Link>
        </div>
      </div>
    </div>
  );
}
