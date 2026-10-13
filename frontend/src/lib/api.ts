import type {
  Job,
  JobEnqueueResponse,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// --- Token store (localStorage) ---

const TOKEN_KEY = "mg_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* ignore quota / private mode */
  }
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

/**
 * fetch yang otomatis menambahkan header Authorization bila token tersedia.
 * Endpoint lama tetap publik (auth_enabled=false), jadi tidak ada redirect paksa.
 */
export async function authFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return fetch(input, { ...init, headers });
}

async function readError(res: Response, fallback: string): Promise<string> {
  const detail = await res.json().catch(() => ({}));
  return (detail && (detail.detail || detail.message)) || fallback;
}

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

export async function fetchLatestAnalysisRun(projectId: number) {
  const res = await fetch(`${API_BASE}/api/analysis/by-project/${projectId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil analisis terbaru");
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

// --- Document Q&A ---

export async function fetchDocuments(projectId: number) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/documents`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil daftar dokumen");
  return res.json();
}

export async function uploadDocument(projectId: number, file: File, docType: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("doc_type", docType);
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/documents`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "Gagal mengunggah dokumen");
  }
  return res.json();
}

export async function sendChat(projectId: number, question: string, topK = 5) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "Gagal memproses pertanyaan");
  }
  return res.json();
}

// --- BOQ & RAB (AHSP) ---

export async function fetchRAB(projectId: number) {
  const res = await fetch(`${API_BASE}/api/rab/${projectId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil data RAB");
  return res.json();
}

export async function fetchAHSPList() {
  const res = await fetch(`${API_BASE}/api/ahsp`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil katalog AHSP");
  return res.json();
}

export async function fetchAHSPDetail(ahspId: number) {
  const res = await fetch(`${API_BASE}/api/ahsp/${ahspId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil detail AHSP");
  return res.json();
}

export async function suggestBOQ(regionId: number) {
  const res = await fetch(`${API_BASE}/api/boq/suggest/${regionId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Gagal mengambil rekomendasi BOQ");
  return res.json();
}

export async function uploadBOQ(projectId: number, file: File) {
  const form = new FormData();
  form.append("project_id", String(projectId));
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/boq/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "Gagal mengunggah BOQ");
  }
  return res.json();
}

// --- Fase 4: Auth ---

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await readError(res, "Email atau password salah."));
  }
  const data: TokenResponse = await res.json();
  setToken(data.access_token);
  return data;
}

export async function register(payload: RegisterRequest): Promise<User> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await readError(res, "Gagal mendaftar."));
  }
  return res.json();
}

export async function fetchMe(): Promise<User> {
  const res = await authFetch(`${API_BASE}/api/auth/me`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await readError(res, "Sesi tidak valid."));
  }
  return res.json();
}

export function logout(): void {
  clearToken();
}

// --- Fase 4: Background jobs ---

export interface EnqueueAnalysisPayload {
  project_id: number;
  drawing_ref_id: number;
  drawing_rev_id: number;
  min_area?: number;
}

/** Masukkan analisis gambar ke antrean background. */
export async function enqueueAnalysisJob(
  payload: EnqueueAnalysisPayload,
): Promise<JobEnqueueResponse> {
  const res = await authFetch(`${API_BASE}/api/jobs/analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(await readError(res, "Gagal memasukkan pekerjaan ke antrean."));
  }
  return res.json();
}

/** Ambil status/ hasil sebuah job. */
export async function fetchJob(jobId: number): Promise<Job> {
  const res = await authFetch(`${API_BASE}/api/jobs/${jobId}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await readError(res, "Gagal mengambil status pekerjaan."));
  }
  return res.json();
}
