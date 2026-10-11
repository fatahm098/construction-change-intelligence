"use client";

import React, { useState } from "react";
import { BOQItem, ChangeRegion } from "@/lib/types";
import { ChevronUp, ChevronDown, FileSpreadsheet, ArrowUpRight } from "lucide-react";

interface VariationLedgerProps {
  boqItems: BOQItem[];
  regions: ChangeRegion[];
}

export function VariationLedger({ boqItems, regions }: VariationLedgerProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<"variations" | "boq">("variations");

  const verifiedRegions = regions.filter((r) => r.status === "verified" && r.cost_impact);

  return (
    <div className="w-full bg-surface-container-low border-t border-surface-container-high shadow-lg transition-all">
      {/* Header Drawer Bar */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between px-4 py-2 cursor-pointer hover:bg-surface-container/60 transition-colors select-none"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-primary">
            <FileSpreadsheet className="w-4 h-4" />
            <span className="font-mono text-xs font-bold uppercase tracking-wider">
              Ledger Variasi Biaya & BOQ
            </span>
          </div>
          <span className="font-mono text-[10px] bg-secondary/10 text-secondary border border-secondary/20 px-2 py-0.5 rounded font-semibold">
            {verifiedRegions.length} Item Terdampak
          </span>
        </div>
        <button className="text-on-surface-variant hover:text-on-surface p-1">
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>

      {/* Content Container */}
      {isOpen && (
        <div className="p-4 pt-1 max-h-64 overflow-y-auto border-t border-surface-container-high/40">
          {/* Tab Switcher */}
          <div className="flex gap-2 mb-3">
            <button
              onClick={() => setActiveTab("variations")}
              className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === "variations"
                  ? "bg-primary-container/20 text-primary border border-primary/30 font-bold"
                  : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              Variasi Desain Terverifikasi ({verifiedRegions.length})
            </button>
            <button
              onClick={() => setActiveTab("boq")}
              className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === "boq"
                  ? "bg-primary-container/20 text-primary border border-primary/30 font-bold"
                  : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              Master BOQ Kontrak ({boqItems.length})
            </button>
          </div>

          {activeTab === "variations" ? (
            verifiedRegions.length === 0 ? (
              <div className="py-6 text-center text-xs font-mono text-outline">
                Belum ada region perubahan yang diverifikasi. Verifikasi dimensi di panel kanan untuk mencatat variasi biaya.
              </div>
            ) : (
              <table className="w-full text-left font-mono text-xs">
                <thead>
                  <tr className="border-b border-surface-container-high text-outline text-[10px] uppercase">
                    <th className="pb-2">Region</th>
                    <th className="pb-2">Elemen</th>
                    <th className="pb-2">Dimensi (Rev 0 → Rev 1)</th>
                    <th className="pb-2 text-right">Delta Vol</th>
                    <th className="pb-2">Item BOQ Terkait</th>
                    <th className="pb-2 text-right">Harga Satuan (IDR)</th>
                    <th className="pb-2 text-right">Dampak Biaya (IDR)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-container-high/30">
                  {verifiedRegions.map((reg) => {
                    const v = reg.verification!;
                    const ci = reg.cost_impact!;
                    return (
                      <tr key={reg.id} className="hover:bg-surface-container/40">
                        <td className="py-2 text-primary font-bold">#{reg.region_index}</td>
                        <td className="py-2 capitalize">{v.element_type}</td>
                        <td className="py-2">
                          {v.dim_before_w}×{v.dim_before_h} → {v.dim_after_w}×{v.dim_after_h} mm
                        </td>
                        <td className="py-2 text-right text-secondary font-bold">
                          +{v.delta_volume_m3.toFixed(3)} m³
                        </td>
                        <td className="py-2 text-on-surface-variant truncate max-w-[200px]">
                          {ci.boq_item ? `${ci.boq_item.code} - ${ci.boq_item.description}` : "Item BOQ"}
                        </td>
                        <td className="py-2 text-right">
                          {ci.unit_price.toLocaleString("id-ID")}
                        </td>
                        <td className="py-2 text-right text-secondary font-bold">
                          +Rp {ci.total_cost_delta.toLocaleString("id-ID")}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )
          ) : (
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-surface-container-high text-outline text-[10px] uppercase">
                  <th className="pb-2">Kode</th>
                  <th className="pb-2">Uraian Pekerjaan</th>
                  <th className="pb-2">Satuan</th>
                  <th className="pb-2 text-right">Vol Kontrak</th>
                  <th className="pb-2 text-right">Harga Satuan (IDR)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-container-high/30">
                {boqItems.map((it) => (
                  <tr key={it.id} className="hover:bg-surface-container/40">
                    <td className="py-2 text-primary">{it.code}</td>
                    <td className="py-2 text-on-surface">{it.description}</td>
                    <td className="py-2">{it.unit}</td>
                    <td className="py-2 text-right">{it.contract_volume.toLocaleString("id-ID")}</td>
                    <td className="py-2 text-right font-medium">
                      Rp {it.unit_price.toLocaleString("id-ID")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
