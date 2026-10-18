"use client";

import React, { useState, useEffect } from "react";
import { ProgressSummary, ProgressPoint, Project } from "@/lib/types";
import { fetchProjects, fetchProgress, createProgressEntry } from "@/lib/api";
import { downloadReport } from "@/lib/reports";
import { TrendingUp, Plus, RefreshCw, Activity, Download } from "lucide-react";

const formatIDR = (val: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val);

const formatPct = (val: number) => `${val.toFixed(2)}%`;

const formatIndex = (val: number) => val.toFixed(3);

// --- S-Curve (inline SVG, no external chart dependency) ---

function SCurveChart({ periods }: { periods: ProgressPoint[] }) {
  const W = 720;
  const H = 260;
  const padL = 44;
  const padR = 16;
  const padT = 16;
  const padB = 34;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;

  const n = periods.length;
  const xAt = (i: number) => (n <= 1 ? padL + innerW / 2 : padL + (i / (n - 1)) * innerW);
  const yAt = (pct: number) => padT + (1 - Math.max(0, Math.min(100, pct)) / 100) * innerH;

  const toPoly = (key: "planned_pct" | "actual_pct") =>
    periods.map((p, i) => `${xAt(i)},${yAt(p[key])}`).join(" ");

  const gridLines = [0, 25, 50, 75, 100];

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-full" preserveAspectRatio="none">
      {/* Grid + Y labels */}
      {gridLines.map((g) => (
        <g key={g}>
          <line
            x1={padL}
            y1={yAt(g)}
            x2={W - padR}
            y2={yAt(g)}
            stroke="#2a2a2d"
            strokeWidth={1}
          />
          <text
            x={padL - 8}
            y={yAt(g) + 3}
            textAnchor="end"
            className="fill-current text-on-surface-variant/50"
            style={{ fontSize: 9, fontFamily: "JetBrains Mono, monospace" }}
          >
            {g}
          </text>
        </g>
      ))}

      {/* X labels */}
      {periods.map((p, i) => (
        <text
          key={`${p.period}-${i}`}
          x={xAt(i)}
          y={H - padB + 16}
          textAnchor="middle"
          className="fill-current text-on-surface-variant/50"
          style={{ fontSize: 9, fontFamily: "JetBrains Mono, monospace" }}
        >
          {p.period}
        </text>
      ))}

      {/* Planned curve (amber) */}
      {n > 1 && (
        <polyline
          points={toPoly("planned_pct")}
          fill="none"
          stroke="#ffc174"
          strokeWidth={2}
          strokeDasharray="5 4"
        />
      )}

      {/* Actual curve (emerald) */}
      {n > 1 && (
        <polyline points={toPoly("actual_pct")} fill="none" stroke="#4edea3" strokeWidth={2} />
      )}

      {/* Data points */}
      {periods.map((p, i) => (
        <g key={`pts-${i}`}>
          <circle cx={xAt(i)} cy={yAt(p.planned_pct)} r={3} fill="#ffc174" />
          <circle cx={xAt(i)} cy={yAt(p.actual_pct)} r={3} fill="#4edea3" />
        </g>
      ))}
    </svg>
  );
}

interface EvmCardProps {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "good" | "bad";
}

