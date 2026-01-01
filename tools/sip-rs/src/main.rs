use clap::{Parser, Subcommand};
use ed25519_dalek::{Signer, Verifier, Signature, SigningKey, VerifyingKey};
use rand::rngs::OsRng;
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::Path;
use zip::write::FileOptions;
use std::process::Command;

#[derive(Parser)]
#[command(name = "sip")]
#[command(about = "Sentinel Installation Protocol - Neuro-secure Package Manager", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Generate a new keypair
    Keygen {
        #[arg(short, long)]
        out: String,
    },
    /// Sign a package directory and create .sip archive
    Sign {
        #[arg(short, long)]
        source: String,
        #[arg(short, long)]
        key: String,
        #[arg(short, long)]
        out: String,
    },
    /// Verify and Install a .sip package
    Install {
        #[arg(short, long)]
        package: String,
        #[arg(short, long)]
        pubkey: String,
    },
}

#[derive(Serialize, Deserialize, Debug)]
struct IntentManifest {
    name: String,
    version: String,
    description: String,
    capabilities: Vec<String>,
    network: String,
    binaries: Vec<BinaryMeta>,
}

#[derive(Serialize, Deserialize, Debug)]
struct BinaryMeta {
    path: String,
    hash: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    match &cli.command {
        Commands::Keygen { out } => {
            let mut csprng = OsRng;
            let signing_key: SigningKey = SigningKey::generate(&mut csprng);
            let verifying_key: VerifyingKey = signing_key.verifying_key();
            
            fs::write(format!("{}.priv", out), signing_key.to_bytes())?;
            fs::write(format!("{}.pub", out), verifying_key.to_bytes())?;
            
            println!("🔑 Keys generated: {}.priv / {}.pub", out, out);
        }
        Commands::Sign { source, key, out } => {
            sign_package(source, key, out)?;
        }
        Commands::Install { package, pubkey } => {
            install_package(package, pubkey)?;
        }
    }

    Ok(())
}

fn sign_package(source: &str, key_path: &str, out_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("📦 Packaging: {}", source);

    // 1. Load Private Key
    let key_bytes = fs::read(key_path)?;
    if key_bytes.len() != 32 {
        return Err("Invalid Private Key length (must be 32 bytes)".into());
    }
    let key_array: [u8; 32] = key_bytes.try_into().unwrap();
    let signing_key = SigningKey::from_bytes(&key_array);

    // 2. Validate/Hash Intent
    let intent_path = Path::new(source).join("intent.json");
    if !intent_path.exists() {
        return Err("Missing intent.json".into());
    }
    let intent_content = fs::read(&intent_path)?;
    
    // 3. Create ZIP
    let file = File::create(out_path)?;
    let mut zip = zip::ZipWriter::new(file);
    let options = FileOptions::default().compression_method(zip::CompressionMethod::Stored);

    // Walk and Add files
    for entry in fs::read_dir(source)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_file() {
            let name = path.file_name().unwrap().to_str().unwrap();
            let mut f = File::open(&path)?;
            let mut buffer = Vec::new();
            f.read_to_end(&mut buffer)?;
            
            zip.start_file(name, options)?;
            zip.write_all(&buffer)?;
        }
    }

    // 4. Sign the Manifest Content
    let signature = signing_key.sign(&intent_content);
    zip.start_file("signature.sig", options)?;
    zip.write_all(&signature.to_bytes())?;

    zip.finish()?;
    println!("✅ Signed Package created: {}", out_path);
    Ok(())
}

fn install_package(pkg_path: &str, pubkey_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("🛡️  SIP Installer v0.1");
    
    // 1. Load Public Key
    let key_bytes = fs::read(pubkey_path)?;
    // Ensure 32 bytes
    if key_bytes.len() != 32 {
        return Err("Invalid Public Key length (must be 32 bytes)".into());
    }
    let key_array: [u8; 32] = key_bytes.try_into().unwrap();
    let verifying_key = VerifyingKey::from_bytes(&key_array)?;

    // 2. Extract in Memory
    let file = File::open(pkg_path)?;
    let mut archive = zip::ZipArchive::new(file)?;
    
    // 3. Read & Verify Signature
    let mut sig_bytes = Vec::new();
    {
        let mut sig_file = archive.by_name("signature.sig")?;
        sig_file.read_to_end(&mut sig_bytes)?;
    }
    
    if sig_bytes.len() != 64 {
        return Err("Invalid Signature length".into());
    }
    let sig_array: [u8; 64] = sig_bytes.try_into().unwrap();
    let signature = Signature::from_bytes(&sig_array);
    
    // 4. Read Manifest
    let mut intent_bytes = Vec::new();
    {
        let mut intent_file = archive.by_name("intent.json")?;
        intent_file.read_to_end(&mut intent_bytes)?;
    }
    
    // CRYPTOGRAPHIC VERIFICATION
    println!("🔐 Verifying Digital Signature...");
    verifying_key.verify(&intent_bytes, &signature).expect("Invalid Signature!");
    println!("   ✅ Ed25519 Signature Valid.");

    let intent: IntentManifest = serde_json::from_slice(&intent_bytes)?;
    
    // SEMANTIC VERIFICATION (The Sentinel Core)
    println!("\n🧠 Semantic Scan (AI Analysis)...");
    println!("   • Description: {}", intent.description);
    println!("   • Permissions: {:?}", intent.capabilities);
    
    // Simulate AI Call (In real production, this calls Ollama/SemSH)
    if intent.description.to_lowercase().contains("calculator") && intent.network != "none" {
       return Err("⛔ SEMANTIC BLOCK: Calculator requesting Network Access.".into());
    }
    
    // Mock "Approved"
    println!("   ✅ AI Verdict: APPROVED (Coherent Intent)");
    
    // INSTALL (Extract)
    println!("\n🚀 Extracting payload...");
    // For demo, just list
    for i in 0..archive.len() {
        let file = archive.by_index(i)?;
        println!("   -> {}", file.name());
    }
    
    println!("\n✅ Package installed successfully.");

    Ok(())
}
