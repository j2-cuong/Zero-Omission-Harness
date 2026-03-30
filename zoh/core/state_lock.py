"""
ZOH State File Integrity Lock
Calculates SHA-256 for state files to prevent manual tampering
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("zoh.state_lock")

class StateIntegrityError(Exception):
    """Exception raised for manual tampering of state files"""
    pass


class StateLockManager:
    """Manages integrity checks for critical state files"""
    
    def __init__(self, lock_dir: str = ".state"):
        self.lock_dir = Path(lock_dir)
        self.lock_file = self.lock_dir / ".lock.sha256"
        
    def generate_lock(self, files: list[Path]):
        """
        Calculate combined hash for critical files and write to lock file
        Files include: STATE.md, STATE_MACHINE.yaml
        """
        combined_hash = self._calc_combined_hash(files)
        
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file.write_text(combined_hash, encoding="utf-8")
        logger.info(f"Generated integrity lock: {combined_hash[:10]}...")

    def verify_lock(self, files: list[Path]):
        """
        Verify if current file hashes match the locked hash
        """
        if not self.lock_file.exists():
            # If no lock file, we generate one (First run)
            self.generate_lock(files)
            return

        current_hash = self._calc_combined_hash(files)
        locked_hash = self.lock_file.read_text(encoding="utf-8").strip()
        
        if current_hash != locked_hash:
            logger.error(f"\033[91m❌ STATE INTEGRITY VIOLATION DETECTED!\033[0m")
            logger.error(f"Manual edit detected in {', '.join(f.name for f in files if f.exists())}")
            raise StateIntegrityError("CRITICAL: Manual STATE.md editing forbidden. Use 'zoh transition' instead.")

    def _calc_combined_hash(self, files: list[Path]) -> str:
        """Calculate combined SHA-256 hash (Normalizing line endings)"""
        hasher = hashlib.sha256()
        
        for file_path in sorted(files):
            if file_path.exists():
                # Normalize line endings to avoid cross-platform mismatches
                content = file_path.read_text(encoding="utf-8").replace('\r\n', '\n')
                hasher.update(content.encode('utf-8'))
                
        return hasher.hexdigest()
