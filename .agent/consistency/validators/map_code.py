#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
MAP-CODE VALIDATOR (Priority 3)
Simple grep-based validator - kiểm tra sự đồng bộ giữa Map và Code
=============================================================================
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from validators.base import BaseValidator, ValidationResult, ValidationStatus, Severity


class MapCodeValidator(BaseValidator):
    """
    Simple validator dùng grep để kiểm tra map vs code
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.map_dir = Path('.map')
        self.code_extensions = config.get('paths.code', ['.py', '.js', '.ts', '.go'])
    
    def validate(self) -> List[ValidationResult]:
        """Validate map ↔ code sync bằng grep đơn giản"""
        results = []
        
        # Check 1: Map directory exists
        if not self.map_dir.exists():
            results.append(self._create_result(
                "map_directory_exists",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "Map directory not found",
                {"path": str(self.map_dir)}
            ))
            return results
        
        # Check 2: Get all code files
        code_files = self._get_all_code_files()
        code_filenames = {f.stem for f in code_files}
        
        # Check 3: Get all files mentioned in map
        mapped_files = self._get_mapped_files()
        
        # Check 4: Calculate sync rate
        total = len(code_filenames) or 1
        mapped_count = len(code_filenames & mapped_files)
        sync_rate = (mapped_count / total) * 100
        
        threshold = self.config.get('thresholds.map_file_sync', 90)
        
        missing_in_map = code_filenames - mapped_files
        orphaned_maps = mapped_files - code_filenames
        
        if sync_rate < threshold:
            results.append(self._create_result(
                "map_code_sync",
                ValidationStatus.WARNING,  # Warning thay vì FAIL
                Severity.WARNING,
                f"Map-Code sync rate: {sync_rate:.1f}% (threshold: {threshold}%)",
                {
                    "sync_rate": sync_rate,
                    "threshold": threshold,
                    "missing_in_map": list(missing_in_map)[:10],
                    "orphaned_maps": list(orphaned_maps)[:10],
                    "total_code_files": len(code_filenames),
                    "mapped_count": mapped_count
                },
                auto_fixable=True  # Safe để auto-fix
            ))
        else:
            results.append(self._create_result(
                "map_code_sync",
                ValidationStatus.PASS,
                Severity.INFO,
                f"Map-Code sync rate: {sync_rate:.1f}%",
                {"sync_rate": sync_rate}
            ))
        
        return results
    
    def _get_all_code_files(self) -> List[Path]:
        """Get tất cả code files trong project (exclude vendor)"""
        code_files = []
        exclude_dirs = ['node_modules', 'vendor', '.git', '__pycache__', '.map', '.doc']
        
        for ext in self.code_extensions:
            for file in Path('.').rglob(f'*{ext}'):
                if any(skip in str(file) for skip in exclude_dirs):
                    continue
                code_files.append(file)
        
        return code_files
    
    def _get_mapped_files(self) -> Set[str]:
        """Get danh sách files từ map bằng grep đơn giản"""
        mapped_files = set()
        
        # Tìm trong tất cả .md files trong .map/
        for map_file in self.map_dir.rglob('*.md'):
            try:
                with open(map_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Pattern đơn giản: `filename.ext` hoặc links
                    # Tìm các file references
                    patterns = [
                        r'`([^`]+\.(py|js|ts|go|java|cpp|hpp|cs|rs))`',
                        r'\[([^\]]+\.(py|js|ts))\]',
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            filename = match[0] if isinstance(match, tuple) else match
                            # Chỉ lấy stem (không có extension)
                            stem = Path(filename).stem
                            mapped_files.add(stem)
            except:
                continue
        
        # Also check YAML files if exist
        for yaml_file in self.map_dir.rglob('*.yaml'):
            try:
                import yaml
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        # Recursively find file references
                        self._extract_files_from_dict(data, mapped_files)
            except:
                continue
        
        return mapped_files
    
    def _extract_files_from_dict(self, data: dict, result_set: Set[str]):
        """Recursively extract filenames from dict"""
        for key, value in data.items():
            if isinstance(value, str):
                # Check if value looks like a filename
                if any(value.endswith(ext) for ext in self.code_extensions):
                    result_set.add(Path(value).stem)
            elif isinstance(value, dict):
                self._extract_files_from_dict(value, result_set)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        if any(item.endswith(ext) for ext in self.code_extensions):
                            result_set.add(Path(item).stem)
                    elif isinstance(item, dict):
                        self._extract_files_from_dict(item, result_set)
    
    def auto_fix(self, results: List[ValidationResult]) -> int:
        """Auto-fix map sync issues - safe operations only"""
        fixed_count = 0
        
        for result in results:
            if not result.auto_fixable or result.status != ValidationStatus.WARNING:
                continue
            
            if 'map_code_sync' in result.check_name:
                missing = result.details.get('missing_in_map', [])
                if missing:
                    self._append_to_new_files_map(missing)
                    fixed_count += 1
        
        return fixed_count
    
    def _append_to_new_files_map(self, files: List[str]):
        """Append missing files to NEW_FILES.md for review"""
        from datetime import datetime
        
        new_files_map = self.map_dir / 'NEW_FILES.md'
        
        with open(new_files_map, 'a', encoding='utf-8') as f:
            f.write(f"\n## Detected {datetime.utcnow().isoformat()}\n")
            for file in files[:50]:  # Limit to 50
                f.write(f"- [ ] `{file}` - needs to be added to component tree\n")
