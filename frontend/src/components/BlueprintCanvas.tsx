"use client";

import React, { useState } from "react";
import { ChangeRegion } from "@/lib/types";
import { ZoomIn, ZoomOut, RotateCcw, Layers } from "lucide-react";

interface BlueprintCanvasProps {
  regions: ChangeRegion[];
  activeRegionId: number | null;
  onSelectRegion: (region: ChangeRegion) => void;
  diffImageUrl?: string | null;
}

export function BlueprintCanvas({
  regions,
  activeRegionId,
  onSelectRegion,
  diffImageUrl,
}: BlueprintCanvasProps) {
  const [zoom, setZoom] = useState(1);
  const [showDiffOverlay, setShowDiffOverlay] = useState(true);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.2, 2.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.2, 0.6));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="relative flex flex-col h-full bg-surface-container-lowest border border-surface-container-high rounded-lg overflow-hidden shadow-sm">
      {/* CAD Toolbar */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-1.5 p-1 rounded-md bg-surface-container/90 backdrop-blur border border-surface-container-high shadow-md">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-1.5 rounded hover:bg-surface-bright text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-1.5 rounded hover:bg-surface-bright text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleResetZoom}
          title="Reset Zoom"
          className="p-1.5 rounded hover:bg-surface-bright text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <div className="w-[1px] h-4 bg-outline-variant mx-1" />
        <button
          onClick={() => setShowDiffOverlay(!showDiffOverlay)}
          className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-mono transition-colors ${
            showDiffOverlay
              ? "bg-primary-container/20 text-primary border border-primary/30"
              : "text-on-surface-variant hover:bg-surface-bright"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>{showDiffOverlay ? "Diff Aktif" : "Raw CAD"}</span>
        </button>
        <span className="font-mono text-[10px] text-outline px-2">
          {Math.round(zoom * 100)}%
        </span>
      </div>

      {/* Blueprint Viewport */}
      <div className="relative flex-1 overflow-auto flex items-center justify-center p-8 bg-[#18181b]">
        <div
          className="relative transition-transform duration-150 origin-center select-none shadow-2xl rounded"
          style={{ transform: `scale(${zoom})` }}
        >
          {diffImageUrl ? (
            <div className="relative w-[1000px] h-[680px] bg-[#fbfbfe] border-2 border-[#27272a] rounded overflow-hidden shadow-inner">
              <img
                src={diffImageUrl}
                alt="Diff gambar teknik"
                className="w-full h-full object-contain"
              />

              {/* Overlaid Bounding Boxes */}
              {showDiffOverlay &&
                regions.map((reg) => {
                  const isSelected = activeRegionId === reg.id;
                  return (
                    <button
                      key={reg.id}
                      onClick={() => onSelectRegion(reg)}
                      style={{
                        left: `${reg.bbox_x}px`,
                        top: `${reg.bbox_y}px`,
                        width: `${reg.bbox_w}px`,
                        height: `${reg.bbox_h}px`,
                      }}
                      className={`absolute border-2 rounded transition-all cursor-pointer flex flex-col justify-between p-1 select-none ${
                        isSelected
                          ? "border-primary bg-primary/20 ring-4 ring-primary/30 z-20"
                          : "border-[#ef4444] bg-[#ef4444]/15 hover:bg-[#ef4444]/25 z-10"
                      }`}
                    >
                      <span className="font-mono text-[9px] font-bold px-1 py-0.5 rounded bg-surface/90 text-primary shadow">
                        #{reg.region_index}
                      </span>
                      {reg.status === "verified" && (
                        <span className="font-mono text-[8px] bg-secondary text-surface font-bold px-1 rounded">
                          VERIF
                        </span>
                      )}
                    </button>
                  );
                })}
            </div>
          ) : (
            <div className="w-[1000px] h-[680px] bg-surface-container-low border border-surface-container-high rounded flex flex-col items-center justify-center text-outline gap-2">
              <Layers className="w-12 h-12 opacity-30 text-primary" />
              <p className="text-sm text-on-surface-variant">Belum ada gambar diff</p>
              <p className="text-xs text-on-surface-variant/50">
                Jalankan analisis di backend untuk menghasilkan gambar perbandingan.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
