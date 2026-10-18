"use client";

import React, { useState, useEffect } from "react";
import { RABResponse, AHSPItem, AHSPComponent } from "@/lib/types";
import { fetchRAB, fetchAHSPList, fetchAHSPDetail, uploadBOQ } from "@/lib/api";
import { downloadReport } from "@/lib/reports";
import type { ReportFormat } from "@/lib/reports";
import {
  FileSpreadsheet,
  Upload,
  ChevronRight,
  Layers,
  HardHat,
  Package,
  Wrench,
  Download,
} from "lucide-react";

const formatIDR = (val: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val);

const TYPE_META: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  labor: { label: "Tenaga Kerja", icon: <HardHat className="w-3 h-3" />, color: "text-primary" },
  material: { label: "Bahan", icon: <Package className="w-3 h-3" />, color: "text-secondary" },
  equipment: { label: "Peralatan", icon: <Wrench className="w-3 h-3" />, color: "text-tertiary" },
};

export default function BoqRabPage() {
  const [projectId] = useState<number | null>(1);
  const [rab, setRab] = useState<RABResponse | null>(null);
  const [ahspList, setAhspList] = useState<AHSPItem[]>([]);
  const [ahspDetail, setAhspDetail] = useState<AHSPItem | null>(null);
  const [uploading, setUploading] = useState(false);
  const [downloading, setDownloading] = useState<ReportFormat | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const loadData = async () => {
    if (projectId == null) return;
    try {
      const [rabData, ahspData] = await Promise.all([fetchRAB(projectId), fetchAHSPList()]);
      setRab(rabData);
      setAhspList(ahspData || []);
    } catch (err) {
      console.error("Gagal memuat data RAB/AHSP:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleDownload = async (format: ReportFormat) => {
    if (projectId == null) return;
    setDownloading(format);
    setDownloadError(null);
    try {
      await downloadReport(projectId, "rab", format);
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : "Gagal mengunduh laporan RAB.");
    } finally {
      setDownloading(null);
    }
  };

  const handleSelectAHSP = async (id: number) => {
    try {
      const detail = await fetchAHSPDetail(id);
      setAhspDetail(detail);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || projectId == null) return;
    setUploading(true);
    try {
      await uploadBOQ(projectId, file);
      await loadData();
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal mengunggah BOQ.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-primary" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                BOQ &amp; RAB
              </span>
              <h1 className="text-sm font-semibold text-on-surface">
                {rab ? rab.project_name : "Memuat RAB..."}
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container-low border border-surface-container-high">
              <span className="font-mono text-[10px] text-on-surface-variant">Kontrak</span>
              <span className="font-mono text-xs text-on-surface font-semibold">
                {rab ? formatIDR(rab.total_contract) : "-"}
              </span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-secondary/10 border border-secondary/20">
              <span className="font-mono text-[10px] text-secondary">Adjusted</span>
              <span className="font-mono text-xs text-secondary font-bold">
                {rab ? formatIDR(rab.total_adjusted) : "-"}
              </span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-primary/10 border border-primary/20">
              <span className="font-mono text-[10px] text-primary">Δ Variasi</span>
              <span className="font-mono text-xs text-primary font-bold">
                {rab ? formatIDR(rab.total_delta) : "-"}
              </span>
            </div>

            <label className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-medium transition-colors cursor-pointer border border-outline-variant/40">
              <Upload className="w-3.5 h-3.5 text-primary" />
              <span>{uploading ? "Mengunggah..." : "Unggah BOQ"}</span>
              <input
                type="file"
                accept=".xlsx,.xls"
                className="hidden"
                onChange={handleUpload}
                disabled={uploading}
              />
            </label>

            <button
              onClick={() => handleDownload("xlsx")}
              disabled={downloading !== null || projectId == null}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-medium transition-colors border border-primary/30 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloading === "xlsx" ? "Menyiapkan…" : "Unduh RAB (Excel)"}</span>
            </button>

            <button
              onClick={() => handleDownload("pdf")}
              disabled={downloading !== null || projectId == null}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-medium transition-colors border border-primary/30 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloading === "pdf" ? "Menyiapkan…" : "Unduh RAB (PDF)"}</span>
            </button>
          </div>
        </div>

        {downloadError && (
          <div className="mt-2 px-3 py-1.5 rounded bg-error-container/30 border border-error/30 text-error text-[11px] font-mono">
            {downloadError}
          </div>
        )}
      </header>

      {/* Workspace */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* RAB Table */}
        <div className="flex-[66] h-full min-w-0 flex flex-col bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
            <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
              Rencana Anggaran Biaya
            </span>
            <span className="font-mono text-[10px] text-on-surface-variant">
              {rab ? `${rab.item_count} item • ${rab.verified_region_count} region terverifikasi` : "-"}
            </span>
          </div>

          <div className="flex-1 overflow-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-surface-container z-10">
                <tr className="text-left text-on-surface-variant/70 font-mono text-[10px] uppercase">
                  <th className="px-3 py-2 font-medium">Kode</th>
                  <th className="px-3 py-2 font-medium">Uraian Pekerjaan</th>
                  <th className="px-3 py-2 font-medium text-right">Vol Kontrak</th>
                  <th className="px-3 py-2 font-medium text-right">Δ Vol</th>
                  <th className="px-3 py-2 font-medium text-right">Vol Akhir</th>
                  <th className="px-3 py-2 font-medium text-right">Harga Satuan</th>
                  <th className="px-3 py-2 font-medium text-right">Jumlah</th>
                  <th className="px-3 py-2 font-medium text-right">Δ Biaya</th>
                </tr>
              </thead>
              <tbody className="font-mono">
                {rab?.lines.map((ln) => (
                  <tr
                    key={ln.boq_item_id}
                    className="border-t border-surface-container-high/40 hover:bg-surface-container/50"
                  >
                    <td className="px-3 py-2 text-primary">{ln.code}</td>
                    <td className="px-3 py-2 text-on-surface font-sans max-w-[280px]">
                      <div className="truncate" title={ln.description}>
                        {ln.description}
                      </div>
                      {ln.ahsp_code && (
                        <span className="font-mono text-[9px] text-on-surface-variant/50">
                          AHSP: {ln.ahsp_code}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right text-on-surface-variant">
                      {ln.contract_volume.toLocaleString("id-ID")} {ln.unit}
                    </td>
                    <td
                      className={`px-3 py-2 text-right ${
                        ln.delta_volume !== 0 ? "text-primary font-semibold" : "text-on-surface-variant/40"
                      }`}
                    >
                      {ln.delta_volume !== 0 ? `+${ln.delta_volume.toLocaleString("id-ID")}` : "—"}
                    </td>
                    <td className="px-3 py-2 text-right text-on-surface">
                      {ln.adjusted_volume.toLocaleString("id-ID")}
                    </td>
                    <td className="px-3 py-2 text-right text-on-surface-variant">
                      {ln.unit_price.toLocaleString("id-ID")}
                    </td>
                    <td className="px-3 py-2 text-right text-on-surface">
                      {formatIDR(ln.adjusted_amount)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-semibold ${
                        ln.delta_amount > 0
                          ? "text-secondary"
                          : ln.delta_amount < 0
                            ? "text-error"
                            : "text-on-surface-variant/40"
                      }`}
                    >
                      {ln.delta_amount !== 0 ? formatIDR(ln.delta_amount) : "—"}
                    </td>
                  </tr>
                ))}
                {(!rab || rab.lines.length === 0) && (
                  <tr>
                    <td colSpan={8} className="px-3 py-8 text-center text-on-surface-variant/50 font-sans">
                      Belum ada item BOQ. Unggah spreadsheet BOQ untuk memulai.
                    </td>
                  </tr>
                )}
              </tbody>
              {rab && rab.lines.length > 0 && (
                <tfoot className="sticky bottom-0 bg-surface-container">
                  <tr className="border-t-2 border-primary/30 font-mono text-xs">
                    <td colSpan={6} className="px-3 py-2.5 text-right text-on-surface-variant font-semibold">
                      TOTAL RAB
                    </td>
                    <td className="px-3 py-2.5 text-right text-on-surface font-bold">
                      {formatIDR(rab.total_adjusted)}
                    </td>
                    <td className="px-3 py-2.5 text-right text-primary font-bold">
                      {formatIDR(rab.total_delta)}
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </div>

        {/* AHSP Catalog */}
        <div className="flex-[34] h-full min-w-[320px] max-w-[440px] flex flex-col bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary" />
            <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
              Katalog AHSP
            </span>
          </div>

          <div className="flex-1 overflow-y-auto">
            {ahspList.map((item) => (
              <button
                key={item.id}
                onClick={() => handleSelectAHSP(item.id)}
                className={`w-full flex items-center gap-2 px-3 py-2.5 border-b border-surface-container-high/40 text-left transition-colors ${
                  ahspDetail?.id === item.id
                    ? "bg-primary/10 border-l-2 border-l-primary"
                    : "hover:bg-surface-container/60 border-l-2 border-l-transparent"
                }`}
              >
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="text-xs text-on-surface truncate">{item.name}</span>
                  <span className="font-mono text-[9px] text-on-surface-variant/60">
                    {item.code} • {item.unit}
                  </span>
                </div>
                <span className="font-mono text-[10px] text-secondary font-semibold whitespace-nowrap">
                  {formatIDR(item.unit_price)}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-on-surface-variant/40 shrink-0" />
              </button>
            ))}
            {ahspList.length === 0 && (
              <p className="text-xs text-on-surface-variant/50 text-center py-6">
                Katalog AHSP kosong.
              </p>
            )}
          </div>

          {/* AHSP Detail */}
          {ahspDetail && (
            <div className="border-t border-surface-container-high max-h-[55%] overflow-y-auto">
              <div className="px-3 py-2 bg-surface-container sticky top-0">
                <span className="font-mono text-[10px] text-primary font-semibold">
                  {ahspDetail.code}
                </span>
                <p className="text-xs text-on-surface">{ahspDetail.name}</p>
                <span className="font-mono text-[10px] text-on-surface-variant/60">
                  per {ahspDetail.unit}
                </span>
              </div>
              <div className="p-2 space-y-1">
                {ahspDetail.components.map((c: AHSPComponent) => {
                  const meta = TYPE_META[c.component_type] || TYPE_META.material;
                  return (
                    <div
                      key={c.id}
                      className="flex items-center gap-2 px-2 py-1.5 rounded bg-surface-container border border-surface-container-high/40"
                    >
                      <span className={`${meta.color} shrink-0`}>{meta.icon}</span>
                      <div className="flex flex-col min-w-0 flex-1">
                        <span className="text-[11px] text-on-surface truncate">{c.name}</span>
                        <span className="font-mono text-[9px] text-on-surface-variant/50">
                          {c.coefficient} {c.unit} × {c.base_price.toLocaleString("id-ID")}
                        </span>
                      </div>
                      <span className="font-mono text-[10px] text-on-surface-variant whitespace-nowrap">
                        {formatIDR(c.subtotal)}
                      </span>
                    </div>
                  );
                })}
                <div className="flex items-center justify-between px-2 py-2 mt-1 border-t border-primary/20">
                  <span className="font-mono text-[10px] text-primary uppercase font-semibold">
                    Harga Satuan
                  </span>
                  <span className="font-mono text-xs text-secondary font-bold">
                    {formatIDR(ahspDetail.unit_price)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
