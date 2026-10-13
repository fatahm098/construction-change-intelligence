"use client";

import React, { useRef, useState } from "react";
import { Document, DocumentType } from "@/lib/types";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface DocumentUploaderProps {
  documents: Document[];
  onUpload: (file: File, docType: DocumentType) => Promise<void>;
  uploading: boolean;
}

const DOC_TYPES: { value: DocumentType; label: string }[] = [
  { value: "rks", label: "RKS" },
  { value: "kontrak", label: "Kontrak" },
  { value: "sni", label: "SNI" },
  { value: "ahsp", label: "AHSP" },
  { value: "other", label: "Lainnya" },
];

export function DocumentUploader({ documents, onUpload, uploading }: DocumentUploaderProps) {
  const [docType, setDocType] = useState<DocumentType>("rks");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    await onUpload(files[0], docType);
  };

  return (
    <div className="flex flex-col h-full bg-surface-container-low border border-surface-container-high rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-surface-container-high">
        <span className="font-mono text-[10px] text-primary tracking-wider uppercase font-semibold">
          Dokumen Sumber
        </span>
        <p className="text-xs text-on-surface-variant mt-0.5">
          Unggah RKS, kontrak, SNI, atau AHSP (PDF)
        </p>
      </div>

      <div className="p-3 flex flex-col gap-2 border-b border-surface-container-high">
        {/* Doc type selector */}
        <div className="flex gap-1">
          {DOC_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => setDocType(t.value)}
              className={`flex-1 py-1 text-[10px] font-mono uppercase rounded transition-colors ${
                docType === t.value
                  ? "bg-primary-container text-on-primary-container font-bold"
                  : "bg-surface-container-high text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Drop zone */}
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            handleFiles(e.dataTransfer.files);
          }}
          className={`flex flex-col items-center justify-center gap-1.5 py-5 rounded border-2 border-dashed cursor-pointer transition-colors ${
            dragging
              ? "border-primary bg-primary/10"
              : "border-outline-variant/40 hover:border-primary/50 hover:bg-surface-container-high/40"
          }`}
        >
          {uploading ? (
            <>
              <Loader2 className="w-6 h-6 text-primary animate-spin" />
              <span className="text-xs text-on-surface-variant">Mengindeks dokumen...</span>
            </>
          ) : (
            <>
              <UploadCloud className="w-6 h-6 text-primary" />
              <span className="text-xs text-on-surface">Klik atau tarik PDF ke sini</span>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {documents.length === 0 ? (
          <p className="text-xs text-on-surface-variant/50 text-center py-6">
            Belum ada dokumen terunggah.
          </p>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-start gap-2 p-2 rounded bg-surface-container border border-surface-container-high"
            >
              <FileText className="w-4 h-4 text-on-surface-variant shrink-0 mt-0.5" />
              <div className="flex flex-col min-w-0 flex-1">
                <span className="text-xs text-on-surface truncate">{doc.filename}</span>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="font-mono text-[9px] uppercase text-on-surface-variant/60">
                    {doc.doc_type}
                  </span>
                  <span className="text-on-surface-variant/30">•</span>
                  {doc.status === "indexed" && (
                    <span className="flex items-center gap-0.5 font-mono text-[9px] text-secondary">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      {doc.num_chunks} chunk
                    </span>
                  )}
                  {doc.status === "failed" && (
                    <span className="flex items-center gap-0.5 font-mono text-[9px] text-error">
                      <AlertCircle className="w-2.5 h-2.5" />
                      gagal
                    </span>
                  )}
                  {doc.status === "pending" && (
                    <span className="font-mono text-[9px] text-primary">pending</span>
                  )}
                </div>
                {doc.status === "failed" && doc.error_message && (
                  <span className="text-[10px] text-error/70 mt-0.5 line-clamp-2">
                    {doc.error_message}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
