'use client';

import { useState } from 'react';

const API_URL = 'http://localhost:8000';

export default function VaultPage() {
    const [masterPassword, setMasterPassword] = useState('');
    const [unlocked, setUnlocked] = useState(false);

    // Vault state
    const [service, setService] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [services, setServices] = useState([]);

    // Analysis state
    const [analyzePassword, setAnalyzePassword] = useState('');
    const [analysis, setAnalysis] = useState(null);

    // Crypto state
    const [wallet, setWallet] = useState(null);
    const [seedPhrase, setSeedPhrase] = useState('');

    // Benchmarks
    const [benchmarks, setBenchmarks] = useState(null);
    const [documents, setDocuments] = useState([]);  // New: documents list
    const [notes, setNotes] = useState([]);  // New: notes list

    async function unlockVault() {
        try {
            const res = await fetch(`${API_URL}/vault/unlock`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ master_password: masterPassword })
            });

            if (res.ok) {
                setUnlocked(true);
                await loadServices();
            } else {
                alert('Failed to unlock vault');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }

    async function savePassword() {
        try {
            const res = await fetch(`${API_URL}/vault/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    master_password: masterPassword,
                    service,
                    username,
                    password
                })
            });

            if (res.ok) {
                alert('Password saved!');
                setService('');
                setUsername('');
                setPassword('');
                await loadServices();
            }
        } catch (error) {
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

    if (res.ok) {
        const data = await res.json();
        alert(`Password for ${serviceName}: ${data.password}`);
    }
} catch (error) {
    alert('Error: ' + error.message);
}
    }

async function analyzePasswordStrength() {
    try {
        const res = await fetch(`${API_URL}/analyze/password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: analyzePassword })
        });

        if (res.ok) {
            const data = await res.json();
            setAnalysis(data);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function generateWallet() {
    try {
        const res = await fetch(`${API_URL}/crypto/generate`, {
            method: 'POST'
        });

        if (res.ok) {
            const data = await res.json();
            setWallet(data);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function recoverWallet() {
    try {
        const res = await fetch(`${API_URL}/crypto/recover?seed_phrase=${encodeURIComponent(seedPhrase)}`, {
            method: 'POST'
        });

        if (res.ok) {
            const data = await res.json();
            setWallet(data);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function runBenchmarks() {
    try {
        const [encRes, ollamaRes] = await Promise.all([
            fetch(`${API_URL}/benchmark/encryption`),
            fetch(`${API_URL}/benchmark/ollama`)
        ]);

        const encData = await encRes.json();
        const ollamaData = await ollamaRes.json();

        setBenchmarks({
            encryption: encData,
            ollama: ollamaData
        });
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

if (!unlocked) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full border border-white/20">
                <h1 className="text-4xl font-bold text-white mb-6 text-center">
                    🔐 Sentinel Vault
                </h1>
                <p className="text-white/80 mb-6 text-center">POC - Password Manager + Crypto Wallets</p>

                <input
                    type="password"
                    value={masterPassword}
                    onChange={(e) => setMasterPassword(e.target.value)}
                    className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-3 mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Master Password"
                    onKeyPress={(e) => e.key === 'Enter' && unlockVault()}
                />

                <button
                    onClick={unlockVault}
                    className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-semibold px-6 py-3 rounded-lg hover:from-purple-600 hover:to-blue-600 transition-all"
                >
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
                <button
                    onClick={() => setUnlocked(false)}
                    className="bg-red-500/80 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-all"
                >
                    Lock Vault
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Vault Section */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h2 className="text-2xl font-semibold text-white mb-4">💾 Password Vault</h2>

                    <div className="space-y-3 mb-6">
                        <input
                            type="text"
                            value={service}
                            onChange={(e) => setService(e.target.value)}
                            className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Service (e.g., GitHub)"
                        />
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Username"
                        />
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Password"
                        />
                        <button
                            onClick={savePassword}
                            className="w-full bg-green-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-green-600 transition-all"
                        >
                            Save Password
                        </button>
                    </div>

                    <div className="border-t border-white/20 pt-4">
                        <h3 className="text-lg font-semibold text-white mb-3">Saved Passwords</h3>
                        {services.length === 0 ? (
                            <p className="text-white/60">No passwords saved yet</p>
                        ) : (
                            <div className="space-y-2">
                                {services.map((svc, i) => (
                                    <div key={i} className="bg-white/10 rounded-lg p-3 flex justify-between items-center">
                                        <div>
                                            <p className="text-white font-medium">{svc.service}</p>
                                            <p className="text-white/60 text-sm">{svc.username}</p>
                                        </div>
                                        <button
                                            onClick={() => getPassword(svc.service)}
                                            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-all text-sm"
                                        >
                                            Show
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Password Analysis */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h2 className="text-2xl font-semibold text-white mb-4">🤖 Password Analysis (Ollama)</h2>

                    <input
                        type="text"
                        value={analyzePassword}
                        onChange={(e) => setAnalyzePassword(e.target.value)}
                        className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Enter password to analyze"
                    />
                    <button
                        onClick={analyzePasswordStrength}
                        className="w-full bg-purple-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-purple-600 transition-all mb-4"
                    >
                        Analyze Strength
                    </button>

                    {analysis && (
                        <div className="bg-white/10 rounded-lg p-4 space-y-2">
                            <div className="flex justify-between items-center">
                                <span className="text-white font-medium">Score:</span>
                                <span className={`text-lg font-bold ${analysis.score >= 80 ? 'text-green-400' :
                                    analysis.score >= 50 ? 'text-yellow-400' : 'text-red-400'
                                    }`}>
                                    {analysis.score}/100
                                </span>
                            </div>

                            <div className="border-t border-white/20 pt-2">
                                <p className="text-white/80 text-sm mb-1">Checks:</p>
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                    <div className={analysis.length_ok ? 'text-green-400' : 'text-red-400'}>
                                        {analysis.length_ok ? '✓' : '✗'} Length
                                    </div>
                                    <div className={analysis.has_uppercase ? 'text-green-400' : 'text-red-400'}>
                                        {analysis.has_uppercase ? '✓' : '✗'} Uppercase
                                    </div>
                                    <div className={analysis.has_lowercase ? 'text-green-400' : 'text-red-400'}>
                                        {analysis.has_lowercase ? '✓' : '✗'} Lowercase
                                    </div>
                                    <div className={analysis.has_numbers ? 'text-green-400' : 'text-red-400'}>
                                        {analysis.has_numbers ? '✓' : '✗'} Numbers
                                    </div>
                                    <div className={analysis.has_symbols ? 'text-green-400' : 'text-red-400'}>
                                        {analysis.has_symbols ? '✓' : '✗'} Symbols
                                    </div>
                                    <div className={!analysis.has_patterns ? 'text-green-400' : 'text-red-400'}>
                                        {!analysis.has_patterns ? '✓' : '✗'} No Patterns
                                    </div>
                                </div>
                            </div>

                            {analysis.issues && analysis.issues.length > 0 && (
                                <div className="border-t border-white/20 pt-2">
                                    <p className="text-red-400 text-sm font-medium mb-1">Issues:</p>
                                    <ul className="text-white/80 text-sm list-disc list-inside">
                                        {analysis.issues.map((issue, i) => (
                                            <li key={i}>{issue}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {analysis.suggestions && analysis.suggestions.length > 0 && (
                                <div className="border-t border-white/20 pt-2">
                                    <p className="text-blue-400 text-sm font-medium mb-1">Suggestions:</p>
                                    <ul className="text-white/80 text-sm list-disc list-inside">
                                        {analysis.suggestions.map((suggestion, i) => (
                                            <li key={i}>{suggestion}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Crypto Wallet */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h2 className="text-2xl font-semibold text-white mb-4">🪙 Crypto Wallet</h2>

                    <button
                        onClick={generateWallet}
                        className="w-full bg-gradient-to-r from-orange-500 to-pink-500 text-white font-semibold px-4 py-2 rounded-lg hover:from-orange-600 hover:to-pink-600 transition-all mb-4"
                    >
                        Generate New Wallet
                    </button>

                    <div className="mb-4">
                        <input
                            type="text"
                            value={seedPhrase}
                            onChange={(e) => setSeedPhrase(e.target.value)}
                            className="w-full bg-white/20 text-white placeholder-white/50 border border-white/30 rounded-lg px-4 py-2 mb-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="Seed phrase (24 words)"
                        />
                        <button
                            onClick={recoverWallet}
                            className="w-full bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-600 transition-all"
                        >
                            Recover Wallet
                        </button>
                    </div>

                    {wallet && (
                        <div className="bg-white/10 rounded-lg p-4 space-y-3">
                            {wallet.seed_phrase && (
                                <div className="bg-red-500/20 border border-red-500/50 rounded p-3">
                                    <p className="text-red-400 font-bold text-sm mb-2">⚠️ SAVE THIS SEED PHRASE!</p>
                                    <p className="text-white text-xs font-mono break-all">{wallet.seed_phrase}</p>
                                </div>
                            )}

                            {/* Bitcoin */}
                            {wallet.wallets?.bitcoin && (
                                <div className="border-t border-white/20 pt-3">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-white/60 text-sm">Bitcoin (BTC)</span>
                                        <span className="text-orange-400 font-semibold">
                                            {wallet.wallets.bitcoin.balance?.toFixed(6) || '0.000000'} BTC
                                        </span>
                                    </div>
                                    <p className="text-white font-mono text-xs break-all">{wallet.wallets.bitcoin.address}</p>
                                    <p className="text-white/40 text-xs mt-1">
                                        ${wallet.wallets.bitcoin.balance_usd?.toFixed(2) || '0.00'} USD
                                    </p>
                                </div>
                            )}

                            {/* Ethereum */}
                            {wallet.wallets?.ethereum && (
                                <div className="border-t border-white/20 pt-3">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-white/60 text-sm">Ethereum (ETH)</span>
                                        <span className="text-blue-400 font-semibold">
                                            {wallet.wallets.ethereum.balance?.toFixed(6) || '0.000000'} ETH
                                        </span>
                                    </div>
                                    <p className="text-white font-mono text-xs break-all">{wallet.wallets.ethereum.address}</p>
                                    <p className="text-white/40 text-xs mt-1">
                                        ${wallet.wallets.ethereum.balance_usd?.toFixed(2) || '0.00'} USD
                                    </p>
                                </div>
                            )}

                            {/* Polygon */}
                            {wallet.wallets?.polygon && (
                                <div className="border-t border-white/20 pt-3">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-white/60 text-sm">Polygon (MATIC)</span>
                                        <span className="text-purple-400 font-semibold">
                                            {wallet.wallets.polygon.balance?.toFixed(6) || '0.000000'} MATIC
                                        </span>
                                    </div>
                                    <p className="text-white font-mono text-xs break-all">{wallet.wallets.polygon.address}</p>
                                    <p className="text-white/40 text-xs mt-1">
                                        ${wallet.wallets.polygon.balance_usd?.toFixed(2) || '0.00'} USD
                                    </p>
                                </div>
                            )}

                            {/* Solana */}
                            {wallet.wallets?.solana && (
                                <div className="border-t border-white/20 pt-3">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-white/60 text-sm">Solana (SOL)</span>
                                        <span className="text-green-400 font-semibold">
                                            {wallet.wallets.solana.balance?.toFixed(6) || '0.000000'} SOL
                                        </span>
                                    </div>
                                    <p className="text-white font-mono text-xs break-all">{wallet.wallets.solana.address}</p>
                                    <p className="text-white/40 text-xs mt-1">
                                        ${wallet.wallets.solana.balance_usd?.toFixed(2) || '0.00'} USD
                                    </p>
                                </div>
                            )}

                            {/* Portfolio Total */}
                            <div className="border-t-2 border-white/30 pt-3 mt-3">
                                <div className="flex items-center justify-between">
                                    <span className="text-white font-semibold">Total Portfolio</span>
                                    <span className="text-green-400 font-bold text-lg">
                                        ${(
                                            (wallet.wallets?.bitcoin?.balance_usd || 0) +
                                            (wallet.wallets?.ethereum?.balance_usd || 0) +
                                            (wallet.wallets?.polygon?.balance_usd || 0) +
                                            (wallet.wallets?.solana?.balance_usd || 0)
                                        ).toFixed(2)} USD
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Document Vault */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h2 className="text-2xl font-semibold text-white mb-4">📄 Document Vault</h2>

                    {/* Upload Area */}
                    <div
                        className="border-2 border-dashed border-white/30 rounded-lg p-8 text-center hover:border-purple-500 transition-all cursor-pointer bg-white/5"
                        onDragOver={(e) => {
                            e.preventDefault();
                            e.currentTarget.classList.add('border-purple-500', 'bg-purple-500/10');
                        }}
                        onDragLeave={(e) => {
                            e.currentTarget.classList.remove('border-purple-500', 'bg-purple-500/10');
                        }}
                        onDrop={async (e) => {
                            e.preventDefault();
                            e.currentTarget.classList.remove('border-purple-500', 'bg-purple-500/10');

                            const files = e.dataTransfer.files;
                            if (files.length > 0) {
                                const file = files[0];

                                // Upload file
                                const formData = new FormData();
                                formData.append('file', file);
                                formData.append('category', 'general');

                                try {
                                    const response = await fetch('http://localhost:8000/documents/upload', {
                                        method: 'POST',
                                        body: formData
                                    });
                                    const data = await response.json();

                                    if (data.success) {
                                        alert(`✅ ${file.name} uploaded and encrypted!`);
                                        // Refresh documents list
                                        fetchDocuments();
                                    }
                                } catch (error) {
                                    alert('❌ Upload failed');
                                }
                            }
                        }}
                    >
                        <div className="text-6xl mb-4">📁</div>
                        <p className="text-white text-lg mb-2">Drag & Drop Files Here</p>
                        <p className="text-white/60 text-sm">or click to browse</p>
                        <p className="text-white/40 text-xs mt-2">All files are encrypted with AES-256-GCM</p>
                    </div>

                    {/* Categories */}
                    <div className="mt-4 flex gap-2 flex-wrap">
                        <span className="text-white/60 text-sm">Categories:</span>
                        {['General', 'Identity', 'Contracts', 'Receipts', 'Medical', 'Legal'].map(cat => (
                            <button
                                key={cat}
                                className="px-3 py-1 bg-white/10 text-white text-xs rounded-full hover:bg-purple-500/30 transition-all"
                            >
                                {cat}
                            </button>
                        ))}
                    </div>

                    {/* Recent Documents */}
                    <div className="mt-6">
                        <h3 className="text-white font-semibold mb-3">Recent Documents ({documents.length})</h3>
                        <div className="space-y-2">
                            {documents.length === 0 ? (
                                <p className="text-white/40 text-sm text-center py-4">
                                    No documents yet. Upload your first document above!
                                </p>
                            ) : (
                                documents.map((doc: any) => (
                                    <div key={doc.id} className="bg-white/5 rounded-lg p-3 flex items-center justify-between hover:bg-white/10 transition-all">
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">
                                                {doc.category === 'identity' ? '📄' :
                                                    doc.category === 'legal' ? '📋' :
                                                        doc.category === 'medical' ? '🏥' :
                                                            doc.category === 'receipts' ? '🧾' : '📁'}
                                            </span>
                                            <div>
                                                <p className="text-white text-sm font-medium">{doc.filename}</p>
                                                <p className="text-white/40 text-xs">
                                                    {doc.category} • {(doc.size / 1024).toFixed(1)} KB • Encrypted
                                                </p>
                                            </div>
                                        </div>
                                        <button className="text-purple-400 hover:text-purple-300 text-sm">
                                            Download
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Encrypted Notes */}
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                        <h2 className="text-2xl font-semibold text-white mb-4">📝 Encrypted Notes</h2>

                        {/* Create Note */}
                        <div className="mb-6">
                            <input
                                type="text"
                                placeholder="Note title..."
                                className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/40 mb-3"
                                id="note-title"
                            />
                            <textarea
                                placeholder="Write your note in Markdown...

Try:
- [[Link to another note]]
- #tags for organization
- **bold** and *italic*
- # Headings"
                                className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/40 font-mono text-sm h-48 resize-none"
                                id="note-content"
                            />
                            <div className="flex gap-2 mt-3">
                                <button
                                    onClick={async () => {
                                        const title = (document.getElementById('note-title') as HTMLInputElement).value;
                                        const content = (document.getElementById('note-content') as HTMLTextAreaElement).value;

                                        if (!title || !content) {
                                            alert('Please enter title and content');
                                            return;
                                        }

                                        try {
                                            const response = await fetch('http://localhost:8000/notes', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                                body: new URLSearchParams({ title, content })
                                            });
                                            const data = await response.json();

                                            if (data.success) {
                                                alert(`✅ Note "${title}" created and encrypted!`);
                                                (document.getElementById('note-title') as HTMLInputElement).value = '';
                                                (document.getElementById('note-content') as HTMLTextAreaElement).value = '';
                                                // Refresh notes list
                                                fetchNotes();
                                            }
                                        } catch (error) {
                                            alert('❌ Failed to create note');
                                        }
                                    }}
                                    className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-all"
                                >
                                    💾 Save Note
                                </button>
                                <button
                                    onClick={() => {
                                        (document.getElementById('note-title') as HTMLInputElement).value = '';
                                        (document.getElementById('note-content') as HTMLTextAreaElement).value = '';
                                    }}
                                    className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>

                        {/* Notes List */}
                        <div>
                            <h3 className="text-white font-semibold mb-3">Your Notes ({notes.length})</h3>
                            <div className="space-y-2">
                                {notes.length === 0 ? (
                                    <p className="text-white/40 text-sm text-center py-4">
                                        No notes yet. Create your first note above!
                                    </p>
                                ) : (
                                    notes.map((note: any) => (
                                        <div key={note.id} className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-all">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className="text-white font-medium mb-1">{note.title}</h4>
                                                    <p className="text-white/60 text-sm mb-2">
                                                        {note.content_length} characters • {note.links?.length || 0} links • {note.tags?.length || 0} tags
                                                    </p>
                                                    {note.links && note.links.length > 0 && (
                                                        <div className="flex gap-2 flex-wrap mb-2">
                                                            {note.links.map((link: string, i: number) => (
                                                                <span key={i} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                                                                    [[{link}]]
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                    {note.tags && note.tags.length > 0 && (
                                                        <div className="flex gap-2 flex-wrap">
                                                            {note.tags.map((tag: string, i: number) => (
                                                                <span key={i} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-1 rounded">
                                                                    #{tag}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={async () => {
                                                        if (confirm(`Delete note "${note.title}"?`)) {
                                                            try {
                                                                await fetch(`http://localhost:8000/notes/${note.id}`, {
                                                                    method: 'DELETE'
                                                                });
                                                                fetchNotes();
                                                            } catch (error) {
                                                                alert('❌ Failed to delete note');
                                                            }
                                                        }
                                                    }}
                                                    className="text-red-400 hover:text-red-300 text-sm ml-4"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                </div>
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h2 className="text-2xl font-semibold text-white mb-4">📊 Benchmarks</h2>

                    <button
                        onClick={runBenchmarks}
                        className="w-full bg-indigo-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-indigo-600 transition-all mb-4"
                    >
                        Run Benchmarks
                    </button>

                    {benchmarks && (
                        <div className="space-y-4">
                            <div className="bg-white/10 rounded-lg p-4">
                                <h3 className="text-white font-semibold mb-2">Encryption</h3>
                                <div className="text-sm space-y-1">
                                    <div className="flex justify-between">
                                        <span className="text-white/60">Key Derivation:</span>
                                        <span className="text-white">{benchmarks.encryption.key_derivation.average_ms.toFixed(2)}ms</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/60">Encryption:</span>
                                        <span className="text-white">{benchmarks.encryption.encryption.encryption.average_ms.toFixed(3)}ms</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-white/60">Decryption:</span>
                                        <span className="text-white">{benchmarks.encryption.encryption.decryption.average_ms.toFixed(3)}ms</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white/10 rounded-lg p-4">
                                <h3 className="text-white font-semibold mb-2">Ollama Analysis</h3>
                                <div className="text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-white/60">Average:</span>
                                        <span className="text-white">{benchmarks.ollama.overall_average_ms.toFixed(2)}ms</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Command Terminal */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                    <h2 className="text-2xl font-semibold text-white mb-4">💻 Command Terminal</h2>

                    {/* Terminal Output */}
                    <div className="bg-black/50 rounded-lg p-4 mb-4 h-96 overflow-y-auto font-mono text-sm">
                        <div id="terminal-output" className="text-green-400 whitespace-pre-wrap">
                            {`🔐 Sentinel Vault Terminal
Type 'vault help' for available commands

$ `}
                        </div>
                    </div>

                    {/* Command Input */}
                    <div className="flex gap-2">
                        <div className="flex-1 relative">
                            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-green-400 font-mono">$</span>
                            <input
                                type="text"
                                placeholder="vault help"
                                className="w-full bg-black/50 border border-green-500/30 rounded-lg pl-8 pr-4 py-3 text-green-400 placeholder-green-400/40 font-mono text-sm focus:border-green-500 focus:outline-none"
                                id="terminal-input"
                                onKeyDown={async (e) => {
                                    if (e.key === 'Enter') {
                                        const input = e.currentTarget;
                                        const command = input.value.trim();

                                        if (!command) return;

                                        const output = document.getElementById('terminal-output');
                                        if (output) {
                                            output.textContent += command + '\n';
                                        }

                                        input.value = '';

                                        try {
                                            const response = await fetch('http://localhost:8000/terminal/execute', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                                body: new URLSearchParams({ command })
                                            });
                                            const data = await response.json();

                                            if (output) {
                                                output.textContent += data.output + '\n\n$ ';
                                                output.parentElement?.scrollTo(0, output.parentElement.scrollHeight);
                                            }
                                        } catch (error) {
                                            if (output) {
                                                output.textContent += '❌ Error executing command\n\n$ ';
                                            }
                                        }
                                    }
                                }}
                            />
                        </div>
                        <button
                            onClick={() => {
                                const output = document.getElementById('terminal-output');
                                if (output) {
                                    output.textContent = `🔐 Sentinel Vault Terminal\nType 'vault help' for available commands\n\n$ `;
                                }
                            }}
                            className="px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all"
                        >
                            Clear
                        </button>
                    </div>

                    {/* Quick Commands */}
                    <div className="mt-4 flex gap-2 flex-wrap">
                        <span className="text-white/60 text-sm">Quick:</span>
                        {['vault help', 'vault balance', 'vault status', 'vault generate 32'].map(cmd => (
                            <button
                                key={cmd}
                                onClick={async () => {
                                    const input = document.getElementById('terminal-input') as HTMLInputElement;
                                    if (input) {
                                        input.value = cmd;
                                        input.focus();
                                        input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
                                    }
                                }}
                                className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded hover:bg-green-500/30 transition-all font-mono"
                            >
                                {cmd}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Secure Browser (Triad) */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 col-span-1 lg:col-span-2">
                <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
                    🦅 Secure Browser <span className="text-sm font-normal text-white/40 bg-white/10 px-2 py-0.5 rounded">Triad Architecture</span>
                </h2>

                {/* Mode Selector */}
                <div className="flex gap-4 mb-4">
                    <button
                        onClick={() => (window as any).setBrowserMode('clear')}
                        id="mode-clear"
                        className="flex-1 py-3 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 transition-all flex flex-col items-center gap-1 group focus:ring-2 focus:ring-blue-500"
                    >
                        <span className="text-2xl">🌐</span>
                        <span className="text-white font-medium">Clear Mode</span>
                        <span className="text-white/40 text-xs text-center">Direct Connection<br />(Standard)</span>
                    </button>
                    <button
                        onClick={() => (window as any).setBrowserMode('velocity')}
                        id="mode-velocity"
                        className="flex-1 py-3 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 transition-all flex flex-col items-center gap-1 group focus:ring-2 focus:ring-purple-500"
                    >
                        <span className="text-2xl">⚡</span>
                        <span className="text-white font-medium">Velocity</span>
                        <span className="text-white/40 text-xs text-center">Rotating Proxies<br />(Speed + Privacy)</span>
                    </button>
                    <button
                        onClick={() => (window as any).setBrowserMode('ghost')}
                        id="mode-ghost"
                        className="flex-1 py-3 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 transition-all flex flex-col items-center gap-1 group focus:ring-2 focus:ring-orange-500"
                    >
                        <span className="text-2xl">👻</span>
                        <span className="text-white font-medium">Ghost</span>
                        <span className="text-white/40 text-xs text-center">Nym Mixnet<br />(Metadata Proof)</span>
                    </button>
                    <button
                        onClick={() => (window as any).setBrowserMode('deep')}
                        id="mode-deep"
                        className="flex-1 py-3 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 transition-all flex flex-col items-center gap-1 group focus:ring-2 focus:ring-green-500"
                    >
                        <span className="text-2xl">🕸️</span>
                        <span className="text-white font-medium">Deep</span>
                        <span className="text-white/40 text-xs text-center">I2P Network<br />(Decentralized)</span>
                    </button>
                </div>

                {/* Browser Bar */}
                <div className="flex gap-2 mb-4">
                    <input
                        type="text"
                        placeholder="https://example.com or site.i2p"
                        className="flex-1 bg-black/40 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/30 font-mono text-sm focus:border-blue-500 focus:outline-none"
                        id="browser-url"
                        onKeyDown={(e) => e.key === 'Enter' && (document.getElementById('browser-go') as HTMLButtonElement).click()}
                    />
                    <button
                        id="browser-go"
                        onClick={async () => {
                            const urlInput = document.getElementById('browser-url') as HTMLInputElement;
                            const contentDiv = document.getElementById('browser-content');
                            const statusDiv = document.getElementById('browser-status');
                            const mode = (window as any).currentBrowserMode || 'clear';

                            if (!urlInput.value) return;

                            // Reset UI
                            if (contentDiv) contentDiv.innerHTML = '<div class="text-center py-20 text-white/40 animate-pulse">Establishing Secure Connection...</div>';
                            if (statusDiv) statusDiv.textContent = `Connecting via ${mode}...`;

                            try {
                                const response = await fetch('http://localhost:8000/browser/browse', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ url: urlInput.value, mode: mode })
                                });
                                const data = await response.json();

                                if (data.success) {
                                    if (contentDiv) {
                                        // Render Sanitized HTML in Shadow DOM or simple div for POC
                                        contentDiv.innerHTML = `
                                                <div class="bg-white text-black p-8 min-h-[400px] rounded-lg shadow-inner overflow-auto font-serif">
                                                    <h1 class="text-3xl font-bold mb-4 border-b pb-2">${data.title}</h1>
                                                    <div class="prose max-w-none">
                                                        ${data.content}
                                                    </div>
                                                </div>
                                            `;
                                    }
                                    if (statusDiv) statusDiv.innerHTML = `<span class="text-green-400">●</span> Connected via ${mode.toUpperCase()} | Sanitized ✅`;
                                } else {
                                    if (contentDiv) contentDiv.innerHTML = `<div class="text-red-400 text-center py-10">❌ Connection Failed: ${data.error}</div>`;
                                    if (statusDiv) statusDiv.textContent = 'Connection Error';
                                }
                            } catch (error) {
                                if (contentDiv) contentDiv.innerHTML = `<div class="text-red-400 text-center py-10">❌ Error: ${error}</div>`;
                            }
                        }}
                        className="px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all"
                    >
                        Go ➔
                    </button>
                </div>

                {/* Status Bar */}
                <div className="flex justify-between items-center bg-black/40 rounded-t-lg px-4 py-2 border-b border-white/10">
                    <span className="text-xs font-mono text-white/60" id="browser-status">Ready</span>
                    <div className="flex gap-2">
                        <span className="text-xs bg-red-500/20 text-red-300 px-2 rounded">JS Disabled</span>
                        <span className="text-xs bg-green-500/20 text-green-300 px-2 rounded">Sanitized</span>
                    </div>
                </div>

                {/* Content Viewport */}
                <div id="browser-content" className="bg-white/5 rounded-b-lg min-h-[400px] border border-white/10 border-t-0 p-4 relative">
                    <div className="text-center py-20 text-white/20">
                        <h3 className="text-xl mb-2">Secure Viewport</h3>
                        <p>Enter a URL to browse securely.</p>
                        <p className="text-sm mt-4 text-white/10">Scripts & Trackers are stripped automatically.</p>
                    </div>
                </div>

                {/* Inline Script for Mode Selection (POC Hack) */}
                <script dangerouslySetInnerHTML={{
                    __html: `
                        window.currentBrowserMode = 'clear';
                        window.setBrowserMode = function(mode) {
                            window.currentBrowserMode = mode;
                            // Reset styles
                            ['clear', 'velocity', 'ghost', 'deep'].forEach(m => {
                                const btn = document.getElementById('mode-' + m);
                                if(btn) {
                                    btn.classList.remove('ring-2', 'ring-blue-500', 'ring-purple-500', 'ring-orange-500', 'ring-green-500', 'bg-white/20');
                                    btn.classList.add('bg-white/5');
                                }
                            });
                            
                            // Set active style
                            const btn = document.getElementById('mode-' + mode);
                            const color = mode === 'clear' ? 'blue' : mode === 'velocity' ? 'purple' : mode === 'ghost' ? 'orange' : 'green';
                            if(btn) {
                                btn.classList.add('ring-2', 'ring-' + color + '-500', 'bg-white/20');
                                btn.classList.remove('bg-white/5');
                            }
                            
                            document.getElementById('browser-status').textContent = 'Mode selected: ' + mode.toUpperCase();
                        }
                        // Init
                        setTimeout(() => window.setBrowserMode('clear'), 500);
                    `}} />
            </div>
        </div>
    </div>
    </div >
);
}