function EvmCard({ label, value, hint, tone = "default" }: EvmCardProps) {
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

export default function ProgressPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<number | null>(null);
  const [summary, setSummary] = useState<ProgressSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  // Entry form state
  const [period, setPeriod] = useState("");
  const [plannedPct, setPlannedPct] = useState("");
  const [actualPct, setActualPct] = useState("");
  const [actualCost, setActualCost] = useState("");
  const [note, setNote] = useState("");

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

  const loadProgress = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProgress(id);
      setSummary(data);
    } catch (err) {
      console.error(err);
      setSummary(null);
      setError(err instanceof Error ? err.message : "Gagal memuat data progress.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId != null) loadProgress(projectId);
  }, [projectId]);

  const handleDownloadEvm = async () => {
    if (projectId == null) return;
    setDownloading(true);
    setDownloadError(null);
    try {
      await downloadReport(projectId, "evm", "xlsx");
    } catch (err) {
      setDownloadError(err instanceof Error ? err.message : "Gagal mengunduh laporan EVM.");
    } finally {
      setDownloading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (projectId == null) return;
    setSaving(true);
    try {
      await createProgressEntry(projectId, {
        period,
        planned_pct: Number(plannedPct) || 0,
        actual_pct: Number(actualPct) || 0,
        actual_cost: Number(actualCost) || 0,
        note: note || undefined,
      });
      setPeriod("");
      setPlannedPct("");
      setActualPct("");
      setActualCost("");
      setNote("");
      await loadProgress(projectId);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal menyimpan entri progress.");
    } finally {
      setSaving(false);
    }
  };

  const spiTone = summary ? (summary.spi >= 1 ? "good" : "bad") : "default";
  const cpiTone = summary ? (summary.cpi >= 1 ? "good" : "bad") : "default";
  const svTone = summary ? (summary.sv >= 0 ? "good" : "bad") : "default";
  const cvTone = summary ? (summary.cv >= 0 ? "good" : "bad") : "default";
  const vacTone = summary ? (summary.vac >= 0 ? "good" : "bad") : "default";

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                Progress &amp; EVM
              </span>
              <h1 className="text-sm font-semibold text-on-surface">
                {summary ? summary.project_name : "Kurva-S & Earned Value"}
              </h1>
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
              onClick={handleDownloadEvm}
              disabled={downloading || projectId == null}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-medium transition-colors border border-primary/30 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloading ? "Menyiapkan…" : "Unduh EVM (Excel)"}</span>
            </button>

            {summary && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-secondary/10 border border-secondary/20">
                <Activity className="w-3.5 h-3.5 text-secondary" />
                <span className="font-mono text-xs text-secondary font-bold">
                  {formatPct(summary.progress_pct)}
                </span>
              </div>
            )}

            <button
              onClick={() => projectId != null && loadProgress(projectId)}
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

        {/* EVM Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
          <EvmCard label="BAC" value={summary ? formatIDR(summary.bac) : "-"} hint="Budget at Completion" />
          <EvmCard label="PV" value={summary ? formatIDR(summary.pv) : "-"} hint="Planned Value" />
          <EvmCard label="EV" value={summary ? formatIDR(summary.ev) : "-"} hint="Earned Value" />
          <EvmCard label="AC" value={summary ? formatIDR(summary.ac) : "-"} hint="Actual Cost" />
          <EvmCard
            label="SV"
            value={summary ? formatIDR(summary.sv) : "-"}
            hint="Schedule Variance"
            tone={svTone}
          />
          <EvmCard
            label="CV"
            value={summary ? formatIDR(summary.cv) : "-"}
            hint="Cost Variance"
            tone={cvTone}
          />
          <EvmCard
            label="SPI"
            value={summary ? formatIndex(summary.spi) : "-"}
            hint="Schedule Perf. Index"
            tone={spiTone}
          />
          <EvmCard
            label="CPI"
            value={summary ? formatIndex(summary.cpi) : "-"}
            hint="Cost Perf. Index"
            tone={cpiTone}
          />
          <EvmCard label="EAC" value={summary ? formatIDR(summary.eac) : "-"} hint="Estimate at Completion" />
          <EvmCard
            label="VAC"
            value={summary ? formatIDR(summary.vac) : "-"}
            hint="Variance at Completion"
            tone={vacTone}
          />
        </div>

        {/* S-Curve */}
        <div className="bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
            <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
              Kurva-S — Rencana vs Aktual (Kumulatif %)
            </span>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-primary" />
                <span className="font-mono text-[9px] text-on-surface-variant/60">Rencana</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-secondary" />
                <span className="font-mono text-[9px] text-on-surface-variant/60">Aktual</span>
              </span>
            </div>
          </div>
          <div className="p-3 h-[280px]">
            {summary && summary.periods.length > 0 ? (
              <SCurveChart periods={summary.periods} />
            ) : (
              <div className="h-full flex items-center justify-center text-xs font-mono text-on-surface-variant/40">
                {loading ? "Memuat data..." : "Belum ada periode progress."}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-3">
          {/* Period Table */}
          <div className="xl:col-span-2 bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Rincian Periode
              </span>
              <span className="font-mono text-[10px] text-on-surface-variant">
                {summary ? `${summary.periods.length} periode` : "-"}
              </span>
            </div>
            <div className="overflow-auto max-h-[420px]">
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-surface-container z-10">
                  <tr className="text-left text-on-surface-variant/70 font-mono text-[10px] uppercase">
                    <th className="px-3 py-2 font-medium">Periode</th>
                    <th className="px-3 py-2 font-medium text-right">Rencana %</th>
                    <th className="px-3 py-2 font-medium text-right">Aktual %</th>
                    <th className="px-3 py-2 font-medium text-right">Planned Value</th>
                    <th className="px-3 py-2 font-medium text-right">Earned Value</th>
                    <th className="px-3 py-2 font-medium text-right">Actual Cost</th>
                  </tr>
                </thead>
                <tbody className="font-mono">
                  {summary?.periods.map((p, i) => (
                    <tr
                      key={`${p.period}-${i}`}
                      className="border-t border-surface-container-high/40 hover:bg-surface-container/50"
                    >
                      <td className="px-3 py-2 text-primary">{p.period}</td>
                      <td className="px-3 py-2 text-right text-on-surface-variant">
                        {formatPct(p.planned_pct)}
                      </td>
                      <td className="px-3 py-2 text-right text-secondary font-semibold">
                        {formatPct(p.actual_pct)}
                      </td>
                      <td className="px-3 py-2 text-right text-on-surface-variant">
                        {formatIDR(p.planned_value)}
                      </td>
                      <td className="px-3 py-2 text-right text-on-surface">
                        {formatIDR(p.earned_value)}
                      </td>
                      <td className="px-3 py-2 text-right text-on-surface">
                        {formatIDR(p.actual_cost)}
                      </td>
                    </tr>
                  ))}
                  {(!summary || summary.periods.length === 0) && (
                    <tr>
                      <td colSpan={6} className="px-3 py-8 text-center text-on-surface-variant/50 font-sans">
                        Belum ada data periode. Tambahkan entri progress untuk memulai.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Entry Form */}
          <div className="bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center gap-2">
              <Plus className="w-4 h-4 text-primary" />
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Tambah / Perbarui Entri
              </span>
            </div>
            <form onSubmit={handleSubmit} className="p-3 space-y-3">
              <div className="flex flex-col gap-1">
                <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                  Periode
                </label>
                <input
                  required
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  placeholder="2026-01 atau Minggu-1"
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Rencana %
                  </label>
                  <input
                    required
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={plannedPct}
                    onChange={(e) => setPlannedPct(e.target.value)}
                    placeholder="0"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                    Aktual %
                  </label>
                  <input
                    required
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={actualPct}
                    onChange={(e) => setActualPct(e.target.value)}
                    placeholder="0"
                    className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-mono text-[10px] text-on-surface-variant/60 uppercase tracking-wider">
                  Actual Cost (IDR)
                </label>
                <input
                  required
                  type="number"
                  step="1"
                  min="0"
                  value={actualCost}
                  onChange={(e) => setActualCost(e.target.value)}
                  placeholder="0"
                  className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
                />
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

              <button
                type="submit"
                disabled={saving || projectId == null}
                className="w-full px-3 py-2 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-semibold font-mono border border-primary/30 transition-colors disabled:opacity-50"
              >
                {saving ? "Menyimpan..." : "Simpan Entri"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
