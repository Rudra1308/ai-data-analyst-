import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Data Analyst — Enterprise SaaS Platform",
  description: "AI-powered data analysis platform. Upload datasets, clean data, perform EDA, train models, and forecast trends instantly.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
