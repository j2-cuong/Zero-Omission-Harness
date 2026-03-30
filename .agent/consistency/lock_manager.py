#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
LOCK MANAGER - Simple File-Based Lock với Timeout + Heartbeat
Không cần distributed lock cho single-machine
=============================================================================
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import uuid


class LockManager:
    """Quản lý lock với timeout và heartbeat"""
    
    def __init__(self, lock_file: str = '.state/lock.json'):
        self.lock_file = Path(lock_file)
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_id = str(uuid.uuid4())[:8]
        self.default_timeout_hours = 2
        self.heartbeat_interval_seconds = 300  # 5 minutes
    
    def acquire(self, phase: str, timeout_hours: int = None) -> bool:
        """
        Acquire lock
        
        Args:
            phase: Current phase (coding, testing, etc.)
            timeout_hours: Lock timeout in hours
        
        Returns:
            True if lock acquired successfully
        """
        if timeout_hours is None:
            timeout_hours = self.default_timeout_hours
        
        # Check if lock exists
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r', encoding='utf-8') as f:
                    lock_data = json.load(f)
                
                # Check if expired
                expires_at = datetime.fromisoformat(lock_data['expires_at'])
                if datetime.utcnow() > expires_at:
                    # Lock expired, can take over
                    print(f"⚠️  Previous lock expired (owner: {lock_data.get('owner', 'unknown')})")
                    return self._write_lock(phase, timeout_hours)
                
                # Check if same owner
                if lock_data.get('owner') == self.session_id:
                    # Already have lock, just refresh
                    return self.heartbeat()
                
                # Lock held by another session
                print(f"❌ Lock held by {lock_data.get('owner', 'unknown')} until {lock_data['expires_at']}")
                return False
                
            except (json.JSONDecodeError, KeyError) as e:
                # Corrupted lock file, take over
                print(f"⚠️  Corrupted lock file, taking over")
                return self._write_lock(phase, timeout_hours)
        else:
            return self._write_lock(phase, timeout_hours)
    
    def _write_lock(self, phase: str, timeout_hours: int) -> bool:
        """Write lock file"""
        lock_data = {
            'owner': self.session_id,
            'phase': phase,
            'acquired_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=timeout_hours)).isoformat(),
            'last_heartbeat': datetime.utcnow().isoformat(),
            'heartbeat_interval': self.heartbeat_interval_seconds
        }
        
        with open(self.lock_file, 'w', encoding='utf-8') as f:
            json.dump(lock_data, f, indent=2)
        
        print(f"✅ Lock acquired: {self.session_id} (phase: {phase}, expires: {lock_data['expires_at']})")
        return True
    
    def release(self) -> bool:
        """Release lock"""
        if not self.lock_file.exists():
            print("⚠️  No lock to release")
            return False
        
        try:
            with open(self.lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            
            if lock_data.get('owner') == self.session_id:
                self.lock_file.unlink()
                print(f"✅ Lock released: {self.session_id}")
                
                # Create audit entry
                self._create_audit_entry('lock_release', {'phase': lock_data.get('phase')})
                return True
            else:
                print(f"❌ Cannot release lock owned by {lock_data.get('owner')}")
                return False
                
        except Exception as e:
            print(f"❌ Error releasing lock: {e}")
            return False
    
    def heartbeat(self) -> bool:
        """Refresh lock heartbeat"""
        if not self.lock_file.exists():
            return False
        
        try:
            with open(self.lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            
            if lock_data.get('owner') == self.session_id:
                lock_data['last_heartbeat'] = datetime.utcnow().isoformat()
                # Extend expiry
                lock_data['expires_at'] = (datetime.utcnow() + timedelta(hours=self.default_timeout_hours)).isoformat()
                
                with open(self.lock_file, 'w', encoding='utf-8') as f:
                    json.dump(lock_data, f, indent=2)
                
                return True
            else:
                return False
                
        except:
            return False
    
    def status(self) -> Optional[dict]:
        """Get lock status"""
        if not self.lock_file.exists():
            return None
        
        try:
            with open(self.lock_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def is_locked(self) -> bool:
        """Check if lock is currently held"""
        status = self.status()
        if status is None:
            return False
        
        expires_at = datetime.fromisoformat(status['expires_at'])
        if datetime.utcnow() > expires_at:
            # Expired
            return False
        
        return True
    
    def force_unlock(self, reason: str = 'manual') -> bool:
        """Force unlock (for admin recovery)"""
        if self.lock_file.exists():
            self.lock_file.unlink()
            self._create_audit_entry('lock_force_unlock', {'reason': reason})
            print(f"✅ Lock force-unlocked: {reason}")
            return True
        return False
    
    def _create_audit_entry(self, event: str, data: dict):
        """Create audit trail entry"""
        audit_dir = Path('.state/history')
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        audit_file = audit_dir / f"{timestamp}_{event}.json"
        
        audit_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': self.session_id,
            'data': data
        }
        
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)


# Auto-run interface

def acquire_lock(phase: str, timeout_hours: int = 2) -> bool:
    """Acquire lock - được gọi tự động bởi workflow"""
    manager = LockManager()
    return manager.acquire(phase, timeout_hours)

def release_lock() -> bool:
    """Release lock - được gọi tự động"""
    manager = LockManager()
    return manager.release()

def check_lock_status() -> dict:
    """Check lock status"""
    manager = LockManager()
    return manager.status()

def refresh_heartbeat() -> bool:
    """Refresh heartbeat"""
    manager = LockManager()
    return manager.heartbeat()

def force_unlock(reason: str = 'manual') -> bool:
    """Force unlock"""
    manager = LockManager()
    return manager.force_unlock(reason)