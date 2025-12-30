/**
 * Root Layout - Applies to all pages
 * 
 * This layout wraps all pages and provides:
 * - Global navigation sidebar
 * - Consistent styling
 * - Font configuration
 * - Metadata
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

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
        {/* Global Navigation Sidebar */}
        <Navigation />

        {/* Page Content */}
        <main>{children}</main>
      </body>
    </html>
  );
}
