import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sentinel - Multi-tenant SaaS Platform',
  description: 'Secure, scalable, and modern SaaS platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-slate-900 to-slate-800 text-gray-100">
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
