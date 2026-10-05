import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";
import { WipModal } from "@/components/WipModal";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Sentinel — Panel de control",
  description: "Interfaz de Sentinel Cortex para métricas de runtime, presión de recursos y verificación TruthSync.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <WipModal />
        <Navigation />
        <main style={{ paddingTop: "72px" }}>{children}</main>
      </body>
    </html>
  );
}
