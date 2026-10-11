"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { BlueprintCanvas } from "@/components/BlueprintCanvas";
import { ChangeInspector } from "@/components/ChangeInspector";
import { VariationLedger } from "@/components/VariationLedger";
import {
  ProjectSummary,
  ChangeRegion,
  BOQItem,
  ElementType,
} from "@/lib/types";
import {
  fetchProjectSummary,
  fetchAnalysisRun,
  fetchProjectBOQ,
  verifyDimension,
  rejectRegion,
} from "@/lib/api";

export default function WorkspacePage() {
  const [projectId] = useState<number>(1);
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [regions, setRegions] = useState<ChangeRegion[]>([]);
  const [activeRegion, setActiveRegion] = useState<ChangeRegion | null>(null);
  const [boqItems, setBoqItems] = useState<BOQItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Load project data on mount
  const loadData = async () => {
    try {
      const [sumData, runData, boqData] = await Promise.all([
        fetchProjectSummary(projectId),
        fetchAnalysisRun(1), // Default run 1 dari spike/seed
        fetchProjectBOQ(projectId),
      ]);

      setSummary(sumData);
      setRegions(runData.regions || []);
      setBoqItems(boqData || []);

      // Auto-select region pertama jika belum ada yang terpilih
      if (runData.regions && runData.regions.length > 0) {
        setActiveRegion(runData.regions[0]);
      }
    } catch (err) {
      console.error("Gagal mengambil data dari FastAPI backend:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  // Handle Verify Dimension
  const handleVerify = async (data: {
    element_type: ElementType;
    dim_before_w: number;
    dim_before_h: number;
    dim_after_w: number;
    dim_after_h: number;
    height_or_length_m: number;
    link_boq_item_id: number | null;
  }) => {
    if (!activeRegion) return;
    setLoading(true);
    try {
      await verifyDimension(activeRegion.id, data);
      await loadData();
    } catch (err) {
      console.error(err);
      alert("Gagal memverifikasi dimensi.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Reject
  const handleReject = async () => {
    if (!activeRegion) return;
    setLoading(true);
    try {
      await rejectRegion(activeRegion.id);
      await loadData();
    } catch (err) {
      console.error(err);
      alert("Gagal menolak region.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-surface text-on-surface">
      {/* Top Navigation */}
      <Header summary={summary} activeDiffCount={regions.length} />

      {/* Main CAD & Inspector Workspace */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* Left 68%: Blueprint Canvas */}
        <div className="flex-[68] h-full min-w-0">
          <BlueprintCanvas
            regions={regions}
            activeRegionId={activeRegion ? activeRegion.id : null}
            onSelectRegion={(reg) => setActiveRegion(reg)}
          />
        </div>

        {/* Right 32%: Change Inspector & AI Verification */}
        <div className="flex-[32] h-full min-w-[380px] max-w-[480px]">
          <ChangeInspector
            region={activeRegion}
            boqItems={boqItems}
            onVerify={handleVerify}
            onReject={handleReject}
            loading={loading}
          />
        </div>
      </div>

      {/* Bottom Ledger Drawer */}
      <VariationLedger boqItems={boqItems} regions={regions} />
    </div>
  );
}
