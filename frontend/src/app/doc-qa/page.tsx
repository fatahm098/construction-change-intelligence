"use client";

import React, { useState, useEffect } from "react";
import { DocumentUploader } from "@/components/DocumentUploader";
import { ChatPanel, ChatMessageItem } from "@/components/ChatPanel";
import { Document, DocumentType } from "@/lib/types";
import { fetchDocuments, uploadDocument, sendChat } from "@/lib/api";

export default function DocQaPage() {
  const [projectId] = useState<number>(1);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);

  const loadDocuments = async () => {
    try {
      const docs = await fetchDocuments(projectId);
      setDocuments(docs || []);
    } catch (err) {
      console.error("Gagal memuat dokumen:", err);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [projectId]);

  const handleUpload = async (file: File, docType: DocumentType) => {
    setUploading(true);
    try {
      await uploadDocument(projectId, file, docType);
      await loadDocuments();
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Gagal mengunggah dokumen.");
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async (question: string) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setChatLoading(true);
    try {
      const res = await sendChat(projectId, question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err instanceof Error
              ? `Terjadi kesalahan: ${err.message}`
              : "Terjadi kesalahan saat memproses pertanyaan.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const indexedCount = documents.filter((d) => d.status === "indexed").length;

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-surface text-on-surface">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full bg-surface/90 backdrop-blur-xl border-b border-surface-container-high px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] text-primary tracking-widest uppercase font-semibold">
                DOCUMENT Q&A
              </span>
              <span className="font-mono text-[9px] bg-surface-container-high text-primary px-1.5 py-0.5 rounded tracking-wider">
                RAG
              </span>
            </div>
            <h1 className="text-sm font-semibold text-on-surface">
              Tanya Jawab Dokumen Proyek
            </h1>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container-low border border-surface-container-high">
            <span className="font-mono text-xs text-secondary font-semibold">
              {indexedCount} dokumen terindeks
            </span>
          </div>
        </div>
      </header>

      {/* Workspace */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        <div className="flex-[34] h-full min-w-[320px] max-w-[420px]">
          <DocumentUploader
            documents={documents}
            onUpload={handleUpload}
            uploading={uploading}
          />
        </div>
        <div className="flex-[66] h-full min-w-0">
          <ChatPanel
            messages={messages}
            onSend={handleSend}
            loading={chatLoading}
            disabled={indexedCount === 0}
          />
        </div>
      </div>
    </div>
  );
}
