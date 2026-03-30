#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
CHECKPOINT MANAGER - Rollback & Recovery System
=============================================================================
"""

import os
import shutil
import json
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import hashlib


class CheckpointManager:
    """Quản lý checkpoint và rollback"""
    
    def __init__(self, checkpoint_dir: str = '.checkpoints'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.checkpoint_dir / 'manifest.json'
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> dict:
        """Load manifest từ file"""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'checkpoints': []}
        return {'checkpoints': []}
    
    def _save_manifest(self):
        """Save manifest ra file"""
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2)
    
    def create_checkpoint(self, label: str = None, include_paths: List[str] = None) -> str:
        """
        Tạo checkpoint mới
        
        Args:
            label: Optional label cho checkpoint
            include_paths: Paths to include (default: .agent/, .state/)
        
        Returns:
            checkpoint_id
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        checkpoint_id = f"checkpoint_{timestamp}"
        
        if label:
            checkpoint_id = f"checkpoint_{timestamp}_{label}"
        
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        # Default paths to backup
        if include_paths is None:
            include_paths = ['.agent/', '.state/']
        
        # Copy files
        copied_files = []
        for path_pattern in include_paths:
            source_path = Path(path_pattern)
            if source_path.exists():
                dest_path = checkpoint_path / source_path.name
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, dest_path)
                copied_files.append(path_pattern)
        
        # Create metadata
        metadata = {
            'checkpoint_id': checkpoint_id,
            'timestamp': timestamp,
            'label': label,
            'included_paths': copied_files,
            'file_count': self._count_files(checkpoint_path),
            'size_bytes': self._get_directory_size(checkpoint_path),
            'state_at_checkpoint': self._capture_current_state()
        }
        
        # Save metadata
        with open(checkpoint_path / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Update manifest
        self.manifest['checkpoints'].append(metadata)
        self._cleanup_old_checkpoints()
        self._save_manifest()
        
        print(f"✅ Checkpoint created: {checkpoint_id}")
        print(f"   Files: {metadata['file_count']}")
        print(f"   Size: {metadata['size_bytes'] / 1024:.1f} KB")
        
        return checkpoint_id
    
    def rollback(self, checkpoint_id: str = None, target: str = None) -> bool:
        """
        Rollback to checkpoint
        
        Args:
            checkpoint_id: Specific checkpoint to rollback to
            target: 'latest' or specific checkpoint_id
        
        Returns:
            True if successful
        """
        if checkpoint_id is None and target is None:
            target = 'latest'
        elif target is None:
            target = checkpoint_id
        
        # Find checkpoint
        if target == 'latest':
            if not self.manifest['checkpoints']:
                print("❌ No checkpoints available")
                return False
            checkpoint_data = self.manifest['checkpoints'][-1]
            checkpoint_id = checkpoint_data['checkpoint_id']
        else:
            checkpoint_data = next(
                (cp for cp in self.manifest['checkpoints'] if cp['checkpoint_id'] == target),
                None
            )
            if not checkpoint_data:
                print(f"❌ Checkpoint not found: {target}")
                return False
        
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        
        if not checkpoint_path.exists():
            print(f"❌ Checkpoint directory not found: {checkpoint_path}")
            return False
        
        # Restore files
        for path_pattern in checkpoint_data['included_paths']:
            source_path = checkpoint_path / Path(path_pattern).name
            dest_path = Path(path_pattern)
            
            if source_path.exists():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
                print(f"   Restored: {path_pattern}")
        
        # Create audit entry
        self._create_audit_entry('rollback_executed', {
            'checkpoint_id': checkpoint_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        print(f"✅ Rollback completed to: {checkpoint_id}")
        return True
    
    def list_checkpoints(self) -> List[dict]:
        """List all checkpoints"""
        return self.manifest['checkpoints']
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        
        if checkpoint_path.exists():
            shutil.rmtree(checkpoint_path)
            self.manifest['checkpoints'] = [
                cp for cp in self.manifest['checkpoints'] 
                if cp['checkpoint_id'] != checkpoint_id
            ]
            self._save_manifest()
            print(f"✅ Deleted checkpoint: {checkpoint_id}")
            return True
        
        return False
    
    def _cleanup_old_checkpoints(self, retention_count: int = 10, retention_days: int = 30):
        """Cleanup old checkpoints based on retention policy"""
        from datetime import timedelta
        
        checkpoints = self.manifest['checkpoints']
        
        # Sort by timestamp
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Keep only recent ones
        to_delete = []
        
        # By count
        if len(checkpoints) > retention_count:
            to_delete.extend(checkpoints[retention_count:])
        
        # By age
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        for cp in checkpoints:
            cp_date = datetime.strptime(cp['timestamp'], '%Y%m%d_%H%M%S')
            if cp_date < cutoff_date and cp not in to_delete:
                to_delete.append(cp)
        
        # Delete
        for cp in to_delete:
            self.delete_checkpoint(cp['checkpoint_id'])
    
    def _count_files(self, path: Path) -> int:
        """Count files in directory"""
        count = 0
        for file in path.rglob('*'):
            if file.is_file():
                count += 1
        return count
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        for file in path.rglob('*'):
            if file.is_file():
                total += file.stat().st_size
        return total
    
    def _capture_current_state(self) -> dict:
        """Capture current state for metadata"""
        state_file = Path('.state/STATE.md')
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract phase
                    import re
                    phase_match = re.search(r'phase:\s*(\w+)', content, re.IGNORECASE)
                    return {
                        'phase': phase_match.group(1) if phase_match else 'unknown',
                        'snapshot_hash': hashlib.sha256(content.encode()).hexdigest()[:16]
                    }
            except:
                pass
        return {'phase': 'unknown', 'snapshot_hash': ''}
    
    def _create_audit_entry(self, event: str, data: dict):
        """Create audit trail entry"""
        audit_dir = Path('.state/history')
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        audit_file = audit_dir / f"{timestamp}_{event}.json"
        
        # Limit file size
        audit_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
        
        # Cleanup if too large
        if audit_file.stat().st_size > 100 * 1024:  # 100KB limit
            # Truncate data field
            audit_data['data'] = {'truncated': True, 'reason': 'size_limit'}
            with open(audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2)


# Auto-run interface

def create_checkpoint(label: str = None) -> str:
    """Tạo checkpoint - được gọi tự động bởi workflow"""
    manager = CheckpointManager()
    return manager.create_checkpoint(label)

def rollback_to_checkpoint(checkpoint_id: str = 'latest'):
    """Rollback về checkpoint - được gọi tự động khi cần"""
    manager = CheckpointManager()
    return manager.rollback(target=checkpoint_id)

def list_checkpoints() -> list:
    """Liệt kê các checkpoint"""
    manager = CheckpointManager()
    return manager.list_checkpoints()