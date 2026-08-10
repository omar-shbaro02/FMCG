import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VAI FMCG Growth Quality Diagnostic",
  description: "Forecast-augmented FMCG commercial decision intelligence",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

