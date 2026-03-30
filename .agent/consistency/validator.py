#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ZERO-OMISSION-HARNESS: CONSISTENCY VALIDATOR
=============================================================================
Mục đích: Tự động kiểm tra sự đồng bộ giữa Code, Map, Doc, Contract, State
Phiên bản: 1.0.0
Tác giả: Zero-Omission-Harness Team
=============================================================================
"""

import os
import sys
import json
import yaml
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import re

# Add validators directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'validators'))

# Import base classes
from validators.base import (
    Severity, ValidationStatus, ValidationResult, ConsistencyReport,
    ConfigLoader, BaseValidator
)

# Import validators
from code_contract import CodeContractValidator
from state_transition import StateTransitionValidator
from map_code import MapCodeValidator
from doc_reality import DocRealityValidator


# =============================================================================
# FILE HASH TRACKER
# =============================================================================

class FileHashTracker:
    """Theo dõi hash của files để phát hiện thay đổi"""
    
    def __init__(self, cache_file: str = '.agent/consistency/.hash_cache.json'):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, str]:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
    def compute_hash(self, file_path: Path) -> str:
        if not file_path.exists():
            return ""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""
    
    def has_changed(self, file_path: Path) -> bool:
        current_hash = self.compute_hash(file_path)
        cached_hash = self.cache.get(str(file_path), "")
        return current_hash != cached_hash
    
    def update_hash(self, file_path: Path):
        self.cache[str(file_path)] = self.compute_hash(file_path)
        self._save_cache()
    
    def get_changed_files(self, file_list: List[Path]) -> List[Path]:
        return [f for f in file_list if self.has_changed(f)]


# =============================================================================
# MAIN VALIDATOR ORCHESTRATOR
# =============================================================================

class ConsistencyValidator:
    """Orchestrator cho tất cả validators"""
    
    def __init__(self, config_path: str = None):
        self.config = ConfigLoader(config_path)
        self.validators = [
            ContractCodeValidator(self.config),
            MapCodeValidator(self.config),
            DocRealityValidator(self.config),
            StateTransitionValidator(self.config),
        ]
        self.hash_tracker = FileHashTracker()
    
    def run_all(self) -> ConsistencyReport:
        """Chạy tất cả validators với weighted scoring"""
        all_results = []
        
        # Get priority order from config
        priority_1 = self.config.get('validators.priority_1', [])
        priority_2 = self.config.get('validators.priority_2', [])
        
        # Run validators by priority
        for validator_name in priority_1 + priority_2:
            validator = self._get_validator_by_name(validator_name)
            if validator:
                results = validator.validate()
                all_results.extend(results)
        
        # Calculate weighted score (mới)
        score = self._calculate_weighted_score(all_results)
        
        # Count results
        total = len(all_results)
        passed = sum(1 for r in all_results if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in all_results if r.status == ValidationStatus.FAIL)
        warnings = sum(1 for r in all_results if r.status == ValidationStatus.WARNING)
        
        # Determine overall status dựa trên should_block (mới)
        should_block = self._should_block(all_results, score)
        
        if should_block:
            overall_status = ValidationStatus.FAIL
        elif failed > 0:
            overall_status = ValidationStatus.WARNING
        elif warnings > 0:
            overall_status = ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASS
        
        # Check for drift
        drift_detected = any('drift' in r.check_name.lower() or 'sync' in r.check_name.lower() 
                            for r in all_results if r.status != ValidationStatus.PASS)
        
        # Auto-fix if enabled (chỉ safe fixes)
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
        
        # Update hash cache
        self._update_hash_cache()
        
        return report
    
    def _get_validator_by_name(self, name: str):
        """Get validator instance by name"""
        validator_map = {
            'code_contract': self.validators[0] if len(self.validators) > 0 else None,
            'state_transition': self.validators[3] if len(self.validators) > 3 else None,
            'map_code': self.validators[1] if len(self.validators) > 1 else None,
            'doc_reality': self.validators[2] if len(self.validators) > 2 else None,
        }
        return validator_map.get(name)
    
    def _calculate_weighted_score(self, results: List[ValidationResult]) -> float:
        """Tính weighted score dựa trên config"""
        weights = self.config.get('scoring.weights', {
            'code_contract': 40,
            'state_transition': 30,
            'map_code': 15,
            'doc_reality': 15
        })
        
        category_scores = {}
        category_totals = {}
        
        for result in results:
            # Determine category từ check_name
            check_lower = result.check_name.lower()
            if 'contract' in check_lower or 'code_contract' in check_lower:
                category = 'code_contract'
            elif 'state' in check_lower:
                category = 'state_transition'
            elif 'map' in check_lower:
                category = 'map_code'
            elif 'doc' in check_lower:
                category = 'doc_reality'
            else:
                continue
            
            # Score: 100 nếu PASS, 0 nếu FAIL, 50 nếu WARNING
            if result.status == ValidationStatus.PASS:
                score = 100
            elif result.status == ValidationStatus.WARNING:
                score = 50
            else:
                score = 0
            
            category_scores[category] = category_scores.get(category, 0) + score
            category_totals[category] = category_totals.get(category, 0) + 100
        
        # Calculate weighted average
        total_weight = sum(weights.values())
        weighted_score = 0
        
        for category, weight in weights.items():
            if category in category_totals and category_totals[category] > 0:
                category_score = (category_scores[category] / category_totals[category]) * 100
                weighted_score += (category_score * weight / total_weight)
        
        return round(weighted_score, 1)
    
    def _should_block(self, results: List[ValidationResult], score: float) -> bool:
        """Quyết định có nên block pipeline không - conservative approach"""
        blocking_config = self.config.get('blocking', {})
        
        # 1. Check critical errors - ALWAYS block
        critical_failures = [
            r for r in results 
            if r.severity == Severity.CRITICAL and r.status == ValidationStatus.FAIL
        ]
        
        if critical_failures and blocking_config.get('on_critical', True):
            return True
        
        # 2. Check errors
        errors = [
            r for r in results 
            if r.severity == Severity.ERROR and r.status == ValidationStatus.FAIL
        ]
        
        if errors and blocking_config.get('on_error', True):
            # Chỉ block nếu là code_contract hoặc state_transition
            contract_or_state_errors = [
                e for e in errors 
                if 'contract' in e.check_name.lower() or 'state' in e.check_name.lower()
            ]
            if contract_or_state_errors:
                return True
        
        # 3. Score-based blocking (chỉ nếu được enable)
        if blocking_config.get('use_score_as_gate', False):
            threshold = blocking_config.get('threshold_block', 50)
            if score < threshold:
                return True
        
        return False
    
    def _run_auto_fix(self, results: List[ValidationResult]) -> int:
        """Chạy auto-fix cho các issues có thể fix - chỉ safe operations"""
        if not self.config.get('auto_fix.safe_fixes_only', True):
            return 0
        
        fixed_count = 0
        
        # Chỉ auto-fix các categories an toàn
        safe_categories = ['map_code', 'doc_reality']
        
        for validator in self.validators:
            validator_name = type(validator).__name__.lower()
            if any(cat in validator_name for cat in safe_categories):
                if hasattr(validator, 'auto_fix'):
                    fixed_count += validator.auto_fix(results)
        
        return fixed_count
    
    def _update_hash_cache(self):
        """Update hash cache sau khi run"""
        # Update hashes for all tracked files
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
        md.append(f"| Drift Detected | {report.drift_detected} 📉 |")
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
            
            if result.auto_fixable:
                md.append(f"**Auto-Fixable:** {'Yes' if result.auto_fixable else 'No'}\n")
                if result.auto_fixed:
                    md.append("**Auto-Fixed:** ✅ Yes\n")
            
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


# =============================================================================
# AUTO-RUN INTERFACE
# =============================================================================

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


# Auto-run khi được import trong workflow context
AUTO_RUN_ON_IMPORT = False  # Set True để auto-run khi import

if AUTO_RUN_ON_IMPORT and __name__ != '__main__':
    # Chỉ chạy nếu được trigger từ workflow
    try:
        run_validation()
    except Exception as e:
        print(f"Auto-validation failed: {e}")