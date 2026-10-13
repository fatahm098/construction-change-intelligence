"use client";

import React from "react";
import { ProjectSummary } from "@/lib/types";
import { getExportCsvUrl } from "@/lib/api";
import { UserMenu } from "@/components/UserMenu";
import { Download, Layers, ShieldCheck, AlertCircle, FileSpreadsheet } from "lucide-react";

interface HeaderProps {
  summary: ProjectSummary | null;
  activeDiffCount: number;
}

export function Header({ summary, activeDiffCount }: HeaderProps) {
  const formatIDR = (val: number) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      maximumFractionDigits: 0,
    }).format(val);
  };

  const handleExport = () => {
    if (!summary?.project_id) return;
    window.open(getExportCsvUrl(summary.project_id), "_blank");
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3 shadow-[0_1px_8px_rgba(0,0,0,0.5)]">
      <div className="max-w-[1700px] mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Project Branding */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                MARGIN GUARDIAN
              </span>
              <span className="font-mono text-[9px] bg-surface-container-high text-primary px-1.5 py-0.5 rounded tracking-wider">
                ACTIVE CAD DIFF
              </span>
            </div>
            <h1 className="text-sm md:text-base font-semibold text-on-surface truncate">
              {summary ? summary.project_name : "Memuat Proyek..."} • LT.1 (Rev.0 vs Rev.1)
            </h1>
          </div>
        </div>

        {/* Center / Right: KPI Metrics & Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Variances KPI */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container-low border border-surface-container-high">
            <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
            <span className="font-mono text-xs text-primary font-semibold">
              {summary ? `${summary.total_changed_regions} Perubahan` : `${activeDiffCount} Perubahan`}
            </span>
          </div>

          {/* Verified KPI */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container-low border border-surface-container-high">
            <ShieldCheck className="w-3.5 h-3.5 text-secondary" />
            <span className="font-mono text-xs text-secondary font-semibold">
              {summary ? `${summary.verified_regions} Terverifikasi` : "0 Terverifikasi"}
            </span>
          </div>

          {/* Total Cost Delta KPI */}
          <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-secondary/10 border border-secondary/20">
            <span className="font-mono text-xs text-secondary font-bold">
              Δ {summary ? formatIDR(summary.total_cost_delta) : "IDR 0"}
            </span>
          </div>

          {/* Export Button */}
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-medium transition-colors shadow-sm ml-2 border border-outline-variant/40"
          >
            <Download className="w-3.5 h-3.5 text-primary" />
            <span>Ekspor CSV</span>
          </button>

          {/* User Menu */}
          <div className="ml-2">
            <UserMenu />
          </div>
        </div>
      </div>
    </header>
  );
}
