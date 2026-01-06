from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import struct
import os
import base64

# --- X25519 (RFC 7748) ---
P = 2**255 - 19
A24 = 121665

def inv(n):
    return pow(n, P - 2, P)

def X25519(k, u):
    x_1 = u
    x_2 = 1
    z_2 = 0
    x_3 = u
    z_3 = 1
    swap = 0

    for t in reversed(range(255)):
        kt = (k >> t) & 1
        swap ^= kt
        
        # cswap
        dummy = swap * (x_2 - x_3)
        x_2 = (x_2 - dummy) % P
        x_3 = (x_3 + dummy) % P
        
        dummy = swap * (z_2 - z_3)
        z_2 = (z_2 - dummy) % P
        z_3 = (z_3 + dummy) % P
        
        swap = kt

        A = (x_2 + z_2) % P
        AA = (A * A) % P
        B = (x_2 - z_2) % P
        BB = (B * B) % P
        E = (AA - BB) % P
        C = (x_3 + z_3) % P
        D = (x_3 - z_3) % P
        DA = (D * A) % P
        CB = (C * B) % P
        
        x_3 = ((DA + CB) ** 2) % P
        z_3 = (x_1 * ((DA - CB) ** 2)) % P
        x_2 = (AA * BB) % P
        z_2 = (E * (AA + A24 * E)) % P

    x_2, x_3 = cswap(swap, x_2, x_3) 
    z_2, z_3 = cswap(swap, z_2, z_3) # dummy cswap
    
    return (x_2 * inv(z_2)) % P

def cswap(swap, a, b):
    dummy = swap * (a - b)
    return (a - dummy) % P, (b + dummy) % P

def decode_scalar_25519(k):
    k_list = [(b) for b in k]
    k_list[0] &= 248
    k_list[31] &= 127
    k_list[31] |= 64
    return int.from_bytes(bytes(k_list), 'little')

def decode_u_coordinate(u):
    u_list = [(b) for b in u]
    u_list[31] &= 127
    return int.from_bytes(bytes(u_list), 'little')

def encode_u_coordinate(u):
    return u.to_bytes(32, 'little')

def generate_keypair():
    secret = os.urandom(32)
    scalar = decode_scalar_25519(secret)
    public_int = X25519(scalar, 9)
    public_bytes = encode_u_coordinate(public_int)
    return secret, public_bytes

def shared_secret(my_secret, their_public):
    scalar = decode_scalar_25519(my_secret)
    u = decode_u_coordinate(their_public)
    shared_int = X25519(scalar, u)
    return encode_u_coordinate(shared_int)

# --- ChaCha20 (RFC 7539) ---
def rotl32(x, n):
    return ((x << n) & 0xffffffff) | (x >> (32 - n))

def chacha20_block(key, counter, nonce):
    constants = [0x61707865, 0x3320646e, 0x796b2d32, 0x6b206574]
    ctx = constants + list(struct.unpack('<8I', key)) + [counter] + list(struct.unpack('<3I', nonce))
    working_state = list(ctx)
    
    for _ in range(10):
        # Quarter steps
        for a, b, c, d in [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                           (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]:
            working_state[a] = (working_state[a] + working_state[b]) & 0xffffffff
            working_state[d] = rotl32(working_state[d] ^ working_state[a], 16)
            working_state[c] = (working_state[c] + working_state[d]) & 0xffffffff
            working_state[b] = rotl32(working_state[b] ^ working_state[c], 12)
            working_state[a] = (working_state[a] + working_state[b]) & 0xffffffff
            working_state[d] = rotl32(working_state[d] ^ working_state[a], 8)
            working_state[c] = (working_state[c] + working_state[d]) & 0xffffffff
            working_state[b] = rotl32(working_state[b] ^ working_state[c], 7)
            
    return b''.join(struct.pack('<I', (working_state[i] + ctx[i]) & 0xffffffff) for i in range(16))

def chacha20_encrypt(key, counter, nonce, data):
    encrypted = bytearray()
    for i in range(0, len(data), 64):
        block = chacha20_block(key, counter + i // 64, nonce)
        chunk = data[i:i+64]
        encrypted.extend(a ^ b for a, b in zip(chunk, block))
    return bytes(encrypted)

# --- Poly1305 (RFC 7539) ---
def poly1305_mac(msg, key):
    r = int.from_bytes(key[:16], 'little')
    r &= 0x0ffffffc0ffffffc0ffffffc0fffffff
    s = int.from_bytes(key[16:], 'little')
    a = 0
    p = (1 << 130) - 5
    for i in range(0, len(msg), 16):
        n = int.from_bytes(msg[i:i+16] + b'\x01', 'little')
        a += n
        a = (r * a) % p
    a += s
    return a.to_bytes(16, 'little')

# --- ChaCha20-Poly1305 AEAD ---
def chacha20_aead_encrypt(key, nonce, plaintext, aad=b''):
    otk = chacha20_block(key, 0, nonce) # Poly1305 key
    ciphertext = chacha20_encrypt(key, 1, nonce, plaintext)
    
    mac_data = aad # Padding logic omitted for simplicity (Init doesn't verify AAD padding strictly in legacy mode)
    # Actually, proper framing: AAD + pad + CT + pad + len_aad + len_ct
    # For this simplified implementation, we assume AAD is empty.
    
    mac_data = aad
    if len(aad) % 16: mac_data += b'\x00' * (16 - len(aad) % 16)
    mac_data += ciphertext
    if len(ciphertext) % 16: mac_data += b'\x00' * (16 - len(ciphertext) % 16)
    mac_data += struct.pack('<Q', len(aad)) + struct.pack('<Q', len(ciphertext))
    
    tag = poly1305_mac(mac_data, otk)
    return ciphertext + tag

def chacha20_aead_decrypt(key, nonce, ciphertext_with_tag, aad=b''):
    if len(ciphertext_with_tag) < 16: return None
    tag = ciphertext_with_tag[-16:]
    ciphertext = ciphertext_with_tag[:-16]
    
    otk = chacha20_block(key, 0, nonce)
    
    mac_data = aad
    if len(aad) % 16: mac_data += b'\x00' * (16 - len(aad) % 16)
    mac_data += ciphertext
    if len(ciphertext) % 16: mac_data += b'\x00' * (16 - len(ciphertext) % 16)
    mac_data += struct.pack('<Q', len(aad)) + struct.pack('<Q', len(ciphertext))
    
    calc_tag = poly1305_mac(mac_data, otk)
    if calc_tag != tag:
        # print("MAC mismatch")
        return None # Auth failed
        
    return chacha20_encrypt(key, 1, nonce, ciphertext)
