import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Blog SEO Writer",
  description: "한국어 블로그 SEO 작성 SaaS MVP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
