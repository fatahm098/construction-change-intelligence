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
  AnalysisRun,
} from "@/lib/types";
import {
  fetchProjectSummary,
  fetchLatestAnalysisRun,
  fetchProjectBOQ,
  verifyDimension,
  rejectRegion,
  dataPathToUrl,
} from "@/lib/api";

export default function ChangeIntelPage() {
  const [projectId] = useState<number>(1);
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [runData, setRunData] = useState<AnalysisRun | null>(null);
  const [regions, setRegions] = useState<ChangeRegion[]>([]);
  const [activeRegion, setActiveRegion] = useState<ChangeRegion | null>(null);
  const [boqItems, setBoqItems] = useState<BOQItem[]>([]);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      const [sumData, run, boqData] = await Promise.all([
        fetchProjectSummary(projectId),
        fetchLatestAnalysisRun(projectId),
        fetchProjectBOQ(projectId),
      ]);

      setSummary(sumData);
      setRunData(run);
      setRegions(run.regions || []);
      setBoqItems(boqData || []);

      if (run.regions && run.regions.length > 0) {
        setActiveRegion(run.regions[0]);
      }
    } catch (err) {
      console.error("Gagal mengambil data dari FastAPI backend:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const diffImageUrl = dataPathToUrl(runData?.diff_image_path);

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
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      <Header summary={summary} activeDiffCount={regions.length} />

      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        <div className="flex-[68] h-full min-w-0">
          <BlueprintCanvas
            regions={regions}
            activeRegionId={activeRegion ? activeRegion.id : null}
            onSelectRegion={(reg) => setActiveRegion(reg)}
            diffImageUrl={diffImageUrl}
          />
        </div>

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

      <VariationLedger boqItems={boqItems} regions={regions} />
    </div>
  );
}
