"use client";

import React, { useState, useEffect } from "react";
import { ChangeRegion, BOQItem, ElementType } from "@/lib/types";
import { ShieldCheck, XCircle, Sparkles, Check, Database, Ruler } from "lucide-react";

interface ChangeInspectorProps {
  region: ChangeRegion | null;
  boqItems: BOQItem[];
  onVerify: (data: {
    element_type: ElementType;
    dim_before_w: number;
    dim_before_h: number;
    dim_after_w: number;
    dim_after_h: number;
    height_or_length_m: number;
    link_boq_item_id: number | null;
  }) => Promise<void>;
  onReject: () => Promise<void>;
  loading: boolean;
}

export function ChangeInspector({
  region,
  boqItems,
  onVerify,
  onReject,
  loading,
}: ChangeInspectorProps) {
  const [elementType, setElementType] = useState<ElementType>("column");
  const [dimBeforeW, setDimBeforeW] = useState(300);
  const [dimBeforeH, setDimBeforeH] = useState(300);
  const [dimAfterW, setDimAfterW] = useState(400);
  const [dimAfterH, setDimAfterH] = useState(400);
  const [heightM, setHeightM] = useState(4.0);
  const [selectedBOQId, setSelectedBOQId] = useState<number | null>(null);

  // Sync state ketika region berubah
  useEffect(() => {
    if (!region) return;

    if (region.verification) {
      setElementType(region.verification.element_type);
      setDimBeforeW(region.verification.dim_before_w);
      setDimBeforeH(region.verification.dim_before_h);
      setDimAfterW(region.verification.dim_after_w);
      setDimAfterH(region.verification.dim_after_h);
      setHeightM(region.verification.height_or_length_m);
    } else {
      // Default dari OCR jika ada
      if (region.suggested_dim_v0) {
        const [w, h] = region.suggested_dim_v0.split("x").map(Number);
        if (w && h) { setDimBeforeW(w); setDimBeforeH(h); }
      }
      if (region.suggested_dim_v1) {
        const [w, h] = region.suggested_dim_v1.split("x").map(Number);
        if (w && h) { setDimAfterW(w); setDimAfterH(h); }
      }
    }

    if (region.cost_impact) {
      setSelectedBOQId(region.cost_impact.boq_item_id);
    } else if (boqItems.length > 0) {
      // Auto-suggest ke item beton kolom
      const defaultItem = boqItems.find((it) => it.description.toLowerCase().includes("kolom"));
      if (defaultItem) setSelectedBOQId(defaultItem.id);
    }
  }, [region, boqItems]);

  if (!region) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-surface-container-low border border-surface-container-high rounded-lg text-outline">
        <Ruler className="w-10 h-10 mb-3 opacity-30 text-primary" />
        <p className="text-sm font-medium text-on-surface">Pilih Bounding Box di Canvas</p>
        <p className="text-xs text-on-surface-variant mt-1">
          Klik kotak merah perbandingan di denah untuk memeriksa perbedaan dimensi dan menghubungkannya ke RAB.
        </p>
      </div>
    );
  }

  // Kalkulasi instan di UI
  const vol0 = (dimBeforeW / 1000) * (dimBeforeH / 1000) * heightM;
  const vol1 = (dimAfterW / 1000) * (dimAfterH / 1000) * heightM;
  const deltaVol = vol1 - vol0;

  const currentBOQ = boqItems.find((it) => it.id === selectedBOQId);
  const costDelta = currentBOQ ? deltaVol * currentBOQ.unit_price : 0;

  const handleCommit = async () => {
    await onVerify({
      element_type: elementType,
      dim_before_w: dimBeforeW,
      dim_before_h: dimBeforeH,
      dim_after_w: dimAfterW,
      dim_after_h: dimAfterH,
      height_or_length_m: heightM,
      link_boq_item_id: selectedBOQId,
    });
  };

  return (
    <div className="flex flex-col h-full bg-surface-container-low border border-surface-container-high rounded-lg overflow-y-auto p-4 gap-4 shadow-sm">
      {/* Header Info */}
      <div className="flex items-center justify-between pb-2 border-b border-surface-container-high">
        <div>
          <span className="font-mono text-[10px] text-primary tracking-wider uppercase font-semibold">
            REGION #{region.region_index}
          </span>
          <h2 className="text-sm font-semibold text-on-surface">
            Inspeksi Kolom Grid B2 (K1)
          </h2>
        </div>
        <span
          className={`font-mono text-[10px] px-2 py-0.5 rounded font-semibold uppercase ${
            region.status === "verified"
              ? "bg-secondary/20 text-secondary border border-secondary/30"
              : region.status === "rejected"
              ? "bg-error/20 text-error border border-error/30"
              : "bg-primary-container/20 text-primary border border-primary/30"
          }`}
        >
          {region.status}
        </span>
      </div>

      {/* Visual Crop Comparison Cards (Rev 0 vs Rev 1) */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-medium">
            Crop Penampang Teknis (Before vs After)
          </span>
          <span className="font-mono text-[10px] text-primary font-bold">
            Δ Luas: +77.8%
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {/* Rev 0 Card */}
          <div className="flex flex-col bg-surface-container rounded p-2 border border-surface-container-high">
            <div className="flex items-center justify-between mb-1">
              <span className="font-mono text-[10px] text-error font-semibold">Rev. 0 Baseline</span>
              <span className="font-mono text-[9px] text-on-surface-variant">Conf: 94%</span>
            </div>
            {/* SVG Visual Representation 300x300 */}
            <div className="relative w-full h-24 bg-surface-container-lowest rounded flex items-center justify-center border border-outline-variant/30">
              <svg className="w-16 h-16" viewBox="0 0 80 80">
                <rect x="20" y="20" width="40" height="40" fill="#93000a" fillOpacity="0.2" stroke="#ffb4ab" strokeWidth="1.5" strokeDasharray="3,2" />
                <circle cx="25" cy="25" r="2" fill="#ffb4ab" />
                <circle cx="55" cy="25" r="2" fill="#ffb4ab" />
                <circle cx="25" cy="55" r="2" fill="#ffb4ab" />
                <circle cx="55" cy="55" r="2" fill="#ffb4ab" />
                <text x="40" y="73" fill="#ffb4ab" fontFamily="JetBrains Mono" fontSize="8" textAnchor="middle">300 mm</text>
              </svg>
              <div className="absolute top-1 left-1 bg-surface-container-high/90 px-1 py-0.5 rounded text-[8px] font-mono text-error font-bold">
                {region.suggested_dim_v0 || "300x300"}
              </div>
            </div>
          </div>

          {/* Rev 1 Card */}
          <div className="flex flex-col bg-surface-container rounded p-2 border border-surface-container-high">
            <div className="flex items-center justify-between mb-1">
              <span className="font-mono text-[10px] text-secondary font-semibold">Rev. 1 Revised</span>
              <span className="font-mono text-[9px] text-on-surface-variant">Conf: 96%</span>
            </div>
            {/* SVG Visual Representation 400x400 */}
            <div className="relative w-full h-24 bg-surface-container-lowest rounded flex items-center justify-center border border-outline-variant/30">
              <svg className="w-16 h-16" viewBox="0 0 80 80">
                <rect x="12" y="12" width="56" height="56" fill="#00a572" fillOpacity="0.2" stroke="#4edea3" strokeWidth="1.5" />
                <circle cx="18" cy="18" r="2.5" fill="#4edea3" />
                <circle cx="62" cy="18" r="2.5" fill="#4edea3" />
                <circle cx="18" cy="62" r="2.5" fill="#4edea3" />
                <circle cx="62" cy="62" r="2.5" fill="#4edea3" />
                <text x="40" y="76" fill="#4edea3" fontFamily="JetBrains Mono" fontSize="8" textAnchor="middle">400 mm</text>
              </svg>
              <div className="absolute top-1 left-1 bg-surface-container-high/90 px-1 py-0.5 rounded text-[8px] font-mono text-secondary font-bold">
                {region.suggested_dim_v1 || "400x400"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Semantic Context Banner */}
      <div className="flex items-start gap-2 p-2.5 rounded bg-primary/10 border border-primary/20">
        <Sparkles className="w-4 h-4 text-primary shrink-0 mt-0.5" />
        <p className="text-xs text-on-surface leading-snug">
          <strong className="text-primary font-medium">Analisis AI:</strong> Terjadi pembesaran penampang fisik kolom beton bertulang dari 300 mm menjadi 400 mm (+33.3% dimensi linear).
        </p>
      </div>

      {/* Verification Form */}
      <div className="flex flex-col gap-3 bg-surface-container rounded-lg p-3 border border-surface-container-high">
        <span className="font-mono text-[10px] text-outline uppercase tracking-wider font-semibold">
          Parameter Verifikasi Manusia
        </span>

        {/* Element Type Selector */}
        <div className="flex gap-1.5">
          {(["column", "beam", "slab"] as ElementType[]).map((t) => (
            <button
              key={t}
              onClick={() => setElementType(t)}
              className={`flex-1 py-1 text-xs font-mono uppercase rounded transition-colors ${
                elementType === t
                  ? "bg-primary-container text-on-primary-container font-bold"
                  : "bg-surface-container-high text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Dimension Inputs */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <label className="text-[10px] text-on-surface-variant block mb-1">Dimensi Rev 0 (w × h mm)</label>
            <div className="flex items-center gap-1">
              <input
                type="number"
                value={dimBeforeW}
                onChange={(e) => setDimBeforeW(Number(e.target.value))}
                className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded px-2 py-1 font-mono text-xs text-on-surface focus:outline-none focus:border-primary"
              />
              <span className="text-outline">×</span>
              <input
                type="number"
                value={dimBeforeH}
                onChange={(e) => setDimBeforeH(Number(e.target.value))}
                className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded px-2 py-1 font-mono text-xs text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>
          <div>
            <label className="text-[10px] text-on-surface-variant block mb-1">Dimensi Rev 1 (w × h mm)</label>
            <div className="flex items-center gap-1">
              <input
                type="number"
                value={dimAfterW}
                onChange={(e) => setDimAfterW(Number(e.target.value))}
                className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded px-2 py-1 font-mono text-xs text-on-surface focus:outline-none focus:border-primary"
              />
              <span className="text-outline">×</span>
              <input
                type="number"
                value={dimAfterH}
                onChange={(e) => setDimAfterH(Number(e.target.value))}
                className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded px-2 py-1 font-mono text-xs text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Height / Length */}
        <div>
          <label className="text-[10px] text-on-surface-variant block mb-1">
            Tinggi Kolom Efektif (m)
          </label>
          <input
            type="number"
            step="0.1"
            value={heightM}
            onChange={(e) => setHeightM(Number(e.target.value))}
            className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded px-2 py-1 font-mono text-xs text-on-surface focus:outline-none focus:border-primary"
          />
        </div>

        {/* Live Volume Calculation Card */}
        <div className="p-2 rounded bg-surface-container-lowest border border-surface-container-high flex items-center justify-between">
          <span className="text-xs text-on-surface-variant font-medium">Delta Volume Beton:</span>
          <span className="font-mono text-xs text-secondary font-bold">
            +{deltaVol.toFixed(3)} m³ / kolom
          </span>
        </div>

        {/* BOQ Item Linking */}
        <div>
          <label className="text-[10px] text-on-surface-variant block mb-1 flex items-center gap-1">
            <Database className="w-3 h-3 text-secondary" />
            Hubungkan ke Item BOQ / RAB
          </label>
          <select
            value={selectedBOQId || ""}
            onChange={(e) => setSelectedBOQId(Number(e.target.value) || null)}
            className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded px-2 py-1.5 font-mono text-xs text-on-surface focus:outline-none focus:border-secondary"
          >
            <option value="">Pilih baris pekerjaan...</option>
            {boqItems.map((it) => (
              <option key={it.id} value={it.id}>
                {it.code} — {it.description} (Rp {it.unit_price.toLocaleString("id-ID")}/{it.unit})
              </option>
            ))}
          </select>
        </div>

        {/* Estimated Cost Delta */}
        {currentBOQ && (
          <div className="p-2.5 rounded bg-secondary/10 border border-secondary/20 flex flex-col gap-0.5">
            <span className="text-[10px] font-mono text-secondary uppercase font-semibold">
              Estimasi Dampak Biaya (1 Kolom):
            </span>
            <span className="font-mono text-sm text-secondary font-bold">
              +Rp {costDelta.toLocaleString("id-ID", { maximumFractionDigits: 0 })}
            </span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 pt-1 mt-auto">
        <button
          onClick={onReject}
          disabled={loading}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded bg-surface-container hover:bg-surface-bright text-on-surface-variant text-xs font-mono transition-colors border border-outline-variant/40"
        >
          <XCircle className="w-3.5 h-3.5 text-error" />
          <span>Tolak (False Positive)</span>
        </button>
        <button
          onClick={handleCommit}
          disabled={loading}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded bg-secondary-container hover:bg-secondary text-surface text-xs font-mono font-bold transition-colors shadow"
        >
          <Check className="w-4 h-4" />
          <span>Verifikasi & Simpan</span>
        </button>
      </div>
    </div>
  );
}
