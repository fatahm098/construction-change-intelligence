import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "Margin Guardian — Civil Engineering AI Platform",
  description:
    "Platform AI multi-modul untuk teknik sipil: deteksi perubahan gambar, BOQ/RAB AHSP, Document Q&A, Progress/EVM, dan Variation Order.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="dark">
      <body className="bg-surface text-on-surface antialiased">
        <div className="flex h-screen w-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 min-w-0 overflow-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}
