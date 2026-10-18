"use client";

import React, { useState, useEffect } from "react";
import {
  Inspection,
  InspectionCategory,
  InspectionStatus,
  CheckResult,
  QCSummary,
  Project,
} from "@/lib/types";
import {
  fetchProjects,
  fetchInspections,
  createInspection,
  updateInspectionItem,
  fetchQCSummary,
} from "@/lib/api";
import { downloadReport } from "@/lib/reports";
import {
  ClipboardCheck,
  Plus,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Trash2,
  Download,
} from "lucide-react";

const formatPct = (val: number) => `${val.toFixed(1)}%`;

const CATEGORY_META: Record<InspectionCategory, string> = {
  concrete: "Beton",
  rebar: "Pembesian",
  formwork: "Bekisting",
  other: "Lainnya",
};

const CATEGORY_OPTIONS: InspectionCategory[] = ["concrete", "rebar", "formwork", "other"];

const INSPECTION_STATUS_META: Record<InspectionStatus, { label: string; className: string }> = {
  draft: {
    label: "Draft",
    className: "bg-surface-container-high/60 text-on-surface-variant border-outline-variant/40",
  },
  passed: { label: "Lulus", className: "bg-secondary/10 text-secondary border-secondary/30" },
  failed: { label: "Gagal", className: "bg-error-container/30 text-error border-error/30" },
};

const RESULT_OPTIONS: CheckResult[] = ["ok", "not_ok", "na"];

const RESULT_META: Record<CheckResult, { label: string; className: string }> = {
  ok: { label: "OK", className: "bg-secondary/10 text-secondary border-secondary/30" },
  not_ok: { label: "Tidak OK", className: "bg-error-container/30 text-error border-error/30" },
  na: {
    label: "N/A",
    className: "bg-surface-container-high/60 text-on-surface-variant border-outline-variant/40",
  },
};

