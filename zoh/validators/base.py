"""
ZOH Validator Base Classes
"""

import os
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


class BaseValidator:
    """Base class cho tất cả validators"""
    
    def __init__(self, config: 'ConfigLoader'):
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
