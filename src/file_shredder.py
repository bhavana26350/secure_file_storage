import os
from src.logger import log_security_event

def secure_shred_file(file_path: str, passes: int = 3):
    """
    Securely deletes a file by overwriting its contents with random data 
    before unlinking it from the filesystem. This simulates DoD 5220.22-M style wiping 
    (though true DoD wiping may require specific byte patterns).
    """
    if not os.path.exists(file_path):
        return

    try:
        length = os.path.getsize(file_path)
        
        with open(file_path, 'r+b') as f:
            for _ in range(passes):
                f.seek(0)
                # Overwrite with random bytes
                f.write(os.urandom(length))
                # Ensure it's written to disk before next pass
                f.flush()
                os.fsync(f.fileno())
                
        # Finally delete the file
        os.remove(file_path)
        log_security_event("SECURE_SHRED", f"Successfully wiped and deleted {os.path.basename(file_path)}")
    except Exception as e:
        log_security_event("SHRED_FAILED", f"Error shredding {os.path.basename(file_path)}: {str(e)}")
        raise
