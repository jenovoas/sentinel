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

    async function getPassword(serviceName) {
        try {
            const res = await fetch(`${API_URL}/vault/get`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    master_password: masterPassword,
                    service: serviceName
                })
            });

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
                            <h3 className="text-white font-semibold mb-3">Recent Documents</h3>
                            <div className="space-y-2">
                                <div className="bg-white/5 rounded-lg p-3 flex items-center justify-between hover:bg-white/10 transition-all">
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl">📄</span>
                                        <div>
                                            <p className="text-white text-sm font-medium">passport.pdf</p>
                                            <p className="text-white/40 text-xs">Identity • 2.3 MB • Encrypted</p>
                                        </div>
                                    </div>
                                    <button className="text-purple-400 hover:text-purple-300 text-sm">
                                        Download
                                    </button>
                                </div>

                                <div className="bg-white/5 rounded-lg p-3 flex items-center justify-between hover:bg-white/10 transition-all">
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl">📋</span>
                                        <div>
                                            <p className="text-white text-sm font-medium">contract.pdf</p>
                                            <p className="text-white/40 text-xs">Legal • 1.1 MB • Encrypted</p>
                                        </div>
                                    </div>
                                    <button className="text-purple-400 hover:text-purple-300 text-sm">
                                        Download
                                    </button>
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
                </div>
            </div>
        </div>
    );
}
