# RetailSafe - Secure File Storage for Retail

**Final Year Project**

## Overview
RetailSafe is a secure, enterprise-grade Python Desktop Application designed to protect sensitive retail data (e.g., customer PII, sales reports) using advanced cryptographic standards. This demonstrates the critical importance of "Data at Rest" security in the retail and e-commerce industries.

## Features
- **AES-256-GCM Encryption**: High-level authenticated encryption preventing data tampering.
- **PBKDF2 Key Derivation**: Hardens passwords against brute-force attacks via cryptographic salting and iterative hashing.
- **Secure File Shredding**: Emulates DoD 5220.22-M to securely wipe plaintext files from the disk to prevent forensic recovery.
- **Security Auditing**: Generates a tamper-evident `.log` file tracking encryption and decryption attempts.
- **Modern UI**: Intuitive UI built with `customtkinter`.

## Installation
Ensure you have Python 3.8+ installed.

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/RetailSafe.git
cd RetailSafe

# Install Python requirements
pip install -r requirements.txt
```

## Usage
Start the desktop application using:
```bash
python main.py
```

1. **Encrypt**: Select a file, enter a strong password, and click `Encrypt`. The original file will be securely shredded (wiped) and a new `.enc` file will be generated.
2. **Decrypt**: Select an `.enc` file, enter the original password, and click `Decrypt` to restore your data safely.

## Project Structure
- `main.py`: Graphical User Interface.
- `src/crypto_engine.py`: Core AES and Hash logic.
- `src/file_shredder.py`: Secure file deletion.
- `data/`: Sample retail dummy dataset for demonstrations.

## Documentation
- High-Level Design (HLD) and Low-Level Design (LLD) documents will be stored in the `/docs` folder.
