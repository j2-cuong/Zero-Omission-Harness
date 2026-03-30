#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
DOC-REALITY VALIDATOR (Priority 3)
Simple grep-based validator - kiểm tra sự đồng bộ giữa Doc và Code
=============================================================================
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from validators.base import BaseValidator, ValidationResult, ValidationStatus, Severity

class DocRealityValidator(BaseValidator):
    """
    Simple validator dùng grep để kiểm tra doc vs reality
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.doc_dirs = [Path('.doc'), Path('docs'), Path('.')]
    
    def validate(self) -> List[ValidationResult]:
        """Validate doc ↔ reality bằng grep đơn giản"""
        results = []
        
        # Check 1: Find doc files
        doc_files = self._get_doc_files()
        
        if not doc_files:
            results.append(self._create_result(
                "doc_files_exist",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "No documentation files found",
                {}
            ))
            return results
        
        # Check 2: Check for outdated markers
        outdated_docs = self._check_outdated_docs(doc_files)
        
        if outdated_docs:
            results.append(self._create_result(
                "outdated_doc_markers",
                ValidationStatus.WARNING,
                Severity.WARNING,
                f"{len(outdated_docs)} docs with outdated markers",
                {"outdated_files": outdated_docs[:10]},
                auto_fixable=False  # Không auto-fix content
            ))
        else:
            results.append(self._create_result(
                "outdated_doc_markers",
                ValidationStatus.PASS,
                Severity.INFO,
                "No outdated doc markers found",
                {}
            ))
        
        # Check 3: Feature documentation coverage (simple)
        features_in_code = self._extract_features_from_code()
        features_in_doc = self._extract_features_from_doc(doc_files)
        
        threshold = self.config.get('thresholds.doc_accuracy', 80)
        total = len(features_in_code) or 1
        coverage = (len(features_in_code & features_in_doc) / total) * 100
        
        if coverage < threshold:
            results.append(self._create_result(
                "feature_doc_coverage",
                ValidationStatus.WARNING,  # Warning thay vì FAIL
                Severity.WARNING,
                f"Feature documentation coverage: {coverage:.1f}% (threshold: {threshold}%)",
                {
                    "coverage": coverage,
                    "threshold": threshold,
                    "undocumented_features": list(features_in_code - features_in_doc)[:10]
                },
                auto_fixable=False  # Không auto-fix doc content
            ))
        else:
            results.append(self._create_result(
                "feature_doc_coverage",
                ValidationStatus.PASS,
                Severity.INFO,
                f"Feature documentation coverage: {coverage:.1f}%",
                {"coverage": coverage}
            ))
        
        # Check 4: PROGRESS.md sync with STATE.md
        progress_sync = self._check_progress_sync()
        if not progress_sync:
            results.append(self._create_result(
                "progress_doc_sync",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "PROGRESS.md may be out of sync with STATE.md",
                {},
                auto_fixable=True  # Safe để update timestamp
            ))
        
        return results
    
    def _get_doc_files(self) -> List[Path]:
        """Get tất cả doc files"""
        doc_files = []
        doc_extensions = ['.md']
        exclude_dirs = ['node_modules', 'vendor', '.git', '.map', '.agent', '__pycache__']
        
        for doc_dir in self.doc_dirs:
            if doc_dir.exists():
                for ext in doc_extensions:
                    for file in doc_dir.rglob(f'*{ext}'):
                        if any(skip in str(file) for skip in exclude_dirs):
                            continue
                        doc_files.append(file)
        
        return doc_files
    
    def _check_outdated_docs(self, doc_files: List[Path]) -> List[str]:
        """Check docs có marker outdated không"""
        outdated = []
        markers = ['OUTDATED', 'DEPRECATED', 'TODO: UPDATE', 'NEEDS UPDATE']
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(marker in content for marker in markers):
                        outdated.append(str(doc_file))
            except:
                continue
        
        return outdated
    
    def _extract_features_from_code(self) -> Set[str]:
        """Extract features từ code - chỉ public functions/classes"""
        features = set()
        exclude_dirs = ['node_modules', 'vendor', '.git', '__pycache__', '.map', '.doc']
        
        # Chỉ scan một số file chính
        for code_file in Path('.').rglob('*.py'):
            if any(skip in str(code_file) for skip in exclude_dirs):
                continue
            # Chỉ scan file ở root level hoặc src/
            if code_file.parent.name not in ['.', 'src', 'lib', 'core']:
                continue
            
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract public function names
                    pattern = r'def\s+(\w+)\s*\('
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if not match.startswith('_'):  # Public only
                            features.add(match)
                    
                    # Extract class names
                    pattern = r'class\s+(\w+)'
                    matches = re.findall(pattern, content)
                    for match in matches:
                        features.add(match)
            except:
                continue
            
            # Giới hạn số lượng
            if len(features) > 100:
                break
        
        return features
    
    def _extract_features_from_doc(self, doc_files: List[Path]) -> Set[str]:
        """Extract features từ doc files"""
        features = set()
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract code references trong backticks
                    pattern = r'`(\w+)`'
                    matches = re.findall(pattern, content)
                    features.update(matches)
            except:
                continue
        
        return features
    
    def _check_progress_sync(self) -> bool:
        """Kiểm tra PROGRESS.md có sync với STATE.md không"""
        progress_file = Path('.doc/PROGRESS.md')
        state_file = Path('.agent/STATE.md')
        
        if not progress_file.exists() or not state_file.exists():
            return True  # Skip if either doesn't exist
        
        try:
            # Simple check: extract timestamps
            progress_time = None
            state_time = None
            
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'updated:\s*(.+)', content, re.IGNORECASE)
                if match:
                    progress_time = match.group(1).strip()
            
            with open(state_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'last_updated:\s*(.+)', content, re.IGNORECASE)
                if match:
                    state_time = match.group(1).strip()
            
            # If state is newer than progress by more than 1 hour, may be out of sync
            if progress_time and state_time:
                from datetime import datetime, timedelta
                try:
                    p_time = datetime.fromisoformat(progress_time.replace('Z', '+00:00'))
                    s_time = datetime.fromisoformat(state_time.replace('Z', '+00:00'))
                    if s_time > p_time + timedelta(hours=1):
                        return False
                except:
                    pass
            
            return True
        except:
            return True
    
    def auto_fix(self, results: List[ValidationResult]) -> int:
        """Auto-fix doc issues - chỉ safe operations"""
        fixed_count = 0
        
        for result in results:
            if not result.auto_fixable:
                continue
            
            if 'progress_doc_sync' in result.check_name:
                # Update timestamp in PROGRESS.md
                if self._update_progress_timestamp():
                    fixed_count += 1
        
        return fixed_count
    
    def _update_progress_timestamp(self) -> bool:
        """Update timestamp trong PROGRESS.md"""
        from datetime import datetime
        
        progress_file = Path('.doc/PROGRESS.md')
        if not progress_file.exists():
            return False
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find and update timestamp line
            updated = False
            new_lines = []
            for line in lines:
                if line.lower().startswith('updated:') or line.lower().startswith('last_updated:'):
                    new_lines.append(f"updated: {datetime.utcnow().isoformat()}\n")
                    updated = True
                else:
                    new_lines.append(line)
            
            if not updated:
                # Add timestamp at beginning
                new_lines.insert(0, f"updated: {datetime.utcnow().isoformat()}\n\n")
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            return True
        except:
            return False
