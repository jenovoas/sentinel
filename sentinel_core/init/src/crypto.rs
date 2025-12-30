use chacha20poly1305::{aead::{Aead, KeyInit}, ChaCha20Poly1305, Key, Nonce};
use x25519_dalek::{EphemeralSecret, PublicKey, SharedSecret};
use rand::rngs::OsRng;
use std::error::Error;
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};
use rand::RngCore;

pub struct PqcContext {
    secret: EphemeralSecret,
    public: PublicKey,
}

impl PqcContext {
    pub fn new() -> Self {
        let secret = EphemeralSecret::random_from_rng(OsRng);
        let public = PublicKey::from(&secret);
        Self { secret, public }
    }

    pub fn public_key_base64(&self) -> String {
        BASE64.encode(self.public.as_bytes())
    }

    // In KEM terms, "decapsulate" here means "Complete DH Exchange".
    // Input is the Peer's Public Key (sent in 'ct' field of Auth message).
    pub fn decapsulate(self, peer_pk_base64: &str) -> Result<Vec<u8>, Box<dyn Error>> {
        let peer_bytes = BASE64.decode(peer_pk_base64)?;
        if peer_bytes.len() != 32 {
            return Err("Invalid Public Key Size".into());
        }
        let mut arr = [0u8; 32];
        arr.copy_from_slice(&peer_bytes);
        let peer_pk = PublicKey::from(arr);
        
        // Compute Shared Secret
        let shared_secret = self.secret.diffie_hellman(&peer_pk);
        
        // Use bytes directly as key (X25519 output is 32 bytes, perfect for ChaCha20)
        Ok(shared_secret.as_bytes().to_vec())
    }
}

pub struct SecureSession {
    cipher: ChaCha20Poly1305,
}

impl SecureSession {
    pub fn new(shared_secret: &[u8]) -> Self {
        let key = Key::from_slice(&shared_secret[0..32]);
        let cipher = ChaCha20Poly1305::new(key);
        Self { cipher }
    }

    pub fn encrypt(&self, plaintext: &[u8]) -> Result<String, Box<dyn Error>> {
        let mut nonce_bytes = [0u8; 12];
        // Note: In Init (musl), OsRng uses getrandom usually. rand::thread_rng() uses it too.
        rand::thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let ciphertext = self.cipher.encrypt(nonce, plaintext)
            .map_err(|_| "Encryption failed")?;

        let mut combined = nonce_bytes.to_vec();
        combined.extend(ciphertext);
        
        Ok(BASE64.encode(combined))
    }

    pub fn decrypt(&self, payload_base64: &str) -> Result<Vec<u8>, Box<dyn Error>> {
        let combined = BASE64.decode(payload_base64)?;
        if combined.len() < 12 {
            return Err("Payload too short".into());
        }
        
        let (nonce_bytes, ciphertext) = combined.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);
        
        let plaintext = self.cipher.decrypt(nonce, ciphertext)
            .map_err(|_| "Decryption failed")?;
            
        Ok(plaintext)
    }
}
