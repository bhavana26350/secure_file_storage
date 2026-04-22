import os
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.logger import log_security_event

class CryptoEngine:
    """Handles secure encryption and decryption using AES-256-GCM and PBKDF2."""
    
    def __init__(self):
        self.salt_size = 16
        self.nonce_size = 12

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derives a strong cryptographic key from a user password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt_file(self, file_path: str, password: str) -> str:
        """
        Encrypts a file using AES-256-GCM.
        Returns the path to the newly encrypted file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("The target file does not exist.")

        # Generate cryptographic parameters
        salt = secrets.token_bytes(self.salt_size)
        nonce = secrets.token_bytes(self.nonce_size)
        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)

        # Read plain data
        with open(file_path, "rb") as f:
            data = f.read()

        # Encrypt the data securely
        ciphertext = aesgcm.encrypt(nonce, data, None)

        output_path = file_path + ".enc"
        
        # Package salt + nonce + ciphertext together
        with open(output_path, "wb") as f:
            f.write(salt)
            f.write(nonce)
            f.write(ciphertext)
            
        log_security_event("ENCRYPT_SUCCESS", f"Encrypted {os.path.basename(file_path)}")
        return output_path

    def decrypt_file(self, file_path: str, password: str) -> str:
        """
        Decrypts a file encrypted by this script.
        Returns the path to the decrypted plaintext file.
        """
        if not os.path.exists(file_path) or not file_path.endswith(".enc"):
            raise ValueError("Target is not a valid encrypted file.")

        with open(file_path, "rb") as f:
            file_data = f.read()

        # Extract parameters
        salt = file_data[:self.salt_size]
        nonce = file_data[self.salt_size:self.salt_size + self.nonce_size]
        ciphertext = file_data[self.salt_size + self.nonce_size:]

        key = self._derive_key(password, salt)
        aesgcm = AESGCM(key)

        # Authenticated decryption
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            log_security_event("DECRYPT_FAILED", f"Authentication failed for {os.path.basename(file_path)}")
            raise ValueError("Decryption failed. Incorrect password or corrupted data.")

        output_path = file_path[:-4] # Remove .enc
        with open(output_path, "wb") as f:
            f.write(plaintext)

        log_security_event("DECRYPT_SUCCESS", f"Decrypted {os.path.basename(file_path)}")
        return output_path
