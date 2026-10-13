"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Job, JobStatus } from "@/lib/types";
import { fetchJob } from "@/lib/api";

const TERMINAL_STATUSES: JobStatus[] = ["success", "failed"];

interface UseJobPollingOptions {
  /** Jeda antar polling (ms). Default 2000. */
  intervalMs?: number;
  onSuccess?: (job: Job) => void;
  onError?: (job: Job) => void;
}

/**
 * Poll status job background sampai mencapai status terminal (success/failed).
 *
 * Pemakaian:
 *   const { job, polling, error, start, stop } = useJobPolling({ onSuccess });
 *   start(jobId);   // mulai polling
 */
export function useJobPolling(options: UseJobPollingOptions = {}) {
  const { intervalMs = 2000, onSuccess, onError } = options;
  const [job, setJob] = useState<Job | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelled = useRef(false);
  // Simpan callback di ref agar efek polling tidak bergantung pada identitasnya.
  const callbacks = useRef({ onSuccess, onError });
  callbacks.current = { onSuccess, onError };

  const clearTimer = useCallback(() => {
    if (timer.current) {
      clearTimeout(timer.current);
      timer.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    cancelled.current = true;
    clearTimer();
    setPolling(false);
  }, [clearTimer]);

  const poll = useCallback(
    async (jobId: number) => {
      try {
        const data = await fetchJob(jobId);
        if (cancelled.current) return;
        setJob(data);

        if (TERMINAL_STATUSES.includes(data.status)) {
          setPolling(false);
          if (data.status === "success") callbacks.current.onSuccess?.(data);
          else callbacks.current.onError?.(data);
          return;
        }
        timer.current = setTimeout(() => poll(jobId), intervalMs);
      } catch (e) {
        if (cancelled.current) return;
        setError(e instanceof Error ? e.message : "Gagal mengambil status pekerjaan.");
        setPolling(false);
      }
    },
    [intervalMs],
  );

  const start = useCallback(
    (jobId: number) => {
      cancelled.current = false;
      setError(null);
      setJob(null);
      setPolling(true);
      poll(jobId);
    },
    [poll],
  );

  // Bersihkan timer saat unmount.
  useEffect(
    () => () => {
      cancelled.current = true;
      clearTimer();
    },
    [clearTimer],
  );

  return { job, polling, error, start, stop };
}
