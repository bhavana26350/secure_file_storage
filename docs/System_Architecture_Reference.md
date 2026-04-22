# RetailSafe - System Architecture & Working Details

*Use this reference document to build your High-Level Design (HLD) and Low-Level Design (LLD) documents.*

---

## 1. System Overview
**RetailSafe** is a Desktop software utility built to protect sensitive retail infrastructure data (Data at Rest) from unauthorized access. The core functionality relies on Authenticated Encryption (AES-GCM) combined with secure Key Derivation (PBKDF2) and forensic-grade File Shredding. 

---

## 2. High-Level Design (HLD) References

### 2.1 Architecture Layers
1. **Presentation Layer (Frontend)**: `main.py` 
   - A desktop GUI powered by `CustomTkinter`. Handles user input, password strength validation, file selection via Windows Explorer, and alerts.
2. **Business Logic Layer (Backend)**: `crypto_engine.py` & `file_shredder.py`
   - Abstract processes handling bytes of data, key derivation, disk file writing, and secure memory overwrites.
3. **Audit/Logging Layer**: `logger.py`
   - Triggers alongside every major transaction, maintaining a secure append-only log of events for compliance/auditing.

### 2.2 Core Data Flow for Encryption
1. **Input**: User selects plaintext file (`sales_report.csv`) and inputs a text password.
2. **Derivation**: The password goes to PBKDF2HMAC, which generates a mathematical 32-byte (256-bit) encryption key using a randomly generated "Salt" token.
3. **Encryption**: AES-256-GCM uses the derived key and a random "Nonce" to lock the file data.
4. **Assembly**: The Salt, Nonce, and Ciphertext are concatenated and saved as `.enc`.
5. **Shredding**: Instead of standard deletion, `file_shredder.py` overwrites the original `sales_report.csv` disk sectors multiple times with random noise before unlinking it from the hard drive.

---

## 3. Low-Level Design (LLD) Component Breakdown

### Component 1: `main.py` (User Interface)
* **Class `RetailSafeApp(ctk.CTk)`**: Main application loop.
* **`check_password_strength()`**: Validates input string length, casing, and symbol inclusion to classify password status (Weak/Medium/Strong) in real-time.
* **`run_encrypt()` & `run_decrypt()`**: Multi-threaded execution blocks. They spawn background Python threads (`threading.Thread`) so that heavily processing a massive file doesn't freeze the UI. Calls `reset_ui()` upon completion strictly after displaying user dialogue.

### Component 2: `crypto_engine.py` (Security Core)
* **Algorithms**: AES-256-GCM (Galois/Counter Mode for authenticated encryption), SHA-256 (for hashing).
* **Methods**:
  - `_derive_key(password, salt)`: Subjects user password to **480,000 algorithmic iterations** to prevent brute force cracking.
  - `encrypt_file(file_path, password)`: Reads binary `rb`, processes securely, stores `salt + nonce + ciphertext` to standard `wb`. Returns absolute path of new `.enc` file.
  - `decrypt_file(file_path, password)`: Reads binary. Extracts first 16 bytes for Salt, next 12 bytes for Nonce. If the password fails authentication check by AES-GCM (indicating wrong password or tampered file), raises a critical Value Error.

### Component 3: `file_shredder.py` (Data Deletion)
* **Function**: `secure_shred_file(file_path)`
* **Design**: Uses `os.urandom(length)` to replace plaintext data at the byte-level on the disk hardware before sending OS-level `os.remove()` and `os.fsync()` commands. This mimics the United States DoD 5220.22-M wiping standards, stopping software like Recuva or EnCase from recovering deleted customer data.

### Component 4: `logger.py` (Compliance)
* **Function**: `log_security_event(event_type, details)`
* **Design**: Standard `utf-8` text stream appender. Captures datetime standard ISO strings and pushes them to `security_audit.log`. Logs events like `ENCRYPT_SUCCESS` or `DECRYPT_FAILED`.

---

## 4. Required Libraries for LLD Table
If your LLD requires a dependency matrix, here is what is used:
- **`cryptography==42.0.5`**: The official cryptographic primitive toolkit for Python.
- **`customtkinter==5.2.2`**: UI Library for creating modern desktop widgets.
- **`os`, `secrets`, `threading`**: Built-in Python C-bindings and modules acting as intermediate system connectors.

## 5. Security Justification (For your Project Defense)
Why is this project "Enterprise" grade?
- It uses **AES in GCM mode** instead of CBC mode. GCM means if someone maliciously opens the `.enc` file in notepad and alters a single byte to try and corrupt the database, the decryption process will detect the tamper and entirely reject the operation, preventing bad data injection.
- It doesn't rely on basic python `delete`. It utilizes hard-drive sector overwriting to guarantee compliance with Retail standard PCI-DSS (Payment Card Industry Data Security Standard) Data at Rest requirements.
