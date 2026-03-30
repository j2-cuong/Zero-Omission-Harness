#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
VALIDATOR BASE CLASSES
Shared base classes for all validators
=============================================================================
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """Mức độ nghiêm trọng của vấn đề"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Trạng thái validation"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Kết quả của một check đơn lẻ"""
    check_name: str
    status: ValidationStatus
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    auto_fixable: bool = False
    auto_fixed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ConsistencyReport:
    """Báo cáo tổng thể"""
    run_id: str
    timestamp: str
    overall_status: ValidationStatus
    overall_score: float
    total_checks: int
    passed: int
    failed: int
    warnings: int
    results: List[ValidationResult] = field(default_factory=list)
    drift_detected: bool = False
    auto_fixes_applied: int = 0


class ConfigLoader:
    """Tải cấu hình từ YAML files"""
    
    DEFAULT_CONFIG = {
        'thresholds': {
            'contract_code_match': 100,
            'map_file_sync': 95,
            'doc_accuracy': 90,
            'state_consistency': 100
        },
        'auto_fix': {
            'enabled': True,
            'max_drift_percent': 5,
            'allowed_fixes': ['map_update', 'doc_sync']
        },
        'blocking': {
            'on_critical': True,
            'on_error': True,
            'on_warning': False
        },
        'paths': {
            'code': ['.py', '.js', '.ts', '.go', '.java', '.rs'],
            'map': ['.map/', 'ARCHITECTURE.md'],
            'doc': ['.doc/', 'README.md', 'docs/'],
            'contract': ['.agent/contracts/'],
            'state': ['.state/STATE.md', '.state/STATE_RULES.yaml']
        }
    }
    
    def __init__(self, config_path: str = '.agent/consistency/config.yaml'):
        self.config_path = Path(config_path)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Tải cấu hình từ file nếu tồn tại"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    self._merge_config(user_config)
            except Exception as e:
                print(f"⚠️  Warning: Cannot load config file: {e}")
                print("   Using default configuration")
    
    def _merge_config(self, user_config: Dict):
        """Merge user config với default config"""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default=None):
        """Get config value với nested key support"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class BaseValidator:
    """Base class cho tất cả validators"""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.results: List[ValidationResult] = []
    
    def validate(self) -> List[ValidationResult]:
        """Thực thi validation - override ở subclass"""
        raise NotImplementedError
    
    def _create_result(self, name: str, status: ValidationStatus, 
                       severity: Severity, message: str, 
                       details: Dict = None, auto_fixable: bool = False) -> ValidationResult:
        """Helper tạo ValidationResult"""
        return ValidationResult(
            check_name=name,
            status=status,
            severity=severity,
            message=message,
            details=details or {},
            auto_fixable=auto_fixable
        )
