"use client";

import React, { useState } from "react";
import { ChangeRegion } from "@/lib/types";
import { ZoomIn, ZoomOut, RotateCcw, Eye, Layers } from "lucide-react";

interface BlueprintCanvasProps {
  regions: ChangeRegion[];
  activeRegionId: number | null;
  onSelectRegion: (region: ChangeRegion) => void;
}

export function BlueprintCanvas({
  regions,
  activeRegionId,
  onSelectRegion,
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

      {/* Interactive Blueprint Viewport */}
      <div className="relative flex-1 overflow-auto flex items-center justify-center p-8 bg-[#18181b]">
        {/* Subtle CAD Grid background */}
        <div
          className="relative transition-transform duration-150 origin-center select-none shadow-2xl rounded"
          style={{ transform: `scale(${zoom})` }}
        >
          {/* Simulated CAD Canvas SVG Vector (Ukuran rasio A3 Landscape 1200x800) */}
          <div className="relative w-[1000px] h-[680px] bg-[#fbfbfe] border-2 border-[#27272a] rounded overflow-hidden shadow-inner">
            <svg
              className="w-full h-full"
              viewBox="0 0 1000 680"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Background Grid Lines */}
              <defs>
                <pattern
                  id="cad-grid"
                  width="20"
                  height="20"
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 20 0 L 0 0 0 20"
                    fill="none"
                    stroke="#e4e4e7"
                    strokeWidth="0.5"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#cad-grid)" />

              {/* Title Block Box */}
              <rect
                x="30"
                y="30"
                width="940"
                height="620"
                fill="none"
                stroke="#18181b"
                strokeWidth="2"
              />
              <text
                x="50"
                y="65"
                fontFamily="Geist"
                fontSize="16"
                fontWeight="bold"
                fill="#09090b"
              >
                PROYEK MENARA SUDIRMAN TOWER — DENAH STRUKTUR LT. 1
              </text>
              <text x="50" y="85" fontFamily="Geist" fontSize="11" fill="#52525b">
                SKALA 1:100 | REVISI 1 (DIMENSI PENAMPANG KOLOM TERKINI)
              </text>

              {/* Structural Grids 1, 2, 3 & A, B, C */}
              <g stroke="#a1a1aa" strokeWidth="1" strokeDasharray="6,4">
                {/* Vertical Grids */}
                <line x1="250" y1="120" x2="250" y2="580" />
                <line x1="500" y1="120" x2="500" y2="580" />
                <line x1="750" y1="120" x2="750" y2="580" />
                {/* Horizontal Grids */}
                <line x1="180" y1="180" x2="820" y2="180" />
                <line x1="180" y1="360" x2="820" y2="360" />
                <line x1="180" y1="520" x2="820" y2="520" />
              </g>

              {/* Grid Bubbles */}
              <g fontFamily="Geist" fontSize="12" fontWeight="bold" textAnchor="middle">
                {/* Horizontal Labels */}
                <circle cx="160" cy="180" r="14" fill="#ffffff" stroke="#18181b" />
                <text x="160" y="184" fill="#09090b">A</text>
                <circle cx="160" cy="360" r="14" fill="#ffffff" stroke="#18181b" />
                <text x="160" y="364" fill="#09090b">B</text>
                <circle cx="160" cy="520" r="14" fill="#ffffff" stroke="#18181b" />
                <text x="160" y="524" fill="#09090b">C</text>

                {/* Vertical Labels */}
                <circle cx="250" cy="605" r="14" fill="#ffffff" stroke="#18181b" />
                <text x="250" y="609" fill="#09090b">1</text>
                <circle cx="500" cy="605" r="14" fill="#ffffff" stroke="#18181b" />
                <text x="500" y="609" fill="#09090b">2</text>
                <circle cx="750" cy="605" r="14" fill="#ffffff" stroke="#18181b" />
                <text x="750" y="609" fill="#09090b">3</text>
              </g>

              {/* Balok Penghubung */}
              <g stroke="#3f3f46" strokeWidth="2.5">
                <line x1="250" y1="180" x2="750" y2="180" />
                <line x1="250" y1="360" x2="750" y2="360" />
                <line x1="250" y1="520" x2="750" y2="520" />
                <line x1="250" y1="180" x2="250" y2="520" />
                <line x1="500" y1="180" x2="500" y2="520" />
                <line x1="750" y1="180" x2="750" y2="520" />
              </g>

              {/* Kolom Standar K1 (300x300 skala gambar ~ 24px) */}
              {[
                [250, 180], [500, 180], [750, 180],
                [250, 360],             [750, 360],
                [250, 520], [500, 520], [750, 520],
              ].map(([cx, cy], idx) => (
                <g key={idx}>
                  <rect
                    x={cx - 12}
                    y={cy - 12}
                    width="24"
                    height="24"
                    fill="#a1a1aa"
                    stroke="#18181b"
                    strokeWidth="1.5"
                  />
                  <text
                    x={cx + 18}
                    y={cy + 4}
                    fontFamily="JetBrains Mono"
                    fontSize="9"
                    fill="#3f3f46"
                  >
                    K1 (300x300)
                  </text>
                </g>
              ))}

              {/* Kolom B2 (Tengah) yang Berubah Jadi 400x400 (~ 32px) */}
              <g>
                <rect
                  x="484"
                  y="344"
                  width="32"
                  height="32"
                  fill="#71717a"
                  stroke="#18181b"
                  strokeWidth="2"
                />
                <line x1="484" y1="344" x2="516" y2="376" stroke="#18181b" strokeWidth="0.8" />
                <line x1="484" y1="376" x2="516" y2="344" stroke="#18181b" strokeWidth="0.8" />
                <text
                  x="524"
                  y="364"
                  fontFamily="JetBrains Mono"
                  fontSize="10"
                  fontWeight="bold"
                  fill="#b91c1c"
                >
                  K1 (400x400) [REV.1]
                </text>
              </g>
            </svg>

            {/* Overlaid Bounding Boxes (Hotspots yang bisa diklik) */}
            {showDiffOverlay &&
              regions.map((reg) => {
                // Mapping posisi bbox (Grid B2 adalah region #1)
                const isTarget = reg.region_index === 1;
                const left = isTarget ? 470 : (reg.region_index === 2 ? 50 : 800);
                const top = isTarget ? 330 : (reg.region_index === 2 ? 40 : 40);
                const width = isTarget ? 170 : 100;
                const height = isTarget ? 70 : 40;
                const isSelected = activeRegionId === reg.id;

                return (
                  <button
                    key={reg.id}
                    onClick={() => onSelectRegion(reg)}
                    style={{
                      left: `${left}px`,
                      top: `${top}px`,
                      width: `${width}px`,
                      height: `${height}px`,
                    }}
                    className={`absolute border-2 rounded transition-all cursor-pointer flex flex-col justify-between p-1 select-none ${
                      isSelected
                        ? "border-primary bg-primary/20 ring-4 ring-primary/30 z-20"
                        : "border-[#ef4444] bg-[#ef4444]/15 hover:bg-[#ef4444]/25 z-10"
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-mono text-[9px] font-bold px-1 py-0.5 rounded bg-surface/90 text-primary shadow">
                        #{reg.region_index} DIFF
                      </span>
                      {reg.status === "verified" && (
                        <span className="font-mono text-[8px] bg-secondary text-surface font-bold px-1 rounded">
                          VERIF
                        </span>
                      )}
                    </div>
                    {isTarget && (
                      <span className="font-mono text-[9px] text-[#ef4444] font-bold truncate">
                        300→400 mm
                      </span>
                    )}
                  </button>
                );
              })}
          </div>
        </div>
      </div>
    </div>
  );
}
