"use client";

import React, { useState, useEffect } from "react";
import {
  SafetyReport,
  SafetyCategory,
  SafetyStatus,
  Severity,
  SafetySummary,
  Project,
} from "@/lib/types";
import {
  fetchProjects,
  fetchSafetyReports,
  createSafetyReport,
  updateSafetyReportStatus,
  fetchSafetySummary,
} from "@/lib/api";
import { ShieldAlert, Plus, RefreshCw } from "lucide-react";

const CATEGORY_META: Record<SafetyCategory, string> = {
  incident: "Insiden",
  near_miss: "Hampir Celaka",
  unsafe_act: "Tindakan Tidak Aman",
  unsafe_condition: "Kondisi Tidak Aman",
};

const CATEGORY_OPTIONS: SafetyCategory[] = [
  "incident",
  "near_miss",
  "unsafe_act",
  "unsafe_condition",
];

const SEVERITY_META: Record<Severity, { label: string; className: string }> = {
  low: {
    label: "Rendah",
    className: "bg-surface-container-high/60 text-on-surface-variant border-outline-variant/40",
  },
  medium: { label: "Sedang", className: "bg-primary/10 text-primary border-primary/30" },
  high: { label: "Tinggi", className: "bg-error-container/20 text-error border-error/20" },
  critical: { label: "Kritis", className: "bg-error-container/40 text-error border-error/40" },
};

const SEVERITY_OPTIONS: Severity[] = ["low", "medium", "high", "critical"];

const STATUS_META: Record<SafetyStatus, { label: string; className: string }> = {
  open: { label: "Terbuka", className: "bg-error-container/30 text-error border-error/30" },
  investigating: { label: "Investigasi", className: "bg-primary/10 text-primary border-primary/30" },
  closed: {
    label: "Tutup",
    className: "bg-secondary/10 text-secondary border-secondary/30",
  },
};

const STATUS_OPTIONS: SafetyStatus[] = ["open", "investigating", "closed"];

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

