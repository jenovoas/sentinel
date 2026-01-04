import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { CognitiveNavBar } from "@/components/CognitiveNavBar";
import { CommandPalette } from "@/components/CommandPalette";
import { AICopilot } from "@/components/ai-copilot/AICopilot";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Sentinel - Control Tower",
  description: "Enterprise observability and security platform with AI-powered insights",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <CommandPalette />
          {/* Global Top Navigation */}
          <CognitiveNavBar />

          {/* Page Content */}
          <main>{children}</main>

          {/* Sentinel IA - Asistente Cognitivo Global */}
          <AICopilot />
        </Providers>
      </body>
    </html>
  );
}