function StatusBadge({ label, className }: { label: string; className: string }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded border font-mono text-[9px] uppercase tracking-wider ${className}`}
    >
      {label}
    </span>
  );
}

interface SummaryCardProps {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "good" | "bad";
}

function SummaryCard({ label, value, hint, tone = "default" }: SummaryCardProps) {
  const valueColor =
    tone === "good" ? "text-secondary" : tone === "bad" ? "text-error" : "text-on-surface";
  return (
    <div className="flex flex-col gap-1 px-3 py-2.5 rounded-lg bg-surface-container-low border border-surface-container-high/50">
      <span className="font-mono text-[9px] text-on-surface-variant/60 tracking-widest uppercase">
        {label}
      </span>
      <span className={`font-mono text-sm font-semibold ${valueColor}`}>{value}</span>
      {hint && (
        <span className="font-mono text-[9px] text-on-surface-variant/40 truncate">{hint}</span>
      )}
    </div>
  );
}

interface ChecklistRow {
  description: string;
  standard: string;
}

const DEFAULT_CHECKLIST: ChecklistRow[] = [
  { description: "Dimensi sesuai gambar", standard: "Toleransi ±10 mm" },
  { description: "Selimut beton", standard: "SNI 2847 — sesuai rencana" },
  { description: "Slump test", standard: "12 ± 2 cm" },
];

export default function QCPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<number | null>(null);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [summary, setSummary] = useState<QCSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [updatingItemId, setUpdatingItemId] = useState<number | null>(null);

  // Create form state
  const [inspectionNumber, setInspectionNumber] = useState("");
  const [title, setTitle] = useState("");
  const [location, setLocation] = useState("");
  const [category, setCategory] = useState<InspectionCategory>("concrete");
  const [inspector, setInspector] = useState("");
  const [note, setNote] = useState("");
  const [checklist, setChecklist] = useState<ChecklistRow[]>(DEFAULT_CHECKLIST);

  useEffect(() => {
    (async () => {
      try {
        const list: Project[] = await fetchProjects();
        setProjects(list || []);
        if (list && list.length > 0) setProjectId(list[0].id);
      } catch (err) {
        console.error("Gagal memuat daftar proyek:", err);
        setError("Gagal memuat daftar proyek.");
      }
    })();
  }, []);

  const loadData = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const [inspectionData, summaryData] = await Promise.all([
        fetchInspections(id),
        fetchQCSummary(id),
      ]);
      setInspections(inspectionData || []);
      setSummary(summaryData);
    } catch (err) {
      console.error(err);
      setInspections([]);
      setSummary(null);
      setError(err instanceof Error ? err.message : "Gagal memuat data QC.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId != null) loadData(projectId);
  }, [projectId]);

  const handleDownloadQc = async () => {
    if (projectId == null) return;
    setDownloading(true);
    setDownloadError(null);
    try {
      await downloadReport(projectId, "qc", "xlsx");
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : "Gagal mengunduh laporan QC.");
    } finally {
      setDownloading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (projectId == null) return;
    const validItems = checklist.filter((c) => c.description.trim());
    if (validItems.length === 0) {
      alert("Tambahkan minimal satu baris checklist.");
      return;
    }
    setSaving(true);
    try {
      await createInspection(projectId, {
        inspection_number: inspectionNumber,
        title,
        location: location || undefined,
        category,
        inspector: inspector || undefined,
        note: note || undefined,
        items: validItems.map((c) => ({
          description: c.description.trim(),
          standard: c.standard.trim() || undefined,
          result: "na" as CheckResult,
        })),
      });
      setInspectionNumber("");
      setTitle("");
      setLocation("");
      setCategory("concrete");
      setInspector("");
      setNote("");
      setChecklist(DEFAULT_CHECKLIST);
      await loadData(projectId);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal membuat inspeksi.");
    } finally {
      setSaving(false);
    }
  };

  const handleResultChange = async (itemId: number, result: CheckResult) => {
    setUpdatingItemId(itemId);
    try {
      const updated = await updateInspectionItem(itemId, { result });
      setInspections((prev) =>
        prev.map((insp) => ({
          ...insp,
          items: insp.items.map((it) => (it.id === itemId ? { ...it, ...updated } : it)),
        })),
      );
      if (projectId != null) {
        const summaryData = await fetchQCSummary(projectId);
        setSummary(summaryData);
      }
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal memperbarui item inspeksi.");
    } finally {
      setUpdatingItemId(null);
    }
  };

  const updateChecklistRow = (index: number, patch: Partial<ChecklistRow>) => {
    setChecklist((prev) => prev.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };

  const addChecklistRow = () => {
    setChecklist((prev) => [...prev, { description: "", standard: "" }]);
  };

  const removeChecklistRow = (index: number) => {
    setChecklist((prev) => prev.filter((_, i) => i !== index));
  };

  const passRateTone = summary
    ? summary.pass_rate >= 80
      ? "good"
      : summary.pass_rate >= 50
        ? "default"
        : "bad"
    : "default";

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <ClipboardCheck className="w-5 h-5 text-primary" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                QC / Mutu
              </span>
              <h1 className="text-sm font-semibold text-on-surface">Inspeksi Mutu &amp; Checklist</h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={projectId ?? ""}
              onChange={(e) => setProjectId(Number(e.target.value))}
              className="px-2.5 py-1.5 rounded bg-surface-container-low border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
            >
              {projects.length === 0 && <option value="">Tidak ada proyek</option>}
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>

            <button
              onClick={handleDownloadQc}
              disabled={downloading || projectId == null}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-medium transition-colors border border-primary/30 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloading ? "Menyiapkan…" : "Unduh QC (Excel)"}</span>
            </button>

            {summary && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-secondary/10 border border-secondary/20">
                <span className="font-mono text-[10px] text-secondary">Pass Rate</span>
                <span className="font-mono text-xs text-secondary font-bold">
                  {formatPct(summary.pass_rate)}
                </span>
              </div>
            )}

            <button
              onClick={() => projectId != null && loadData(projectId)}
              disabled={loading || projectId == null}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-medium transition-colors border border-outline-variant/40 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-primary ${loading ? "animate-spin" : ""}`} />
              <span>Muat Ulang</span>
            </button>
          </div>
        </div>
      </header>

      {/* Workspace */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {error && (
          <div className="px-4 py-2 rounded-lg bg-error-container/30 border border-error/30 text-error text-xs font-mono">
            {error}
          </div>
        )}

        {downloadError && (
          <div className="px-4 py-2 rounded-lg bg-error-container/30 border border-error/30 text-error text-xs font-mono">
            {downloadError}
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
          <SummaryCard
            label="Total Inspeksi"
            value={summary ? String(summary.total) : "-"}
            hint="Semua status"
          />
          <SummaryCard
            label="Lulus"
            value={summary ? String(summary.passed) : "-"}
            hint="passed"
            tone="good"
          />
          <SummaryCard
            label="Gagal"
            value={summary ? String(summary.failed) : "-"}
            hint="failed"
            tone="bad"
          />
          <SummaryCard label="Draft" value={summary ? String(summary.draft) : "-"} hint="draft" />
          <SummaryCard
            label="Pass Rate"
            value={summary ? formatPct(summary.pass_rate) : "-"}
            hint={summary ? `${summary.not_ok_items} item tidak OK` : "Belum ada data"}
            tone={passRateTone}
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-3">
          {/* Inspection List */}
          <div className="xl:col-span-2 bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Daftar Inspeksi
              </span>
              <span className="font-mono text-[10px] text-on-surface-variant">
                {inspections.length} inspeksi
              </span>
            </div>

            <div className="overflow-auto max-h-[560px]">
              {inspections.map((insp) => {
                const statusMeta =
                  INSPECTION_STATUS_META[insp.status] || INSPECTION_STATUS_META.draft;
                const isExpanded = expandedId === insp.id;
                const notOkCount = insp.items.filter((it) => it.result === "not_ok").length;
                return (
                  <div
                    key={insp.id}
                    className="border-b border-surface-container-high/40 last:border-b-0"
                  >
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : insp.id)}
                      className="w-full flex items-center gap-2 px-3 py-2.5 text-left hover:bg-surface-container/50 transition-colors"
                    >
                      {isExpanded ? (
                        <ChevronDown className="w-3.5 h-3.5 text-primary shrink-0" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-on-surface-variant/60 shrink-0" />
                      )}
                      <div className="flex flex-col min-w-0 flex-1">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="font-mono text-[10px] text-primary shrink-0">
                            {insp.inspection_number}
                          </span>
                          <span className="text-xs text-on-surface font-medium truncate" title={insp.title}>
                            {insp.title}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="font-mono text-[9px] text-on-surface-variant/50 uppercase">
                            {CATEGORY_META[insp.category] || insp.category}
                          </span>
                          {insp.location && (
                            <span className="font-mono text-[9px] text-on-surface-variant/40 truncate">
                              · {insp.location}
                            </span>
                          )}
                          <span className="font-mono text-[9px] text-on-surface-variant/40">
                            · {insp.items.length} item
                            {notOkCount > 0 ? ` (${notOkCount} tidak OK)` : ""}
                          </span>
                        </div>
                      </div>
                      <StatusBadge label={statusMeta.label} className={statusMeta.className} />
                    </button>

                    {isExpanded && (
                      <div className="px-3 pb-3 pl-9 space-y-1.5">
                        {insp.items.map((item) => {
                          const resultMeta = RESULT_META[item.result] || RESULT_META.na;
                          return (
                            <div
                              key={item.id}
                              className="flex items-start gap-2 px-2.5 py-2 rounded bg-surface-container border border-surface-container-high/50"
                            >
                              <div className="flex flex-col min-w-0 flex-1">
                                <span className="text-[11px] text-on-surface">{item.description}</span>
                                {item.standard && (
                                  <span className="font-mono text-[9px] text-on-surface-variant/50">
                                    Standar: {item.standard}
                                  </span>
                                )}
                              </div>
                              <StatusBadge label={resultMeta.label} className={resultMeta.className} />
                              <select
                                value={item.result}
                                disabled={updatingItemId === item.id}
                                onChange={(e) =>
                                  handleResultChange(item.id, e.target.value as CheckResult)
                                }
                                className="px-2 py-1 rounded bg-surface-container-low border border-surface-container-high text-[10px] text-on-surface focus:outline-none focus:border-primary/50 disabled:opacity-50"
                              >
                                {RESULT_OPTIONS.map((r) => (
                                  <option key={r} value={r}>
                                    {RESULT_META[r].label}
                                  </option>
                                ))}
                              </select>
                            </div>
                          );
                        })}
                        {insp.items.length === 0 && (
                          <p className="text-[11px] text-on-surface-variant/50 font-sans">
                            Tidak ada item checklist.
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
              {inspections.length === 0 && (
                <p className="text-xs text-on-surface-variant/50 text-center py-8 font-sans">
                  {loading ? "Memuat data..." : "Belum ada inspeksi. Buat inspeksi baru untuk memulai."}
                </p>
              )}
            </div>
          </div>

          {/* Create Form */}
          <div className="bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center gap-2">
              <Plus className="w-4 h-4 text-primary" />
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Buat Inspeksi Baru
              </span>
            </div>
            <form onSubmit={handleSubmit} className="p-3 space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    No. Inspeksi
                  </label>
                  <input
                    required
                    value={inspectionNumber}
                    onChange={(e) => setInspectionNumber(e.target.value)}
                    placeholder="QC-001"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Kategori
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as InspectionCategory)}
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  >
                    {CATEGORY_OPTIONS.map((c) => (
                      <option key={c} value={c}>
                        {CATEGORY_META[c]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                  Judul
                </label>
                <input
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Pengecoran Kolom K1 Lantai 3"
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Lokasi (opsional)
                  </label>
                  <input
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="Zona A - Grid 4"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Inspektor (opsional)
                  </label>
                  <input
                    value={inspector}
                    onChange={(e) => setInspector(e.target.value)}
                    placeholder="Nama pengawas"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                  Catatan (opsional)
                </label>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  rows={2}
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50 resize-none"
                />
              </div>

              {/* Checklist rows */}
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Checklist
                  </label>
                  <button
                    type="button"
                    onClick={addChecklistRow}
                    className="flex items-center gap-1 font-mono text-[10px] text-primary hover:text-primary/80 transition-colors"
                  >
                    <Plus className="w-3 h-3" />
                    Baris
                  </button>
                </div>
                {checklist.map((row, i) => (
                  <div key={i} className="flex flex-col gap-1 px-2 py-1.5 rounded bg-surface-container border border-surface-container-high/50">
                    <div className="flex items-center gap-1.5">
                      <input
                        value={row.description}
                        onChange={(e) => updateChecklistRow(i, { description: e.target.value })}
                        placeholder="Deskripsi item"
                        className="flex-1 px-2 py-1 rounded bg-surface-container-low border border-surface-container-high text-[11px] text-on-surface focus:outline-none focus:border-primary/50"
                      />
                      <button
                        type="button"
                        onClick={() => removeChecklistRow(i)}
                        className="p-1 rounded text-on-surface-variant/50 hover:text-error hover:bg-error-container/20 transition-colors"
                        aria-label="Hapus baris"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                    <input
                      value={row.standard}
                      onChange={(e) => updateChecklistRow(i, { standard: e.target.value })}
                      placeholder="Standar / toleransi (opsional)"
                      className="w-full px-2 py-1 rounded bg-surface-container-low border border-surface-container-high text-[10px] text-on-surface-variant focus:outline-none focus:border-primary/50"
                    />
                  </div>
                ))}
              </div>

              <button
                type="submit"
                disabled={saving || projectId == null}
                className="w-full px-3 py-2 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-semibold font-mono border border-primary/30 transition-colors disabled:opacity-50"
              >
                {saving ? "Menyimpan..." : "Simpan Inspeksi"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
