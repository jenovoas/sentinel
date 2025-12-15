"use client";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function TestShadcnPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-gray-100 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-4xl font-semibold text-white mb-8">shadcn/ui Test Page</h1>
        
        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
          <CardHeader>
            <CardTitle>Card Component</CardTitle>
            <CardDescription>This is a shadcn/ui Card component</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-300 mb-4">
              If you can see this card with proper styling, shadcn/ui is working correctly!
            </p>
            <div className="flex gap-2">
              <Button>Default Button</Button>
              <Button variant="outline">Outline Button</Button>
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="destructive">Destructive Button</Button>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/5 backdrop-blur-xl border-cyan-500/20">
          <CardHeader>
            <CardTitle className="text-cyan-400">Styled Card</CardTitle>
            <CardDescription>Custom styling with Tailwind</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-300">
              shadcn/ui components work perfectly with your existing Tailwind classes!
            </p>
          </CardContent>
        </Card>

        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4">
          <p className="text-emerald-400 font-semibold">✅ Success!</p>
          <p className="text-gray-300 text-sm mt-1">
            shadcn/ui is installed and working. You can now use Card, Button, and other components in your pages.
          </p>
        </div>
      </div>
    </main>
  );
}
