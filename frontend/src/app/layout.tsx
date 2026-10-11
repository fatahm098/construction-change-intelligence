import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Margin Guardian — Construction Change Intelligence",
  description:
    "AI-Assisted CAD & Blueprint Change Detection with Deterministic BOQ Variation Order Ledger",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="dark">
      <body className="bg-surface text-on-surface antialiased">{children}</body>
    </html>
  );
}
