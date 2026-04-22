import os
import secrets
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, after_this_request
from werkzeug.utils import secure_filename

# Import our existing Security Modules
from src.crypto_engine import CryptoEngine
from src.file_shredder import secure_shred_file
from src.logger import log_security_event

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configure Server Workspaces
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

crypto_engine = CryptoEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        flash("No file part uploaded.", "error")
        return redirect(url_for('index'))
        
    file = request.files['file']
    password = request.form.get('password')
    action = request.form.get('action') # 'encrypt' or 'decrypt'
    
    if file.filename == '':
        flash("No selected file.", "error")
        return redirect(url_for('index'))
        
    if not password:
        flash("Password is required.", "error")
        return redirect(url_for('index'))
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    out_path = ""
    try:
        if action == "encrypt":
            # Encrypt
            out_path_raw = crypto_engine.encrypt_file(filepath, password)
            out_filename = os.path.basename(out_path_raw)
            out_path = os.path.join(DOWNLOAD_FOLDER, out_filename)
            os.replace(out_path_raw, out_path) # Move to downloads folder
            
            # Secure shred the uploaded original
            secure_shred_file(filepath)
            
        elif action == "decrypt":
            if not filename.endswith(".enc"):
                flash("You must select a .enc file to decrypt.", "error")
                os.remove(filepath)
                return redirect(url_for('index'))
            
            # Decrypt
            out_path_raw = crypto_engine.decrypt_file(filepath, password)
            out_filename = os.path.basename(out_path_raw)
            out_path = os.path.join(DOWNLOAD_FOLDER, out_filename)
            os.replace(out_path_raw, out_path)
            
            os.remove(filepath)
        else:
            flash("Invalid action.", "error")
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f"Operation Failed: {str(e)}", "error")
        if os.path.exists(filepath):
            os.remove(filepath)
        return redirect(url_for('index'))

    # Serve the file securely, then delete the temporarily processed file
    @after_this_request
    def remove_file(response):
        try:
            os.remove(out_path)
        except Exception as error:
            app.logger.error(f"Error removing or closing downloaded file handle: {error}")
        return response

    return send_file(out_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
