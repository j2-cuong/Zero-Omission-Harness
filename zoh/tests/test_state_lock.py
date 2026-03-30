"""
Tests for State File Integrity (Checksum Lock)
"""

import pytest
from pathlib import Path
from zoh.core.state_lock import StateLockManager, StateIntegrityError

@pytest.fixture
def state_lock_mgr(tmp_path):
    return StateLockManager(lock_dir=str(tmp_path / ".state"))

def test_lock_generation_and_verification(state_lock_mgr, tmp_path):
    # Setup test files
    state_file = tmp_path / "STATE.md"
    state_file.write_text("phase: interview\nstatus: active", encoding="utf-8")
    
    machine_file = tmp_path / "STATE_MACHINE.yaml"
    machine_file.write_text("states:\n  - interview", encoding="utf-8")
    
    critical_files = [state_file, machine_file]
    
    # Generate lock
    state_lock_mgr.generate_lock(critical_files)
    assert (Path(state_lock_mgr.lock_dir) / ".lock.sha256").exists()
    
    # Verify (should pass)
    state_lock_mgr.verify_lock(critical_files)

def test_lock_detection_manual_edit(state_lock_mgr, tmp_path):
    state_file = tmp_path / "STATE.md"
    state_file.write_text("phase: interview", encoding="utf-8")
    
    critical_files = [state_file]
    
    # Generate lock
    state_lock_mgr.generate_lock(critical_files)
    
    # Manual Edit (Bypass CLI)
    state_file.write_text("phase: coding", encoding="utf-8")
    
    # Verify (should FAIL)
    with pytest.raises(StateIntegrityError) as excinfo:
        state_lock_mgr.verify_lock(critical_files)
    
    assert "Manual STATE.md editing forbidden" in str(excinfo.value)

def test_line_ending_normalization(state_lock_mgr, tmp_path):
    # Different line endings should result in the same hash if content is same
    file_lf = tmp_path / "file_lf.txt"
    file_lf.write_bytes(b"line1\nline2\n")
    
    file_crlf = tmp_path / "file_crlf.txt"
    file_crlf.write_bytes(b"line1\r\nline2\r\n")
    
    hash_lf = state_lock_mgr._calc_combined_hash([file_lf])
    hash_crlf = state_lock_mgr._calc_combined_hash([file_crlf])
    
    assert hash_lf == hash_crlf
