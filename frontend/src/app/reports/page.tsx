"use client";

import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, ChevronRight, Loader2, Download, Search, HardDrive, Shield, BookOpen, Clock, Zap, Terminal } from "lucide-react";

interface DocFile {
  name: string;
  path: string;
}

export default function ReportsPage() {
  const [docs, setDocs] = useState<DocFile[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch("/api/reports/list")
      .then(res => res.json())
      .then(data => {
        const files = data.files || [];
        setDocs(files);
        if (files.length > 0) {
          loadDoc(files[0].name);
        }
      })
      .catch(err => console.error("Failed to load docs list", err));
  }, []);

  const loadDoc = async (filename: string) => {
    setLoading(true);
    setSelectedDoc(filename);
    try {
      const res = await fetch(`/api/reports/read?file=${filename}`);
      const data = await res.json();
      setContent(data.content || "No content found.");
    } catch (error) {
      setContent("Error loading documentation.");
    } finally {
      setLoading(false);
    }
  };

  const filteredDocs = docs.filter(doc =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-[#020617] text-gray-100 selection:bg-purple-500/30 overflow-hidden relative">
      {/* Background Aesthetic */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[10%] -left-[5%] w-[40%] h-[40%] bg-purple-500/5 blur-[120px] rounded-full" />
        <div className="absolute bottom-[20%] -right-[5%] w-[40%] h-[50%] bg-blue-500/5 blur-[120px] rounded-full" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 pointer-events-none" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-[1700px] px-8 py-10 flex flex-col h-screen">
        <header className="flex flex-col md:flex-row items-end justify-between gap-8 mb-12 shrink-0">
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4 mb-3"
            >
              <div className="h-[3px] w-12 bg-gradient-to-r from-purple-500 to-transparent rounded-full" />
              <p className="text-[10px] uppercase tracking-[0.6em] text-purple-400 font-black">Sentinel Knowledge Base // Archive Matrix v2.1</p>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white uppercase italic leading-none">
              Sovereign <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-white to-blue-500">Archives Matrix</span>
            </h1>
            <p className="text-gray-500 mt-6 max-w-2xl font-bold uppercase tracking-widest text-[10px] italic">
              ITIL / ISO Standard Operating Procedures // Incident Response & Recovery Intelligence.
            </p>
          </div>

          <div className="flex gap-4">
            <div className="flex flex-col items-end gap-1 px-6 py-2 border-r border-white/10 pr-8">
              <span className="text-[8px] font-black text-gray-600 uppercase tracking-widest">Storage Status</span>
              <span className="text-xs font-black text-emerald-400 italic">OPTIMIZED</span>
            </div>
            <button className="h-14 px-8 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-black uppercase tracking-widest hover:bg-purple-500/20 transition-all flex items-center gap-3 shadow-[0_0_20px_rgba(168,85,247,0.1)]">
              <Download size={16} /> Export Intelligence
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-12 gap-8 mb-4">
          {/* Sidebar Area */}
          <div className="md:col-span-3 flex flex-col gap-6 overflow-hidden">
            <div className="relative group">
              <div className="absolute -inset-[1px] bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-2xl blur-sm opacity-50 group-hover:opacity-100 transition-opacity" />
              <div className="relative bg-[#0a0f1e] border border-white/5 rounded-2xl overflow-hidden">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="QUERY ARCHIVES..."
                  className="w-full bg-transparent border-none py-4 pl-12 pr-4 text-[10px] font-black text-white placeholder:text-gray-600 focus:ring-0 uppercase tracking-widest"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-3 custom-scrollbar">
              <div className="flex items-center gap-3 px-2 mb-2">
                <HardDrive size={14} className="text-purple-500" />
                <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">Central Repository</span>
              </div>

              <AnimatePresence mode="popLayout">
                {filteredDocs.map((doc, idx) => (
                  <motion.button
                    key={doc.name}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.03 }}
                    onClick={() => loadDoc(doc.name)}
                    className={`group w-full text-left p-4 rounded-2xl flex items-center gap-4 transition-all relative overflow-hidden ${selectedDoc === doc.name
                      ? "bg-purple-500/10 border border-purple-500/30 text-purple-200"
                      : "bg-white/2 border border-white/5 hover:bg-white/5 text-gray-500 hover:text-gray-200"
                      }`}
                  >
                    {selectedDoc === doc.name && (
                      <motion.div layoutId="active-doc" className="absolute left-0 top-0 h-full w-1 bg-purple-500" />
                    )}
                    <FileText className={`w-4 h-4 shrink-0 transition-transform group-hover:scale-110 ${selectedDoc === doc.name ? 'text-purple-400' : 'text-gray-600'}`} />
                    <span className="truncate text-[10px] font-black uppercase tracking-widest">{doc.name.replace('.md', '')}</span>
                    <ChevronRight className={`w-3 h-3 ml-auto transition-opacity ${selectedDoc === doc.name ? 'opacity-100' : 'opacity-0'}`} />
                  </motion.button>
                ))}
              </AnimatePresence>

              {filteredDocs.length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 text-center opacity-30">
                  <Zap size={32} className="mb-4 text-gray-500" />
                  <p className="text-[10px] font-black text-white uppercase tracking-widest">No Intelligence Found</p>
                </div>
              )}
            </div>

            <div className="p-6 bg-purple-500/5 border border-purple-500/10 rounded-3xl relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-16 h-16 bg-purple-500/10 blur-2xl rounded-full" />
              <div className="flex items-center gap-3 mb-4">
                <Shield size={16} className="text-purple-400" />
                <span className="text-[10px] font-black text-white uppercase tracking-widest italic">Security Clearance</span>
              </div>
              <p className="text-[10px] font-bold text-gray-500 uppercase leading-relaxed tracking-wider">
                You are viewing Level 4 Controlled Documents. All access is logged by the Sentinel Watchdog.
              </p>
            </div>
          </div>

          {/* Content Area */}
          <div className="md:col-span-9 flex flex-col overflow-hidden relative group/content">
            <div className="absolute -inset-[1px] bg-gradient-to-br from-white/5 to-transparent rounded-[40px] border border-white/5" />
            <div className="relative flex-1 bg-slate-900/40 backdrop-blur-3xl rounded-[40px] overflow-hidden flex flex-col border border-white/5 shadow-2xl">

              <div className="h-20 shrink-0 px-10 border-b border-white/5 bg-black/20 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2.5 bg-purple-500/10 rounded-xl text-purple-400 border border-purple-500/20">
                    <BookOpen size={18} />
                  </div>
                  <div>
                    <h2 className="text-xs font-black text-white uppercase tracking-widest italic">
                      {selectedDoc ? selectedDoc.replace('.md', '').replace(/_/g, ' ') : "SELECT INTELLIGENCE FILE"}
                    </h2>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Status: READY</span>
                      <div className="w-1 h-1 rounded-full bg-gray-700" />
                      <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Verification: HASHED</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest">Last Modified</p>
                    <p className="text-[9px] font-black text-white uppercase italic">{selectedDoc ? "0x8f2a Epoch" : "---"}</p>
                  </div>
                  <div className="h-8 w-[1px] bg-white/10" />
                  <button className="p-2.5 rounded-xl bg-white/5 border border-white/5 text-gray-500 hover:text-white transition-all">
                    <Terminal size={14} />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-12 custom-scrollbar relative">
                {loading ? (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#020617]/50 backdrop-blur-sm z-20">
                    <motion.div
                      animate={{ rotate: 360, scale: [1, 1.1, 1] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 className="w-12 h-12 text-purple-500 opacity-50" />
                    </motion.div>
                    <p className="mt-6 text-[10px] font-black uppercase tracking-[0.4em] text-purple-400/50 animate-pulse italic">Decrypting Matrix Stream...</p>
                  </div>
                ) : (
                  <motion.div
                    key={selectedDoc}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="prose prose-invert prose-purple max-w-none 
                        prose-headings:font-black prose-headings:uppercase prose-headings:tracking-tighter prose-headings:italic
                        prose-p:text-gray-400 prose-p:font-bold prose-p:tracking-wide prose-p:leading-relaxed
                        prose-strong:text-purple-400 prose-code:text-cyan-400 prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/5
                        prose-li:text-gray-400 prose-li:font-bold prose-img:rounded-3xl shadow-none"
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {content}
                    </ReactMarkdown>
                  </motion.div>
                )}
              </div>

              <div className="h-12 shrink-0 px-10 border-t border-white/5 bg-black/20 flex items-center justify-between">
                <div className="flex gap-8 items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                    <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Pristine State</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                    <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Synchronized Layer 1</span>
                  </div>
                </div>
                <p className="text-[8px] font-black text-gray-700 uppercase tracking-[0.4em]">Sentinel Archive OS // Node 2.1 Final</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
