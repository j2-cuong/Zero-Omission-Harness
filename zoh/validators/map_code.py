"""
Map-Code Validator
Kiểm tra sự đồng bộ giữa Map và Code
"""

import re
from pathlib import Path
from typing import Dict, List, Set

from zoh.validators.base import BaseValidator, ValidationResult, ValidationStatus, Severity


class MapCodeValidator(BaseValidator):
    """Simple validator kiểm tra map vs code"""
    
    def __init__(self, config):
        super().__init__(config)
        self.map_dir = Path('.map')
        self.code_extensions = config.get('paths.code', ['.py', '.js', '.ts', '.go'])
    
    def validate(self) -> List[ValidationResult]:
        """Validate map ↔ code sync"""
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
                ValidationStatus.WARNING,
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
                auto_fixable=True
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
        """Get all code files"""
        code_files = []
        for ext in self.code_extensions:
            code_files.extend(Path('.').rglob(f'*{ext}'))
        return [f for f in code_files if '.git' not in str(f) and 'node_modules' not in str(f)]
    
    def _get_mapped_files(self) -> Set[str]:
        """Extract file names mentioned in map"""
        mapped = set()
        
        for map_file in self.map_dir.rglob('*.md'):
            try:
                with open(map_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for file references
                patterns = [
                    r'([\w_]+)\.(py|js|ts|go|java|rs)',
                    r'`([\w_]+)\.(py|js|ts|go|java|rs)`',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        mapped.add(match[0] if isinstance(match, tuple) else match)
            except:
                pass
        
        return mapped
    
    def auto_fix(self, results: List[ValidationResult]) -> int:
        """Auto-fix map-code drift"""
        fixed = 0
        
        for result in results:
            if result.check_name == "map_code_sync" and result.auto_fixable:
                missing = result.details.get("missing_in_map", [])
                
                # Add missing files to map
                for filename in missing:
                    # Simple fix: append to map index
                    map_index = self.map_dir / "index.md"
                    if map_index.exists():
                        with open(map_index, 'a', encoding='utf-8') as f:
                            f.write(f"\n- {filename} (auto-added)\n")
                        fixed += 1
        
        return fixed
