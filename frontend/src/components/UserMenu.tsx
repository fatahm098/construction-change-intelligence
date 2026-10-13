"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { LogIn, LogOut, ChevronDown, UserCircle2, ShieldCheck } from "lucide-react";

const ROLE_LABEL: Record<string, string> = {
  admin: "Admin",
  engineer: "Engineer",
  viewer: "Viewer",
};

export function UserMenu() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (loading) {
    return <div className="h-7 w-24 rounded bg-surface-container-high/40 animate-pulse" />;
  }

  if (!user) {
    return (
      <Link
        href="/login"
        className="flex items-center gap-1.5 rounded bg-surface-container-high px-3 py-1.5 text-xs font-medium text-on-surface transition-colors hover:bg-surface-bright border border-outline-variant/40"
      >
        <LogIn className="w-3.5 h-3.5 text-primary" />
        Masuk
      </Link>
    );
  }

  const initials = (user.full_name || user.email).slice(0, 1).toUpperCase();

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded bg-surface-container-high px-2 py-1.5 text-xs text-on-surface transition-colors hover:bg-surface-bright border border-outline-variant/40"
      >
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-[10px] font-bold text-primary">
          {initials}
        </span>
        <span className="hidden max-w-[120px] truncate sm:inline">
          {user.full_name || user.email}
        </span>
        <ChevronDown className="w-3.5 h-3.5 text-on-surface-variant/70" />
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-56 rounded-md border border-surface-container-high bg-surface-container-low shadow-lg">
          <div className="border-b border-surface-container-high/60 px-3 py-2.5">
            <div className="flex items-center gap-2">
              <UserCircle2 className="w-4 h-4 text-primary" />
              <div className="flex flex-col min-w-0">
                <span className="truncate text-xs font-medium text-on-surface">
                  {user.full_name || "Tanpa Nama"}
                </span>
                <span className="truncate text-[10px] text-on-surface-variant/60">
                  {user.email}
                </span>
              </div>
            </div>
            <div className="mt-2 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-secondary" />
              <span className="font-mono text-[10px] text-secondary">
                {ROLE_LABEL[user.role] || user.role}
              </span>
            </div>
          </div>
          <button
            onClick={() => {
              setOpen(false);
              logout();
              router.push("/login");
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-xs text-error transition-colors hover:bg-error/10"
          >
            <LogOut className="w-3.5 h-3.5" />
            Keluar
          </button>
        </div>
      )}
    </div>
  );
}
