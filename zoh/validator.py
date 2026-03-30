"""
ZOH Main Validator Orchestrator
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .core.config import ConfigLoader
from .validators.base import (
    Severity, ValidationStatus, ValidationResult, ConsistencyReport
)
from .validators.code_contract import CodeContractValidator
from .validators.map_code import MapCodeValidator
from .validators.doc_reality import DocRealityValidator
from .validators.state_transition import StateTransitionValidator


class FileHashTracker:
    """Theo dõi hash của files để phát hiện thay đổi"""
    
    def __init__(self, cache_file: str = '.agent/consistency/.hash_cache.json'):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load hash cache từ file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save hash cache ra file"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_hash(self, file_path: Path) -> str:
        """Tính hash của file"""
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return ""
    
    def has_changed(self, file_path: Path) -> bool:
        """Kiểm tra xem file có thay đổi không"""
        current_hash = self.get_hash(file_path)
        cached_hash = self.cache.get(str(file_path))
        return current_hash != cached_hash
    
    def update_hash(self, file_path: Path):
        """Update hash cho file trong cache"""
        self.cache[str(file_path)] = self.get_hash(file_path)
        self._save_cache()


class ConsistencyValidator:
    """Orchestrator cho tất cả validators"""
    
    def __init__(self, config_path: str = None):
        self.config = ConfigLoader(config_path or "CONFIG.yaml")
        self.validators = [
            CodeContractValidator(self.config),
            MapCodeValidator(self.config),
            DocRealityValidator(self.config),
            StateTransitionValidator(self.config),
        ]
        self.hash_tracker = FileHashTracker()
    
    def run_all(self) -> ConsistencyReport:
        """Chạy tất cả validators"""
        all_results = []
        
        for validator in self.validators:
            results = validator.validate()
            all_results.extend(results)
        
        # Calculate overall score
        total = len(all_results)
        passed = sum(1 for r in all_results if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in all_results if r.status == ValidationStatus.FAIL)
        warnings = sum(1 for r in all_results if r.status == ValidationStatus.WARNING)
        
        score = (passed / total * 100) if total > 0 else 0
        
        # Determine overall status
        if failed > 0:
            has_critical = any(r.severity == Severity.CRITICAL for r in all_results if r.status == ValidationStatus.FAIL)
            overall_status = ValidationStatus.FAIL if has_critical else ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASS if warnings == 0 else ValidationStatus.WARNING
        
        # Check for drift
        drift_detected = any('drift' in r.check_name.lower() or 'sync' in r.check_name.lower() 
                            for r in all_results if r.status == ValidationStatus.FAIL)
        
        # Auto-fix if enabled
        auto_fixes = 0
        if self.config.get('auto_fix.enabled', True):
            auto_fixes = self._run_auto_fix(all_results)
        
        report = ConsistencyReport(
            run_id=datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
            timestamp=datetime.utcnow().isoformat(),
            overall_status=overall_status,
            overall_score=score,
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            results=all_results,
            drift_detected=drift_detected,
            auto_fixes_applied=auto_fixes
        )
        
        self._update_hash_cache()
        
        return report
    
    def _run_auto_fix(self, results: List[ValidationResult]) -> int:
        """Chạy auto-fix cho các issues có thể fix"""
        fixed_count = 0
        
        for validator in self.validators:
            if hasattr(validator, 'auto_fix'):
                fixed_count += validator.auto_fix(results)
        
        return fixed_count
    
    def _update_hash_cache(self):
        """Update hash cache sau khi run"""
        for ext in self.config.get('paths.code', ['.py', '.js', '.ts']):
            for file in Path('.').rglob(f'*{ext}'):
                self.hash_tracker.update_hash(file)
    
    def generate_report(self, report: ConsistencyReport, output_path: str = None) -> str:
        """Generate báo cáo markdown"""
        if output_path is None:
            output_path = f'.agent/consistency/reports/consistency_{report.run_id}.md'
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        md = []
        md.append("# 🔍 Consistency Validation Report\n")
        md.append(f"**Run ID:** {report.run_id}\n")
        md.append(f"**Timestamp:** {report.timestamp}\n")
        md.append(f"**Overall Status:** {report.overall_status.value.upper()}\n")
        md.append(f"**Overall Score:** {report.overall_score:.1f}/100\n")
        md.append("")
        
        # Summary
        md.append("## 📊 Summary\n")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Total Checks | {report.total_checks} |")
        md.append(f"| Passed | {report.passed} ✅ |")
        md.append(f"| Failed | {report.failed} ❌ |")
        md.append(f"| Warnings | {report.warnings} ⚠️ |")
        md.append(f"| Auto-Fixes Applied | {report.auto_fixes_applied} 🔧 |")
        md.append(f"| Drift Detected | {'Detected 📉' if report.drift_detected else 'None ✅'}")
        md.append("")
        
        # Detailed Results
        md.append("## 🔬 Detailed Results\n")
        
        for result in report.results:
            status_icon = {"pass": "✅", "fail": "❌", "warning": "⚠️", "skipped": "⏭️"}.get(result.status.value, "❓")
            severity_icon = {"info": "ℹ️", "warning": "⚠️", "error": "🔴", "critical": "🚨"}.get(result.severity.value, "❓")
            
            md.append(f"### {status_icon} {result.check_name} {severity_icon}\n")
            md.append(f"**Status:** {result.status.value}\n")
            md.append(f"**Severity:** {result.severity.value}\n")
            md.append(f"**Message:** {result.message}\n")
            
            if result.details:
                md.append("\n**Details:**\n```json")
                md.append(json.dumps(result.details, indent=2, ensure_ascii=False))
                md.append("```\n")
            
            md.append("")
        
        # Recommendations
        if report.failed > 0:
            md.append("## 🎯 Recommendations\n")
            md.append("1. Address all CRITICAL and ERROR issues before proceeding\n")
            md.append("2. Review WARNING issues for potential improvements\n")
            md.append("3. Run `zoh fix` to apply auto-fixes where available\n")
            md.append("")
        
        content = '\n'.join(md)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path


# Auto-run interface
def run_validation(config_path: str = None, output_path: str = None) -> ConsistencyReport:
    """
    Auto-run validation - được gọi tự động bởi workflow
    
    Returns:
        ConsistencyReport với kết quả validation
    """
    validator = ConsistencyValidator(config_path)
    report = validator.run_all()
    
    if output_path:
        validator.generate_report(report, output_path)
    
    # Log kết quả
    print(f"\n{'='*70}")
    print(f"Validation Run ID: {report.run_id}")
    print(f"Overall Score: {report.overall_score:.1f}/100")
    print(f"Status: {report.overall_status.value.upper()}")
    print(f"Passed: {report.passed} | Failed: {report.failed} | Warnings: {report.warnings}")
    print(f"{'='*70}\n")
    
    return report
