"use client";

import React, { useState } from "react";
import { enqueueAnalysisJob } from "@/lib/api";
import { useJobPolling } from "@/hooks/useJobPolling";
import type { JobStatus } from "@/lib/types";
import { Play, Loader2, CheckCircle2, XCircle, Clock, AlertCircle } from "lucide-react";

interface AsyncAnalysisButtonProps {
  projectId: number;
  drawingRefId: number;
  drawingRevId: number;
  /** Dipanggil saat job sukses agar halaman memuat ulang hasil analisis. */
  onComplete?: () => void;
}

const STATUS_META: Record<JobStatus, { label: string; className: string; icon: React.ReactNode }> = {
  pending: {
    label: "Dalam antrean",
    className: "text-on-surface-variant border-surface-container-high",
    icon: <Clock className="w-3.5 h-3.5" />,
  },
  running: {
    label: "Diproses",
    className: "text-primary border-primary/30",
    icon: <Loader2 className="w-3.5 h-3.5 animate-spin" />,
  },
  success: {
    label: "Selesai",
    className: "text-secondary border-secondary/30",
    icon: <CheckCircle2 className="w-3.5 h-3.5" />,
  },
  failed: {
    label: "Gagal",
    className: "text-error border-error/30",
    icon: <XCircle className="w-3.5 h-3.5" />,
  },
};

export function AsyncAnalysisButton({
  projectId,
  drawingRefId,
  drawingRevId,
  onComplete,
}: AsyncAnalysisButtonProps) {
  const [enqueueError, setEnqueueError] = useState<string | null>(null);
  const [enqueuing, setEnqueuing] = useState(false);

  const { job, polling, error, start } = useJobPolling({
    intervalMs: 2000,
    onSuccess: () => onComplete?.(),
  });

  const handleRun = async () => {
    setEnqueueError(null);
    setEnqueuing(true);
    try {
      const res = await enqueueAnalysisJob({
        project_id: projectId,
        drawing_ref_id: drawingRefId,
        drawing_rev_id: drawingRevId,
      });
      start(res.job_id);
    } catch (e) {
      setEnqueueError(e instanceof Error ? e.message : "Gagal memulai analisis.");
    } finally {
      setEnqueuing(false);
    }
  };

  const busy = enqueuing || polling;
  const meta = job ? STATUS_META[job.status] : null;
  const message = enqueueError || error;

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleRun}
        disabled={busy}
        className="flex items-center gap-1.5 rounded border border-primary/30 bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-primary/20 disabled:opacity-50"
        title="Jalankan analisis gambar di latar belakang"
      >
        {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
        {busy ? "Memproses…" : "Analisis Async"}
      </button>

      {meta && (
        <span
          className={`flex items-center gap-1.5 rounded border bg-surface-container-low px-2.5 py-1 font-mono text-[10px] ${meta.className}`}
        >
          {meta.icon}
          Job #{job?.id} · {meta.label}
        </span>
      )}

      {message && (
        <span className="flex items-center gap-1 text-[10px] text-error">
          <AlertCircle className="w-3 h-3" />
          {message}
        </span>
      )}
    </div>
  );
}