export default function K3Page() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<number | null>(null);
  const [reports, setReports] = useState<SafetyReport[]>([]);
  const [summary, setSummary] = useState<SafetySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  // Create form state
  const [reportNumber, setReportNumber] = useState("");
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<SafetyCategory>("incident");
  const [severity, setSeverity] = useState<Severity>("low");
  const [description, setDescription] = useState("");
  const [actionTaken, setActionTaken] = useState("");
  const [reportedBy, setReportedBy] = useState("");

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
      const [reportData, summaryData] = await Promise.all([
        fetchSafetyReports(id),
        fetchSafetySummary(id),
      ]);
      setReports(reportData || []);
      setSummary(summaryData);
    } catch (err) {
      console.error(err);
      setReports([]);
      setSummary(null);
      setError(err instanceof Error ? err.message : "Gagal memuat data K3.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId != null) loadData(projectId);
  }, [projectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (projectId == null) return;
    setSaving(true);
    try {
      await createSafetyReport(projectId, {
        report_number: reportNumber,
        title,
        category,
        severity,
        description,
        action_taken: actionTaken || undefined,
        reported_by: reportedBy || undefined,
      });
      setReportNumber("");
      setTitle("");
      setCategory("incident");
      setSeverity("low");
      setDescription("");
      setActionTaken("");
      setReportedBy("");
      await loadData(projectId);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal membuat laporan K3.");
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (reportId: number, status: SafetyStatus) => {
    if (projectId == null) return;
    setUpdatingId(reportId);
    try {
      const updated = await updateSafetyReportStatus(reportId, status);
      setReports((prev) => prev.map((r) => (r.id === reportId ? { ...r, ...updated } : r)));
      const summaryData = await fetchSafetySummary(projectId);
      setSummary(summaryData);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal memperbarui status laporan K3.");
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-primary" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                K3 / Safety
              </span>
              <h1 className="text-sm font-semibold text-on-surface">Laporan Keselamatan Kerja</h1>
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

            {summary && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-error-container/30 border border-error/30">
                <span className="font-mono text-[10px] text-error">Terbuka</span>
                <span className="font-mono text-xs text-error font-bold">{summary.open}</span>
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

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-2">
          <SummaryCard
            label="Total Laporan"
            value={summary ? String(summary.total) : "-"}
            hint="Semua status"
          />
          <SummaryCard
            label="Terbuka"
            value={summary ? String(summary.open) : "-"}
            hint="open"
            tone="bad"
          />
          <SummaryCard
            label="Investigasi"
            value={summary ? String(summary.investigating) : "-"}
            hint="investigating"
          />
          <SummaryCard
            label="Tutup"
            value={summary ? String(summary.closed) : "-"}
            hint="closed"
            tone="good"
          />
          <SummaryCard
            label="Rendah"
            value={summary ? String(summary.by_severity.low) : "-"}
            hint="low"
          />
          <SummaryCard
            label="Sedang"
            value={summary ? String(summary.by_severity.medium) : "-"}
            hint="medium"
          />
          <SummaryCard
            label="Tinggi/Kritis"
            value={
              summary ? String(summary.by_severity.high + summary.by_severity.critical) : "-"
            }
            hint={summary ? `Tinggi ${summary.by_severity.high} · Kritis ${summary.by_severity.critical}` : "high + critical"}
            tone="bad"
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-3">
          {/* Reports Table */}
          <div className="xl:col-span-2 bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Daftar Laporan K3
              </span>
              <span className="font-mono text-[10px] text-on-surface-variant">
                {reports.length} laporan
              </span>
            </div>

            <div className="overflow-auto max-h-[560px]">
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-surface-container z-10">
                  <tr className="text-left text-on-surface-variant/70 font-mono text-[10px] uppercase">
                    <th className="px-3 py-2 font-medium">No. Laporan</th>
                    <th className="px-3 py-2 font-medium">Judul / Kategori</th>
                    <th className="px-3 py-2 font-medium">Severity</th>
                    <th className="px-3 py-2 font-medium">Status</th>
                    <th className="px-3 py-2 font-medium">Ubah Status</th>
                  </tr>
                </thead>
                <tbody className="font-mono">
                  {reports.map((report) => {
                    const sevMeta = SEVERITY_META[report.severity] || SEVERITY_META.low;
                    const statusMeta = STATUS_META[report.status] || STATUS_META.open;
                    return (
                      <tr
                        key={report.id}
                        className="border-t border-surface-container-high/40 hover:bg-surface-container/50 align-top"
                      >
                        <td className="px-3 py-2 text-primary whitespace-nowrap">
                          {report.report_number}
                        </td>
                        <td className="px-3 py-2 text-on-surface font-sans max-w-[260px]">
                          <div className="truncate" title={report.title}>
                            {report.title}
                          </div>
                          <div className="text-[10px] text-on-surface-variant/50 truncate">
                            {CATEGORY_META[report.category] || report.category}
                            {report.reported_by ? ` · ${report.reported_by}` : ""}
                          </div>
                        </td>
                        <td className="px-3 py-2">
                          <StatusBadge label={sevMeta.label} className={sevMeta.className} />
                        </td>
                        <td className="px-3 py-2">
                          <StatusBadge label={statusMeta.label} className={statusMeta.className} />
                        </td>
                        <td className="px-3 py-2">
                          <select
                            value={report.status}
                            disabled={updatingId === report.id}
                            onChange={(e) =>
                              handleStatusChange(report.id, e.target.value as SafetyStatus)
                            }
                            className="px-2 py-1 rounded bg-surface-container border border-surface-container-high text-[10px] text-on-surface focus:outline-none focus:border-primary/50 disabled:opacity-50"
                          >
                            {STATUS_OPTIONS.map((s) => (
                              <option key={s} value={s}>
                                {STATUS_META[s].label}
                              </option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    );
                  })}
                  {reports.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-3 py-8 text-center text-on-surface-variant/50 font-sans">
                        {loading ? "Memuat data..." : "Belum ada laporan K3."}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Create Form */}
          <div className="bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center gap-2">
              <Plus className="w-4 h-4 text-primary" />
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Buat Laporan Baru
              </span>
            </div>
            <form onSubmit={handleSubmit} className="p-3 space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    No. Laporan
                  </label>
                  <input
                    required
                    value={reportNumber}
                    onChange={(e) => setReportNumber(e.target.value)}
                    placeholder="K3-001"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Kategori
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as SafetyCategory)}
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
                  placeholder="Pekerja tanpa helm di area tower crane"
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Severity
                  </label>
                  <select
                    value={severity}
                    onChange={(e) => setSeverity(e.target.value as Severity)}
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  >
                    {SEVERITY_OPTIONS.map((s) => (
                      <option key={s} value={s}>
                        {SEVERITY_META[s].label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Pelapor (opsional)
                  </label>
                  <input
                    value={reportedBy}
                    onChange={(e) => setReportedBy(e.target.value)}
                    placeholder="Nama pelapor"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                  Deskripsi
                </label>
                <textarea
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Uraian kejadian / temuan..."
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50 resize-none"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                  Tindakan (opsional)
                </label>
                <textarea
                  value={actionTaken}
                  onChange={(e) => setActionTaken(e.target.value)}
                  rows={2}
                  placeholder="Tindakan perbaikan yang diambil..."
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50 resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={saving || projectId == null}
                className="w-full px-3 py-2 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-semibold font-mono border border-primary/30 transition-colors disabled:opacity-50"
              >
                {saving ? "Menyimpan..." : "Simpan Laporan"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
