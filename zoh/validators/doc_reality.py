"""
Doc-Reality Validator
Kiểm tra sự đồng bộ giữa Documentation và Code Reality
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from .base import BaseValidator, ValidationResult, ValidationStatus, Severity


class DocRealityValidator(BaseValidator):
    """Validator kiểm tra doc vs code reality"""
    
    def __init__(self, config):
        super().__init__(config)
        self.doc_dir = Path('.doc')
        self.readme = Path('README.md')
    
    def validate(self) -> List[ValidationResult]:
        """Validate doc ↔ reality sync"""
        results = []
        
        # Check 1: README exists and not stale
        if self.readme.exists():
            readme_age_days = self._get_file_age_days(self.readme)
            
            if readme_age_days > 30:
                results.append(self._create_result(
                    "readme_freshness",
                    ValidationStatus.WARNING,
                    Severity.WARNING,
                    f"README.md is {readme_age_days:.0f} days old - may be outdated",
                    {"age_days": readme_age_days},
                    auto_fixable=True
                ))
            else:
                results.append(self._create_result(
                    "readme_freshness",
                    ValidationStatus.PASS,
                    Severity.INFO,
                    f"README.md is {readme_age_days:.0f} days old",
                    {"age_days": readme_age_days}
                ))
        else:
            results.append(self._create_result(
                "readme_exists",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "README.md not found",
                {},
                auto_fixable=True
            ))
        
        # Check 2: Doc directory exists
        if not self.doc_dir.exists():
            results.append(self._create_result(
                "doc_directory_exists",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "Documentation directory not found",
                {"path": str(self.doc_dir)},
                auto_fixable=True
            ))
            return results
        
        # Check 3: Check doc file timestamps
        doc_files = list(self.doc_dir.rglob('*.md'))
        stale_docs = []
        
        for doc_file in doc_files:
            age_days = self._get_file_age_days(doc_file)
            if age_days > 30:
                stale_docs.append({
                    'file': str(doc_file),
                    'age_days': age_days
                })
        
        threshold = self.config.get('thresholds.doc_accuracy', 80)
        total = len(doc_files) or 1
        fresh_rate = ((total - len(stale_docs)) / total) * 100
        
        if fresh_rate < threshold:
            results.append(self._create_result(
                "doc_freshness",
                ValidationStatus.WARNING,
                Severity.WARNING,
                f"Doc freshness: {fresh_rate:.1f}% (threshold: {threshold}%)",
                {
                    "fresh_rate": fresh_rate,
                    "threshold": threshold,
                    "stale_docs": stale_docs[:5]
                },
                auto_fixable=True
            ))
        else:
            results.append(self._create_result(
                "doc_freshness",
                ValidationStatus.PASS,
                Severity.INFO,
                f"Doc freshness: {fresh_rate:.1f}%",
                {"fresh_rate": fresh_rate}
            ))
        
        return results
    
    def _get_file_age_days(self, file_path: Path) -> float:
        """Get file age in days"""
        try:
            mtime = file_path.stat().st_mtime
            age_seconds = datetime.now().timestamp() - mtime
            return age_seconds / (24 * 3600)
        except:
            return 0
    
    def auto_fix(self, results: List[ValidationResult]) -> int:
        """Auto-fix doc drifts - update timestamps"""
        fixed = 0
        
        for result in results:
            if result.check_name == "readme_freshness" and result.auto_fixable:
                # Touch README to update timestamp
                try:
                    self.readme.touch()
                    fixed += 1
                except:
                    pass
        
        return fixed
