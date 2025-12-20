'use client';

import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

export default function VaultPage() {
    // Auth State
    const [masterPassword, setMasterPassword] = useState('');
    const [unlocked, setUnlocked] = useState(false);

    // Vault State
    const [service, setService] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [services, setServices] = useState([]);

    // Analysis State
    const [analyzePassword, setAnalyzePassword] = useState('');
    const [analysis, setAnalysis] = useState<any>(null);

    // Crypto State
    const [wallet, setWallet] = useState<any>(null);
    const [seedPhrase, setSeedPhrase] = useState('');

    // Docs & Notes State
    const [documents, setDocuments] = useState([]);
    const [notes, setNotes] = useState([]);

    // Benchmark State
    const [benchmarks, setBenchmarks] = useState<any>(null);

    // Browser State
    const [browserUrl, setBrowserUrl] = useState('');
    const [browserMode, setBrowserMode] = useState('clear');
    const [browserContent, setBrowserContent] = useState<any>(null);
    const [browserStatus, setBrowserStatus] = useState('Ready');

    // Finance State
    const [financeData, setFinanceData] = useState<any>(null);

    // Load initial data upon unlock
    useEffect(() => {
        if (unlocked) {
            loadServices();
            fetchDocuments();
            fetchNotes();
            loadFinance();
        }
    }, [unlocked]);

    // --- API Functions ---

    async function unlockVault() {
        try {
            const res = await fetch(`${API_URL}/vault/unlock`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ master_password: masterPassword })
            });
            if (res.ok) {
                setUnlocked(true);
            } else {
                alert('Failed to unlock vault');
            }
        } catch (error: any) {
            alert('Error: ' + error.message);
        }
    }

    async function loadServices() {
        try {
            const res = await fetch(`${API_URL}/vault/list`);
            const data = await res.json();
            setServices(data.services || []);
        } catch (error) {
            console.error('Error loading services:', error);
        }
    }

    async function savePassword() {
        try {
            const res = await fetch(`${API_URL}/vault/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ master_password: masterPassword, service, username, password })
            });
            if (res.ok) {
                alert('Password saved!');
                setService(''); setUsername(''); setPassword('');
                loadServices();
            }
        } catch (error: any) { alert('Error: ' + error.message); }
    }

    async function getPassword(serviceName: string) {
        try {
            const res = await fetch(`${API_URL}/vault/get?service=${serviceName}&master_password=${masterPassword}`);
            if (res.ok) {
                const data = await res.json();
                alert(`Password for ${serviceName}: ${data.password}`);
            }
        } catch (error: any) { alert('Error: ' + error.message); }
    }

    async function analyzePasswordStrength() {
        try {
            const res = await fetch(`${API_URL}/analyze/password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: analyzePassword })
            });
            if (res.ok) setAnalysis(await res.json());
        } catch (error: any) { alert('Error: ' + error.message); }
    }

    async function generateWallet() {
        try {
            const res = await fetch(`${API_URL}/crypto/generate`, { method: 'POST' });
            if (res.ok) setWallet(await res.json());
        } catch (error: any) { alert('Error: ' + error.message); }
    }

    async function recoverWallet() {
        try {
            const res = await fetch(`${API_URL}/crypto/recover?seed_phrase=${encodeURIComponent(seedPhrase)}`, { method: 'POST' });
            if (res.ok) setWallet(await res.json());
        } catch (error: any) { alert('Error: ' + error.message); }
    }

    async function fetchDocuments() {
        try {
            const res = await fetch(`${API_URL}/documents`);
            if (res.ok) {
                const data = await res.json();
                setDocuments(data.documents || []);
            }
        } catch (error) { console.error(error); }
    }

    async function fetchNotes() {
        try {
            const res = await fetch(`${API_URL}/notes`);
            if (res.ok) {
                const data = await res.json();
                setNotes(data.notes || []);
            }
        } catch (error) { console.error(error); }
    }

    async function runBenchmarks() {
        try {
            const [encRes, ollamaRes] = await Promise.all([
                fetch(`${API_URL}/benchmark/encryption`),
                fetch(`${API_URL}/benchmark/ollama`)
            ]);
            setBenchmarks({
                encryption: await encRes.json(),
                ollama: await ollamaRes.json()
            });
        } catch (error: any) { alert('Error: ' + error.message); }
    }

    async function loadFinance() {
        try {
            const res = await fetch(`${API_URL}/finance/summary`);
            if (res.ok) {
                setFinanceData(await res.json());
            }
        } catch (error) { console.error(error); }
    }

    async function executeBrowserGo() {
        if (!browserUrl) return;
        setBrowserStatus(`Connecting via ${browserMode}...`);
        setBrowserContent(null);

        try {
            const res = await fetch(`${API_URL}/browser/browse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: browserUrl, mode: browserMode })
            });
            const data = await res.json();

            if (data.success) {
                setBrowserContent(data);
                setBrowserStatus(`Connected via ${browserMode.toUpperCase()} | Sanitized ✅`);
            } else {
                setBrowserContent({ error: data.error });
                setBrowserStatus('Connection Error');
            }
        } catch (error: any) {
            setBrowserContent({ error: error.message });
            setBrowserStatus('Error');
        }
    }

    // --- Render ---

    if (!unlocked) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-8">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full border border-white/20">
                    <h1 className="text-4xl font-bold text-white mb-6 text-center">🔐 Sentinel Vault</h1>
                    <p className="text-white/80 mb-6 text-center">POC - Password Manager + Crypto Wallets</p>
                    <input
                        type="password"
                        value={masterPassword}
                        onChange={(e) => setMasterPassword(e.target.value)}
                        className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Master Password"
                        onKeyDown={(e) => e.key === 'Enter' && unlockVault()}
                    />
                    <button onClick={unlockVault} className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-semibold px-6 py-3 rounded-lg hover:from-purple-600 hover:to-blue-600 transition-all">
                        Unlock Vault
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-4xl font-bold text-white">🔐 Sentinel Vault POC</h1>
                    <button onClick={() => setUnlocked(false)} className="bg-red-500/80 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-all">
                        Lock Vault
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Vault Section */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h2 className="text-2xl font-semibold text-white mb-4">💾 Password Vault</h2>
                        <div className="space-y-3 mb-6">
                            <input type="text" value={service} onChange={(e) => setService(e.target.value)} className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2" placeholder="Service" />
                            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2" placeholder="Username" />
                            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2" placeholder="Password" />
                            <button onClick={savePassword} className="w-full bg-green-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-green-600 transition-all">Save Password</button>
                        </div>
                        <div className="border-t border-white/20 pt-4">
                            <h3 className="text-lg font-semibold text-white mb-3">Saved Passwords</h3>
                            <div className="space-y-2 max-h-48 overflow-y-auto">
                                {services.map((svc: any, i) => (
                                    <div key={i} className="bg-white/10 rounded-lg p-3 flex justify-between items-center">
                                        <div><p className="text-white font-medium">{svc.service}</p><p className="text-white/60 text-sm">{svc.username}</p></div>
                                        <button onClick={() => getPassword(svc.service)} className="bg-blue-500/80 text-white px-3 py-1 rounded text-sm">Show</button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Password Analysis */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h2 className="text-2xl font-semibold text-white mb-4">🤖 Analysis</h2>
                        <input type="text" value={analyzePassword} onChange={(e) => setAnalyzePassword(e.target.value)} className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 mb-3" placeholder="Analyze password..." />
                        <button onClick={analyzePasswordStrength} className="w-full bg-purple-500 text-white font-semibold px-4 py-2 rounded-lg mb-4">Analyze Strength</button>
                        {analysis && (
                            <div className="bg-white/10 rounded-lg p-4">
                                <div className="flex justify-between font-bold text-white mb-2">
                                    <span>Score:</span> <span className={analysis.score >= 80 ? 'text-green-400' : 'text-yellow-400'}>{analysis.score}/100</span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-sm text-white/80">
                                    {analysis.issues?.map((issue: string, i: number) => <div key={i} className="text-red-300">• {issue}</div>)}
                                    {analysis.suggestions?.map((s: string, i: number) => <div key={i} className="text-blue-300">• {s}</div>)}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Crypto Wallet */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h2 className="text-2xl font-semibold text-white mb-4">🪙 Crypto Wallet</h2>
                        <div className="flex gap-2 mb-4">
                            <button onClick={generateWallet} className="flex-1 bg-gradient-to-r from-orange-500 to-pink-500 text-white font-semibold px-4 py-2 rounded-lg">New Wallet</button>
                            <button onClick={recoverWallet} className="flex-1 bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg">Recover</button>
                        </div>
                        <input type="text" value={seedPhrase} onChange={(e) => setSeedPhrase(e.target.value)} className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 mb-4" placeholder="Seed Phrase" />

                        {wallet && (
                            <div className="bg-white/10 rounded-lg p-4 space-y-3">
                                {wallet.seed_phrase && <div className="bg-red-500/20 p-2 rounded text-xs text-red-300 break-all font-mono border border-red-500/30">SEED: {wallet.seed_phrase}</div>}
                                {['bitcoin', 'ethereum', 'polygon', 'solana'].map((chain) => wallet.wallets?.[chain] && (
                                    <div key={chain} className="flex justify-between items-center border-t border-white/10 pt-2">
                                        <div>
                                            <span className="text-white/60 capitalize text-sm">{chain}</span>
                                            <p className="text-white text-xs font-mono w-48 truncate opacity-70">{wallet.wallets[chain].address}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-white font-bold">{wallet.wallets[chain].balance?.toFixed(4)}</div>
                                            <div className="text-white/40 text-xs">${wallet.wallets[chain].balance_usd?.toFixed(2)}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Document Vault */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h2 className="text-2xl font-semibold text-white mb-4">📄 Documents</h2>
                        <div
                            className="border-2 border-dashed border-white/30 rounded-lg p-6 text-center hover:border-purple-500 transition-all cursor-pointer bg-white/5 mb-4"
                            onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('border-purple-500'); }}
                            onDragLeave={(e) => { e.currentTarget.classList.remove('border-purple-500'); }}
                            onDrop={async (e) => {
                                e.preventDefault();
                                const file = e.dataTransfer.files[0];
                                if (!file) return;
                                const formData = new FormData();
                                formData.append('file', file);
                                formData.append('category', 'general');
                                try {
                                    const res = await fetch(`${API_URL}/documents/upload`, { method: 'POST', body: formData });
                                    if ((await res.json()).success) { alert('Uploaded!'); fetchDocuments(); }
                                } catch (e) { alert('Error uploading'); }
                            }}
                        >
                            <div className="text-4xl mb-2">📁</div>
                            <p className="text-white/60 text-sm">Drag & Drop to Encrypt</p>
                        </div>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                            {documents.map((doc: any) => (
                                <div key={doc.id} className="bg-white/5 rounded p-2 flex justify-between items-center">
                                    <span className="text-white text-sm truncate w-40">{doc.filename}</span>
                                    <span className="text-white/40 text-xs">{doc.category}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Encrypted Notes */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 lg:col-span-2">
                        <h2 className="text-2xl font-semibold text-white mb-4">📝 Encrypted Notes</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <input id="note-title" type="text" placeholder="Title" className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-2 text-white mb-2" />
                                <textarea id="note-content" placeholder="Markdown content..." className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-2 text-white h-32"></textarea>
                                <button onClick={async () => {
                                    const title = (document.getElementById('note-title') as any).value;
                                    const content = (document.getElementById('note-content') as any).value;
                                    if (!title) return;
                                    await fetch(`${API_URL}/notes`, {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                        body: new URLSearchParams({ title, content })
                                    });
                                    fetchNotes();
                                }} className="mt-2 bg-purple-500 text-white px-4 py-2 rounded">Save Note</button>
                            </div>
                            <div className="max-h-60 overflow-y-auto space-y-2">
                                {notes.map((note: any) => (
                                    <div key={note.id} className="bg-white/5 p-3 rounded hover:bg-white/10">
                                        <h4 className="text-white font-bold">{note.title}</h4>
                                        <p className="text-white/60 text-xs truncate">{note.content_length} chars</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Secure Browser (Triad) */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 lg:col-span-2">
                        <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
                            🦅 Secure Browser <span className="text-xs font-normal text-white/40 bg-white/10 px-2 py-0.5 rounded">Triad Architecture</span>
                        </h2>

                        {/* Mode Selector */}
                        <div className="flex gap-4 mb-4">
                            {[
                                { id: 'clear', icon: '🌐', label: 'Clear', sub: 'Direct' },
                                { id: 'velocity', icon: '⚡', label: 'Velocity', sub: 'Proxy/VPN' },
                                { id: 'ghost', icon: '👻', label: 'Ghost', sub: 'Nym Mixnet' },
                                { id: 'deep', icon: '🕸️', label: 'Deep', sub: 'I2P Network' }
                            ].map(m => (
                                <button
                                    key={m.id}
                                    onClick={() => setBrowserMode(m.id)}
                                    className={`flex-1 py-3 rounded-lg border transition-all flex flex-col items-center gap-1
                                        ${browserMode === m.id
                                            ? 'bg-white/20 border-blue-500 ring-2 ring-blue-500'
                                            : 'bg-white/5 border-white/20 hover:bg-white/10'}`}
                                >
                                    <span className="text-2xl">{m.icon}</span>
                                    <span className="text-white font-medium">{m.label}</span>
                                    <span className="text-white/40 text-xs">{m.sub}</span>
                                </button>
                            ))}
                        </div>

                        {/* URL Bar */}
                        <div className="flex gap-2 mb-4">
                            <input
                                type="text"
                                value={browserUrl}
                                onChange={(e) => setBrowserUrl(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && executeBrowserGo()}
                                placeholder="https://example.com"
                                className="flex-1 bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white font-mono text-sm"
                            />
                            <button onClick={executeBrowserGo} className="px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg">Go ➔</button>
                        </div>

                        {/* Status */}
                        <div className="flex justify-between items-center bg-black/40 rounded-t-lg px-4 py-2 border-b border-white/10">
                            <span className="text-xs font-mono text-white/60">{browserStatus}</span>
                            <div className="flex gap-2">
                                <span className="text-xs bg-red-500/20 text-red-300 px-2 rounded">JS Disabled</span>
                                <span className="text-xs bg-green-500/20 text-green-300 px-2 rounded">Sanitized</span>
                            </div>
                        </div>

                        {/* Viewport */}
                        <div className="bg-white/5 rounded-b-lg min-h-[400px] border border-white/10 border-t-0 p-4 overflow-auto">
                            {browserContent ? (
                                browserContent.error ? (
                                    <div className="text-red-400 text-center py-20">❌ {browserContent.error}</div>
                                ) : (
                                    <div className="bg-white text-black p-8 rounded-lg shadow-inner min-h-full font-serif">
                                        <h1 className="text-3xl font-bold mb-4 border-b pb-2">{browserContent.title}</h1>
                                        <div dangerouslySetInnerHTML={{ __html: browserContent.content }} />
                                    </div>
                                )
                            ) : (
                                <div className="text-center py-20 text-white/20">
                                    <h3 className="text-xl mb-2">Secure Viewport</h3>
                                    <p>Enter a URL to browse securely.</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Terminal */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 lg:col-span-2">
                        <h2 className="text-2xl font-semibold text-white mb-4">💻 Command Terminal</h2>
                        <div className="bg-black/50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm text-green-400 mb-4 whitespace-pre-wrap" id="term-out">
                            🔐 Sentinel Vault Terminal{'\n'}$
                        </div>
                        <input
                            type="text"
                            className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-green-400 font-mono"
                            placeholder="vault help"
                            onKeyDown={async (e) => {
                                if (e.key === 'Enter') {
                                    const cmd = e.currentTarget.value;
                                    e.currentTarget.value = '';
                                    const out = document.getElementById('term-out');
                                    if (out) out.innerHTML += cmd + '\n';
                                    const res = await fetch(`${API_URL}/terminal/execute`, {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                        body: new URLSearchParams({ command: cmd })
                                    });
                                    const data = await res.json();
                                    if (out) {
                                        out.innerHTML += (data.output || data.error) + '\n$ ';
                                        out.scrollTop = out.scrollHeight;
                                    }
                                }
                            }}
                        />
                    </div>

                </div>
            </div>
        </div>
    );
}
