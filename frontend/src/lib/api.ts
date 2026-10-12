const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/api/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil daftar proyek");
  return res.json();
}

export async function fetchProjectSummary(projectId: number) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil ringkasan proyek");
  return res.json();
}

export async function fetchAnalysisRun(runId: number) {
  const res = await fetch(`${API_BASE}/api/analysis/${runId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil detail analisis");
  return res.json();
}

export async function fetchProjectBOQ(projectId: number) {
  const res = await fetch(`${API_BASE}/api/boq/by-project/${projectId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil data BOQ");
  return res.json();
}

export async function verifyDimension(regionId: number, data: {
  element_type: string;
  dim_before_w: number;
  dim_before_h: number;
  dim_after_w: number;
  dim_after_h: number;
  height_or_length_m: number;
  link_boq_item_id?: number | null;
}) {
  const res = await fetch(`${API_BASE}/api/analysis/region/${regionId}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Gagal memverifikasi dimensi");
  return res.json();
}

export async function rejectRegion(regionId: number) {
  const res = await fetch(`${API_BASE}/api/analysis/region/${regionId}/reject`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Gagal menolak region");
  return res.json();
}

export function getExportCsvUrl(projectId: number) {
  return `${API_BASE}/api/export/csv/${projectId}`;
}

/**
 * Konversi path file absolut (dari DB) ke URL yang dilayani via /static/data.
 * Backend mount /static/data ke backend/data/.
 */
export function dataPathToUrl(absolutePath: string | undefined | null): string | null {
  if (!absolutePath) return null;
  const marker = "data/";
  const idx = absolutePath.replace(/\\/g, "/").indexOf(marker);
  if (idx === -1) return null;
  const rel = absolutePath.replace(/\\/g, "/").slice(idx + marker.length);
  return `${API_BASE}/static/data/${rel}`;
}
