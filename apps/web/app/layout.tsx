import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GrantDraft - 補助金情報ダッシュボード",
  description: "JグランツとeRadの補助金情報を一覧表示するダッシュボード",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
