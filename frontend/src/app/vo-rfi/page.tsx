"use client";

import React, { useState, useEffect } from "react";
import { VariationOrder, RFI, VOStatus, Project } from "@/lib/types";
import {
  fetchProjects,
  fetchVOs,
  createVO,
  updateVOStatus,
  fetchRFIs,
  createRFI,
  answerRFI,
} from "@/lib/api";
import { FolderGit2, Plus, MessageSquare, Check, RefreshCw } from "lucide-react";

const formatIDR = (val: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(val);

const VO_STATUSES: VOStatus[] = ["draft", "submitted", "approved", "rejected"];

const VO_STATUS_META: Record<VOStatus, { label: string; className: string }> = {
  draft: { label: "Draft", className: "bg-surface-container-high/60 text-on-surface-variant border-outline-variant/40" },
  submitted: { label: "Diajukan", className: "bg-primary/10 text-primary border-primary/30" },
  approved: { label: "Disetujui", className: "bg-secondary/10 text-secondary border-secondary/30" },
  rejected: { label: "Ditolak", className: "bg-error-container/30 text-error border-error/30" },
};

const RFI_STATUS_META: Record<string, { label: string; className: string }> = {
  open: { label: "Terbuka", className: "bg-primary/10 text-primary border-primary/30" },
  answered: { label: "Terjawab", className: "bg-secondary/10 text-secondary border-secondary/30" },
  closed: { label: "Tutup", className: "bg-surface-container-high/60 text-on-surface-variant border-outline-variant/40" },
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

export default function VoRfiPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectId, setProjectId] = useState<number | null>(null);
  const [vos, setVos] = useState<VariationOrder[]>([]);
  const [rfis, setRfis] = useState<RFI[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingVO, setSavingVO] = useState(false);
  const [savingRFI, setSavingRFI] = useState(false);
  const [answeringId, setAnsweringId] = useState<number | null>(null);
  const [answerText, setAnswerText] = useState("");

  // VO form state
  const [voNumber, setVoNumber] = useState("");
  const [voTitle, setVoTitle] = useState("");
  const [voDescription, setVoDescription] = useState("");
  const [voAmount, setVoAmount] = useState("");
  const [voRegionId, setVoRegionId] = useState("");

  // RFI form state
  const [rfiNumber, setRfiNumber] = useState("");
  const [rfiSubject, setRfiSubject] = useState("");
  const [rfiQuestion, setRfiQuestion] = useState("");
  const [rfiVoId, setRfiVoId] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const list: Project[] = await fetchProjects();
        setProjects(list || []);
        if (list && list.length > 0) setProjectId(list[0].id);
      } catch (err) {
        console.error("Gagal memuat daftar proyek:", err);
      }
    })();
  }, []);

  const loadData = async (id: number) => {
    setLoading(true);
    try {
      const [voData, rfiData] = await Promise.all([fetchVOs(id), fetchRFIs(id)]);
      setVos(voData || []);
      setRfis(rfiData || []);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal memuat data VO & RFI.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId != null) loadData(projectId);
  }, [projectId]);

  const handleCreateVO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (projectId == null) return;
    setSavingVO(true);
    try {
      await createVO(projectId, {
        vo_number: voNumber,
        title: voTitle,
        description: voDescription || undefined,
        amount: Number(voAmount) || 0,
        change_region_id: voRegionId ? Number(voRegionId) : undefined,
      });
      setVoNumber("");
      setVoTitle("");
      setVoDescription("");
      setVoAmount("");
      setVoRegionId("");
      await loadData(projectId);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal membuat variation order.");
    } finally {
      setSavingVO(false);
    }
  };

  const handleStatusChange = async (voId: number, status: VOStatus) => {
    if (projectId == null) return;
    try {
      const updated = await updateVOStatus(voId, status);
      setVos((prev) => prev.map((v) => (v.id === voId ? { ...v, ...updated } : v)));
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal memperbarui status VO.");
    }
  };

  const handleCreateRFI = async (e: React.FormEvent) => {
    e.preventDefault();
    if (projectId == null) return;
    setSavingRFI(true);
    try {
      await createRFI(projectId, {
        rfi_number: rfiNumber,
        subject: rfiSubject,
        question: rfiQuestion,
        variation_order_id: rfiVoId ? Number(rfiVoId) : undefined,
      });
      setRfiNumber("");
      setRfiSubject("");
      setRfiQuestion("");
      setRfiVoId("");
      await loadData(projectId);
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal membuat RFI.");
    } finally {
      setSavingRFI(false);
    }
  };

  const handleAnswer = async (rfiId: number) => {
    if (projectId == null || !answerText.trim()) return;
    try {
      const updated = await answerRFI(rfiId, answerText.trim());
      setRfis((prev) => prev.map((r) => (r.id === rfiId ? { ...r, ...updated } : r)));
      setAnsweringId(null);
      setAnswerText("");
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal menjawab RFI.");
    }
  };

  const voTotal = vos.reduce((sum, v) => sum + (v.amount || 0), 0);
  const openRfiCount = rfis.filter((r) => r.status === "open").length;

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-primary" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                VO &amp; RFI
              </span>
              <h1 className="text-sm font-semibold text-on-surface">
                Variation Order &amp; Request for Information
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

            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container-low border border-surface-container-high">
              <span className="font-mono text-[10px] text-on-surface-variant">Nilai VO</span>
              <span className="font-mono text-xs text-primary font-semibold">{formatIDR(voTotal)}</span>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-primary/10 border border-primary/20">
              <span className="font-mono text-[10px] text-primary">RFI Terbuka</span>
              <span className="font-mono text-xs text-primary font-bold">{openRfiCount}</span>
            </div>

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
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* VO Panel */}
        <div className="flex-1 min-w-0 flex flex-col bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
            <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
              Variation Order
            </span>
            <span className="font-mono text-[10px] text-on-surface-variant">{vos.length} item</span>
          </div>

          <div className="flex-1 overflow-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-surface-container z-10">
                <tr className="text-left text-on-surface-variant/70 font-mono text-[10px] uppercase">
                  <th className="px-3 py-2 font-medium">No. VO</th>
                  <th className="px-3 py-2 font-medium">Judul</th>
                  <th className="px-3 py-2 font-medium text-right">Nilai</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-3 py-2 font-medium">Ubah Status</th>
                </tr>
              </thead>
              <tbody className="font-mono">
                {vos.map((vo) => {
                  const meta = VO_STATUS_META[vo.status] || VO_STATUS_META.draft;
                  return (
                    <tr
                      key={vo.id}
                      className="border-t border-surface-container-high/40 hover:bg-surface-container/50 align-top"
                    >
                      <td className="px-3 py-2 text-primary whitespace-nowrap">{vo.vo_number}</td>
                      <td className="px-3 py-2 text-on-surface font-sans max-w-[220px]">
                        <div className="truncate" title={vo.title}>
                          {vo.title}
                        </div>
                        {vo.description && (
                          <div className="text-[10px] text-on-surface-variant/50 truncate" title={vo.description}>
                            {vo.description}
                          </div>
                        )}
                      </td>
                      <td className="px-3 py-2 text-right text-on-surface whitespace-nowrap">
                        {formatIDR(vo.amount)}
                      </td>
                      <td className="px-3 py-2">
                        <StatusBadge label={meta.label} className={meta.className} />
                      </td>
                      <td className="px-3 py-2">
                        <select
                          value={vo.status}
                          onChange={(e) => handleStatusChange(vo.id, e.target.value as VOStatus)}
                          className="px-2 py-1 rounded bg-surface-container border border-surface-container-high text-[10px] text-on-surface focus:outline-none focus:border-primary/50"
                        >
                          {VO_STATUSES.map((s) => (
                            <option key={s} value={s}>
                              {VO_STATUS_META[s].label}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  );
                })}
                {vos.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-8 text-center text-on-surface-variant/50 font-sans">
                      Belum ada variation order.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Create VO Form */}
          <form
            onSubmit={handleCreateVO}
            className="border-t border-surface-container-high p-3 space-y-2 bg-surface-container-lowest/40"
          >
            <div className="flex items-center gap-2">
              <Plus className="w-3.5 h-3.5 text-primary" />
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Buat VO Baru
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                required
                value={voNumber}
                onChange={(e) => setVoNumber(e.target.value)}
                placeholder="No. VO"
                className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
              />
              <input
                required
                value={voTitle}
                onChange={(e) => setVoTitle(e.target.value)}
                placeholder="Judul"
                className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
              />
              <input
                required
                type="number"
                step="1"
                min="0"
                value={voAmount}
                onChange={(e) => setVoAmount(e.target.value)}
                placeholder="Nilai (IDR)"
                className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
              />
              <input
                type="number"
                step="1"
                value={voRegionId}
                onChange={(e) => setVoRegionId(e.target.value)}
                placeholder="ID Region (opsional)"
                className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
              />
            </div>
            <input
              value={voDescription}
              onChange={(e) => setVoDescription(e.target.value)}
              placeholder="Deskripsi (opsional)"
              className="w-full px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
            />
            <button
              type="submit"
              disabled={savingVO || projectId == null}
              className="w-full px-3 py-2 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-semibold font-mono border border-primary/30 transition-colors disabled:opacity-50"
            >
              {savingVO ? "Menyimpan..." : "Simpan VO"}
            </button>
          </form>
        </div>

        {/* RFI Panel */}
        <div className="flex-1 min-w-0 flex flex-col bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
          <div className="px-4 py-2.5 border-b border-surface-container-high flex items-center justify-between">
            <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
              Request for Information
            </span>
            <span className="font-mono text-[10px] text-on-surface-variant">{rfis.length} item</span>
          </div>

          <div className="flex-1 overflow-auto p-2 space-y-2">
            {rfis.map((rfi) => {
              const meta = RFI_STATUS_META[rfi.status] || RFI_STATUS_META.open;
              return (
                <div
                  key={rfi.id}
                  className="rounded-lg bg-surface-container border border-surface-container-high/50 p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex flex-col min-w-0">
                      <span className="font-mono text-[10px] text-primary">{rfi.rfi_number}</span>
                      <span className="text-xs text-on-surface font-medium truncate" title={rfi.subject}>
                        {rfi.subject}
                      </span>
                    </div>
                    <StatusBadge label={meta.label} className={meta.className} />
                  </div>

                  <p className="mt-2 text-[11px] text-on-surface-variant/80 whitespace-pre-wrap">
                    {rfi.question}
                  </p>

                  {rfi.answer && (
                    <div className="mt-2 pl-2 border-l-2 border-secondary/40">
                      <span className="font-mono text-[9px] text-secondary uppercase tracking-wider">
                        Jawaban
                      </span>
                      <p className="text-[11px] text-on-surface/90 whitespace-pre-wrap">{rfi.answer}</p>
                    </div>
                  )}

                  {rfi.status === "open" && (
                    <div className="mt-2">
                      {answeringId === rfi.id ? (
                        <div className="space-y-1.5">
                          <textarea
                            autoFocus
                            value={answerText}
                            onChange={(e) => setAnswerText(e.target.value)}
                            rows={2}
                            placeholder="Tulis jawaban..."
                            className="w-full px-2.5 py-1.5 rounded bg-surface-container-low border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50 resize-none"
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleAnswer(rfi.id)}
                              disabled={!answerText.trim()}
                              className="flex items-center gap-1 px-2.5 py-1 rounded bg-secondary/10 hover:bg-secondary/20 text-secondary text-[10px] font-mono font-semibold border border-secondary/30 transition-colors disabled:opacity-50"
                            >
                              <Check className="w-3 h-3" />
                              Kirim Jawaban
                            </button>
                            <button
                              onClick={() => {
                                setAnsweringId(null);
                                setAnswerText("");
                              }}
                              className="px-2.5 py-1 rounded text-on-surface-variant text-[10px] font-mono hover:bg-surface-container-high transition-colors"
                            >
                              Batal
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            setAnsweringId(rfi.id);
                            setAnswerText("");
                          }}
                          className="flex items-center gap-1 px-2.5 py-1 rounded bg-surface-container-high hover:bg-surface-bright text-on-surface text-[10px] font-mono border border-outline-variant/40 transition-colors"
                        >
                          <MessageSquare className="w-3 h-3 text-primary" />
                          Jawab RFI
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
            {rfis.length === 0 && (
              <p className="text-xs text-on-surface-variant/50 text-center py-6 font-sans">
                Belum ada RFI.
              </p>
            )}
          </div>

          {/* Create RFI Form */}
          <form
            onSubmit={handleCreateRFI}
            className="border-t border-surface-container-high p-3 space-y-2 bg-surface-container-lowest/40"
          >
            <div className="flex items-center gap-2">
              <Plus className="w-3.5 h-3.5 text-primary" />
              <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
                Buat RFI Baru
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                required
                value={rfiNumber}
                onChange={(e) => setRfiNumber(e.target.value)}
                placeholder="No. RFI"
                className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
              />
              <input
                type="number"
                step="1"
                value={rfiVoId}
                onChange={(e) => setRfiVoId(e.target.value)}
                placeholder="ID VO terkait (opsional)"
                className="px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
              />
            </div>
            <input
              required
              value={rfiSubject}
              onChange={(e) => setRfiSubject(e.target.value)}
              placeholder="Subjek"
              className="w-full px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50"
            />
            <textarea
              required
              value={rfiQuestion}
              onChange={(e) => setRfiQuestion(e.target.value)}
              rows={2}
              placeholder="Pertanyaan..."
              className="w-full px-2.5 py-1.5 rounded bg-surface-container border border-surface-container-high text-xs text-on-surface focus:outline-none focus:border-primary/50 resize-none"
            />
            <button
              type="submit"
              disabled={savingRFI || projectId == null}
              className="w-full px-3 py-2 rounded bg-primary-container/20 hover:bg-primary-container/30 text-primary text-xs font-semibold font-mono border border-primary/30 transition-colors disabled:opacity-50"
            >
              {savingRFI ? "Menyimpan..." : "Simpan RFI"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
