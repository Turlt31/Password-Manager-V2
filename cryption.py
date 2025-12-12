from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
import base64
import os

def deriveMasterKey(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=64 * 1024,
        parallelism=4,
        hash_len=32,
        type=Type.ID
    )
def createMasterPassword(master_password: str):
    """
    Generates:
    - random salt
    - Argon2id login hash (stored)
    - vault_key (used later for AES but NOT stored)
    """
    salt = os.urandom(16)

    loginHash = deriveMasterKey(master_password, salt)

    return {
        "salt": base64.b64encode(salt).decode(),
        "login_hash": base64.b64encode(loginHash).decode(),
        "vault_key": loginHash
    }
def verifyMasterPassword(user_input: str, stored_salt: str, stored_hash: str):
    """
    Returns:
    - True/False if password is correct
    - vault_key (same bytes as stored hash) if correct
    """
    salt = base64.b64decode(stored_salt)
    expected_hash = base64.b64decode(stored_hash)

    derived = deriveMasterKey(user_input, salt)

    if derived == expected_hash:
        return True, derived   # vault_key
    else:
        return False, None

def encrypt_line(vault_key: bytes, plaintext: str) -> str:
    """
    Encrypts a full line of text using AES-256-GCM.
    Returns a string containing nonce + ciphertext
    that you can safely store in your vault file.
    """
    aes = AESGCM(vault_key)
    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode(),
        None  # no associated data
    )

    nonce_b64 = base64.b64encode(nonce).decode()
    ct_b64 = base64.b64encode(ciphertext).decode()

    # format: nonce|ciphertext
    return f"{nonce_b64}|{ct_b64}"
def decrypt_line(vault_key: bytes, encrypted_line: str) -> str:
    """
    Decrypts a previously encrypted line using AES-256-GCM.
    Input must be the same format returned by encrypt_line().
    """
    aes = AESGCM(vault_key)

    nonce_b64, ct_b64 = encrypted_line.split("|", 1)

    nonce = base64.b64decode(nonce_b64)
    ciphertext = base64.b64decode(ct_b64)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode()

def encrypt_note(vault_key: bytes, note_text: str) -> str:
    if not note_text: return ""
    return encrypt_line(vault_key, note_text)
def decrypt_note(vault_key: bytes, file_contents: str) -> str:
    if not file_contents: return ""
    file_contents = file_contents.strip()

    if "|" not in file_contents: return file_contents

    try: return decrypt_line(vault_key, file_contents)
    except Exception: return file_contents

