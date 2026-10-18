import { authFetch } from "./api";

export type ReportKind = "rab" | "evm" | "qc";
export type ReportFormat = "xlsx" | "pdf";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Format yang benar-benar disediakan backend per jenis laporan. */
const SUPPORTED_FORMATS: Record<ReportKind, ReportFormat[]> = {
  rab: ["xlsx", "pdf"],
  evm: ["xlsx"],
  qc: ["xlsx"],
};

/**
 * Ambil nama file dari header Content-Disposition.
 * Mendukung `filename="..."` dan `filename*=UTF-8''...` (RFC 5987).
 */
function parseFilename(disposition: string | null): string | null {
  if (!disposition) return null;

  const encodedMatch = disposition.match(/filename\*\s*=\s*([^;]+)/i);
  if (encodedMatch) {
    const raw = encodedMatch[1].trim().replace(/^"|"$/g, "");
    // Buang prefix charset'lang' (mis. UTF-8'') sebelum decode.
    const encoded = raw.replace(/^[^']*'[^']*'/, "");
    try {
      return decodeURIComponent(encoded) || null;
    } catch {
      return encoded || null;
    }
  }

  const quotedMatch = disposition.match(/filename\s*=\s*"([^"]+)"/i);
  if (quotedMatch) return quotedMatch[1] || null;

  const bareMatch = disposition.match(/filename\s*=\s*([^;]+)/i);
  if (bareMatch) return bareMatch[1].trim().replace(/^"|"$/g, "") || null;

  return null;
}

async function readErrorMessage(res: Response, kind: ReportKind): Promise<string> {
  if (res.status === 401) {
    return "Sesi berakhir, silakan login ulang (HTTP 401).";
  }

  let detail = "";
  try {
    const data = await res.json();
    if (data && typeof data.detail === "string") detail = data.detail;
    else if (data && typeof data.message === "string") detail = data.message;
  } catch {
    /* respons error bukan JSON — abaikan */
  }

  const base = `Gagal mengunduh laporan ${kind.toUpperCase()} (HTTP ${res.status})`;
  return detail ? `${base}: ${detail}` : `${base}.`;
}

/**
 * Unduh laporan dari backend. Memakai `authFetch` agar header
 * `Authorization: Bearer <token>` ikut terkirim saat auth aktif.
 */
export async function downloadReport(
  projectId: number,
  kind: ReportKind,
  format: ReportFormat,
): Promise<void> {
  if (!SUPPORTED_FORMATS[kind].includes(format)) {
    throw new Error(
      `Format ${format.toUpperCase()} tidak tersedia untuk laporan ${kind.toUpperCase()}. ` +
        `Gunakan ${SUPPORTED_FORMATS[kind].map((f) => f.toUpperCase()).join(" atau ")}.`,
    );
  }

  const res = await authFetch(`${API_BASE}/api/reports/${kind}/${projectId}.${format}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(await readErrorMessage(res, kind));
  }

  const blob = await res.blob();
  const filename =
    parseFilename(res.headers.get("Content-Disposition")) || `${kind}_${projectId}.${format}`;

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  // Beri waktu browser memulai unduhan sebelum URL dilepas.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
