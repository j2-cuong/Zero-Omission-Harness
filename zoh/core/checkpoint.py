"""
ZOH Checkpoint Manager
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
            Checkpoint ID
        """
        checkpoint_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        if label:
            checkpoint_id = f"{checkpoint_id}_{label}"
        
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        # Default paths to backup
        if include_paths is None:
            include_paths = ['.agent/', '.state/', '.map/', '.doc/']
        
        checkpoint_data = {
            'id': checkpoint_id,
            'timestamp': datetime.utcnow().isoformat(),
            'label': label,
            'files': []
        }
        
        for file_path in include_paths:
            path = Path(file_path)
            if path.exists():
                if path.is_file():
                    dest = checkpoint_path / path.name
                    shutil.copy2(path, dest)
                    checkpoint_data['files'].append(str(file_path))
                elif path.is_dir():
                    dest = checkpoint_path / path.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(path, dest)
                    checkpoint_data['files'].append(str(file_path))
        
        # Save checkpoint metadata
        with open(checkpoint_path / 'checkpoint.yaml', 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(checkpoint_data, f, default_flow_style=False)
        
        # Update manifest
        self.manifest['checkpoints'].append({
            'id': checkpoint_id,
            'timestamp': datetime.utcnow().isoformat(),
            'label': label
        })
        self._save_manifest()
        
        print(f"✅ Checkpoint created: {checkpoint_id}")
        return checkpoint_id
    
    def rollback(self, target: str = 'latest') -> bool:
        """
        Rollback về checkpoint
        
        Args:
            target: Checkpoint ID or 'latest'
        
        Returns:
            True if successful
        """
        if target == 'latest':
            if not self.manifest['checkpoints']:
                print("❌ No checkpoints available")
                return False
            target = self.manifest['checkpoints'][-1]['id']
        
        checkpoint_path = self.checkpoint_dir / target
        
        if not checkpoint_path.exists():
            print(f"❌ Checkpoint not found: {target}")
            return False
        
        # Load checkpoint metadata
        metadata_file = checkpoint_path / 'checkpoint.yaml'
        if metadata_file.exists():
            try:
                import yaml
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                files = metadata.get('files', [])
            except:
                files = []
        else:
            files = []
        
        # Restore files
        restored = 0
        for file_str in files:
            src = checkpoint_path / Path(file_str).name
            dest = Path(file_str)
            
            if src.exists():
                if src.is_file():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    restored += 1
                elif src.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                    restored += 1
        
        print(f"✅ Rolled back to checkpoint: {target}")
        print(f"   Restored {restored} items")
        return True
    
    def list_checkpoints(self) -> List[dict]:
        """Liệt kê các checkpoint"""
        return self.manifest.get('checkpoints', [])
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Xóa một checkpoint"""
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        
        if not checkpoint_path.exists():
            print(f"❌ Checkpoint not found: {checkpoint_id}")
            return False
        
        try:
            shutil.rmtree(checkpoint_path)
            self.manifest['checkpoints'] = [
                cp for cp in self.manifest['checkpoints'] 
                if cp['id'] != checkpoint_id
            ]
            self._save_manifest()
            print(f"✅ Deleted checkpoint: {checkpoint_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting checkpoint: {e}")
            return False


# Auto-run interface
def create_checkpoint(label: str = None) -> str:
    """Tạo checkpoint - được gọi tự động bởi workflow"""
    manager = CheckpointManager()
    return manager.create_checkpoint(label)

def rollback_to_checkpoint(checkpoint_id: str = 'latest') -> bool:
    """Rollback về checkpoint - được gọi tự động khi cần"""
    manager = CheckpointManager()
    return manager.rollback(checkpoint_id)

def list_checkpoints() -> List[dict]:
    """Liệt kê các checkpoint"""
    manager = CheckpointManager()
    return manager.list_checkpoints()
