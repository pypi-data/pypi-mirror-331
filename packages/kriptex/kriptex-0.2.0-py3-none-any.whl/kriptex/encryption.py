import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Cipher import DES3

# AES ile şifreleme fonksiyonu
def encrypt_aes(file_data, key_length, symbols):
    key = hashlib.sha256(''.join(symbols).encode()).digest()[:key_length]
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    encrypted_data = base64.b64encode(iv + cipher.encrypt(pad(file_data.encode(), AES.block_size))).decode()
    return encrypted_data

def decrypt_aes(encrypted_data, key_length, symbols):
    key = hashlib.sha256(''.join(symbols).encode()).digest()[:key_length]
    raw = base64.b64decode(encrypted_data)
    iv = raw[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(raw[AES.block_size:]), AES.block_size).decode()
    return decrypted_data

# RSA ile şifreleme fonksiyonu
def encrypt_rsa(file_data, symbols):
    key = RSA.generate(2048)
    public_key = key.publickey()
    encrypted_data = base64.b64encode(public_key.encrypt(file_data.encode(), 32)[0]).decode()
    return encrypted_data

def decrypt_rsa(encrypted_data, symbols):
    # Özel anahtarın private.pem dosyasından alındığını varsayıyoruz.
    key = RSA.importKey(open("private.pem").read())
    decrypted_data = key.decrypt(base64.b64decode(encrypted_data)).decode()
    return decrypted_data

# SHA256 ile şifreleme fonksiyonu
def encrypt_sha256(file_data, symbols):
    hashed_data = hashlib.sha256(file_data.encode()).hexdigest()
    return hashed_data

def decrypt_sha256(encrypted_data, symbols):
    # SHA256 hash'ini geri döndürme
    return f"SHA256 Hash: {encrypted_data}"

# Yeni bir şifreleme türü ekleyelim, örneğin 3DES (Triple DES)
def encrypt_3des(file_data, key_length, symbols):
    key = hashlib.sha256(''.join(symbols).encode()).digest()[:key_length]
    cipher = DES3.new(key, DES3.MODE_CBC)
    iv = cipher.iv
    encrypted_data = base64.b64encode(iv + cipher.encrypt(pad(file_data.encode(), DES3.block_size))).decode()
    return encrypted_data

def decrypt_3des(encrypted_data, key_length, symbols):
    key = hashlib.sha256(''.join(symbols).encode()).digest()[:key_length]
    raw = base64.b64decode(encrypted_data)
    iv = raw[:DES3.block_size]
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(raw[DES3.block_size:]), DES3.block_size).decode()
    return decrypted_data

# Ana şifreleme fonksiyonu
def encrypt_file(file_data, algorithm, key_length, symbols):
    if algorithm == "AES":
        return encrypt_aes(file_data, key_length, symbols)
    elif algorithm == "RSA":
        return encrypt_rsa(file_data, symbols)
    elif algorithm == "SHA256":
        return encrypt_sha256(file_data, symbols)
    elif algorithm == "3DES":
        return encrypt_3des(file_data, key_length, symbols)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

def decrypt_file(encrypted_data, algorithm, key_length, symbols):
    if algorithm == "AES":
        return decrypt_aes(encrypted_data, key_length, symbols)
    elif algorithm == "RSA":
        return decrypt_rsa(encrypted_data, symbols)
    elif algorithm == "SHA256":
        return decrypt_sha256(encrypted_data, symbols)
    elif algorithm == "3DES":
        return decrypt_3des(encrypted_data, key_length, symbols)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
