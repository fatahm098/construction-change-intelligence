"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  GitCompareArrows,
  FileQuestion,
  FileText,
  TrendingUp,
  FolderGit2,
  ClipboardCheck,
  ShieldAlert,
  Boxes,
  Settings2,
} from "lucide-react";

interface ModuleEntry {
  id: string;
  label: string;
  href: string;
  icon: React.ReactNode;
  status: "active" | "soon";
  description: string;
}

const MODULES: ModuleEntry[] = [
  {
    id: "change-intel",
    label: "Change Intelligence",
    href: "/change-intel",
    icon: <GitCompareArrows className="w-4 h-4" />,
    status: "active",
    description: "Deteksi perubahan gambar & dampak biaya",
  },
  {
    id: "doc-qa",
    label: "Document Q&A",
    href: "/doc-qa",
    icon: <FileQuestion className="w-4 h-4" />,
    status: "active",
    description: "Chat RAG dokumen RKS/kontrak/SNI",
  },
  {
    id: "boq-rab",
    label: "BOQ & RAB",
    href: "/boq-rab",
    icon: <FileText className="w-4 h-4" />,
    status: "active",
    description: "Estimasi & AHSP Indonesia",
  },
  {
    id: "progress",
    label: "Progress & EVM",
    href: "/progress",
    icon: <TrendingUp className="w-4 h-4" />,
    status: "active",
    description: "Kurva-S & earned value",
  },
  {
    id: "vo-rfi",
    label: "VO & RFI",
    href: "/vo-rfi",
    icon: <FolderGit2 className="w-4 h-4" />,
    status: "active",
    description: "Variation order & request info",
  },
  {
    id: "qc",
    label: "QC / Mutu",
    href: "/qc",
    icon: <ClipboardCheck className="w-4 h-4" />,
    status: "active",
    description: "Inspeksi mutu & checklist",
  },
  {
    id: "k3",
    label: "K3 / Safety",
    href: "/k3",
    icon: <ShieldAlert className="w-4 h-4" />,
    status: "active",
    description: "Laporan keselamatan kerja",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col w-60 min-w-60 h-full bg-surface-container-lowest border-r border-surface-container-high/50 overflow-y-auto">
      {/* Brand */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-surface-container-high/30">
        <Boxes className="w-5 h-5 text-primary" />
        <div className="flex flex-col">
          <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
            Margin Guardian
          </span>
          <span className="font-mono text-[9px] text-on-surface-variant/60 tracking-wider">
            Civil Engineering AI
          </span>
        </div>
      </div>

      {/* Module Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        <div className="px-2 py-1.5">
          <span className="font-mono text-[9px] text-on-surface-variant/50 tracking-widest uppercase">
            Modul
          </span>
        </div>
        {MODULES.map((mod) => {
          const isActive = pathname === mod.href || pathname.startsWith(mod.href + "/");
          return (
            <Link
              key={mod.id}
              href={mod.status === "active" ? mod.href : "#"}
              className={`group flex items-start gap-2.5 px-2.5 py-2 rounded-md transition-colors ${
                isActive
                  ? "bg-primary/10 border border-primary/20"
                  : mod.status === "active"
                    ? "hover:bg-surface-container-high/50 border border-transparent"
                    : "opacity-40 cursor-not-allowed border border-transparent"
              }`}
            >
              <span className={`mt-0.5 ${isActive ? "text-primary" : "text-on-surface-variant/70"}`}>
                {mod.icon}
              </span>
              <div className="flex flex-col min-w-0">
                <span
                  className={`text-xs font-medium truncate ${
                    isActive ? "text-primary" : "text-on-surface"
                  }`}
                >
                  {mod.label}
                </span>
                <span className="text-[10px] text-on-surface-variant/50 truncate">
                  {mod.description}
                </span>
              </div>
              {mod.status === "soon" && (
                <span className="ml-auto font-mono text-[8px] text-on-surface-variant/40 px-1 py-0.5 rounded bg-surface-container-high/40">
                  SOON
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-2 py-2 border-t border-surface-container-high/30 space-y-1">
        <Link
          href="/settings"
          className={`flex items-center gap-2.5 px-2.5 py-2 rounded-md transition-colors ${
            pathname === "/settings" || pathname.startsWith("/settings/")
              ? "bg-primary/10 border border-primary/20 text-primary"
              : "hover:bg-surface-container-high/50 border border-transparent text-on-surface"
          }`}
        >
          <Settings2
            className={`w-4 h-4 ${
              pathname === "/settings" ? "text-primary" : "text-on-surface-variant/70"
            }`}
          />
          <span className="text-xs font-medium">Pengaturan</span>
        </Link>
        <div className="px-2.5 pt-1">
          <span className="font-mono text-[9px] text-on-surface-variant/40 tracking-wider">
            v1.0.0-dev
          </span>
        </div>
      </div>
    </aside>
  );
}
