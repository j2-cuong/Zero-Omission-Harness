#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
CODE-CONTRACT VALIDATOR (Priority 1)
Kiểm tra sự đồng bộ giữa Contract và Code Implementation
=============================================================================
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from validators.base import BaseValidator, ValidationResult, ValidationStatus, Severity


class CodeContractValidator(BaseValidator):
    """
    Validator quan trọng nhất - kiểm tra contract vs code
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.contract_dir = Path('.agent/contracts')
        self.code_extensions = config.get('paths.code', ['.py', '.js', '.ts', '.go', '.java'])
    
    def validate(self) -> List[ValidationResult]:
        """Validate contract ↔ code consistency"""
        results = []
        
        # Check 1: Contract directory exists
        if not self.contract_dir.exists():
            results.append(self._create_result(
                "contract_directory_exists",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "Contract directory not found",
                {"path": str(self.contract_dir)}
            ))
            return results
        
        # Check 2: Extract API endpoints from contracts
        contract_endpoints = self._extract_contract_endpoints()
        
        # Check 3: Extract API endpoints from code
        code_endpoints = self._extract_code_endpoints()
        
        # Check 4: Compare endpoints
        threshold = self.config.get('thresholds.contract_code_match', 100)
        total = len(contract_endpoints) or 1
        match_rate = ((total - len(contract_endpoints - code_endpoints)) / total) * 100
        
        if match_rate < threshold:
            results.append(self._create_result(
                "contract_code_match",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                f"Contract-Code match rate: {match_rate:.1f}% (threshold: {threshold}%)",
                {
                    "match_rate": match_rate,
                    "threshold": threshold,
                    "missing_in_code": list(contract_endpoints - code_endpoints)[:10],
                    "missing_in_contract": list(code_endpoints - contract_endpoints)[:10]
                },
                auto_fixable=False
            ))
        else:
            results.append(self._create_result(
                "contract_code_match",
                ValidationStatus.PASS,
                Severity.INFO,
                f"Contract-Code match rate: {match_rate:.1f}%",
                {"match_rate": match_rate}
            ))
        
        # Check 5: Individual contract files
        for contract_file in self.contract_dir.glob('*.md'):
            code_match = self._check_contract_file_match(contract_file)
            if not code_match:
                results.append(self._create_result(
                    f"contract_file_{contract_file.name}",
                    ValidationStatus.FAIL,
                    Severity.ERROR,
                    f"Contract {contract_file.name} has no matching code",
                    {"file": str(contract_file)},
                    auto_fixable=False
                ))
        
        return results
    
    def _extract_contract_endpoints(self) -> Set[str]:
        """Extract API endpoints từ contract files"""
        endpoints = set()
        if not self.contract_dir.exists():
            return endpoints
        
        for contract_file in self.contract_dir.glob('*.md'):
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Pattern: GET /api/v1/users, POST /api/v1/create
                    pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\)]+)'
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for method, path in matches:
                        endpoints.add(f"{method.upper()} {path}")
            except:
                continue
        
        return endpoints
    
    def _extract_code_endpoints(self) -> Set[str]:
        """Extract API endpoints từ code files"""
        endpoints = set()
        
        for ext in self.code_extensions:
            for code_file in Path('.').rglob(f'*{ext}'):
                if self._should_skip_file(code_file):
                    continue
                
                try:
                    with open(code_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        endpoints.update(self._extract_endpoints_from_content(content, ext))
                except:
                    continue
        
        return endpoints
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Kiểm tra có nên skip file không"""
        skip_patterns = ['node_modules', 'vendor', '.git', '__pycache__', '.map', '.doc']
        return any(skip in str(file_path) for skip in skip_patterns)
    
    def _extract_endpoints_from_content(self, content: str, ext: str) -> Set[str]:
        """Extract endpoints từ content dựa trên extension"""
        endpoints = set()
        
        if ext == '.py':
            # Flask/FastAPI patterns
            patterns = [
                r'@(app|router)\.(get|post|put|delete|patch)\(["\'](/[^"\']+)["\']',
                r'@(?:app|router|api)\.route\(["\'](/[^"\']+)["\']',
            ]
        elif ext in ['.js', '.ts']:
            # Express.js patterns
            patterns = [
                r'(app|router)\.(get|post|put|delete|patch)\(["\'](/[^"\']+)["\']',
            ]
        elif ext == '.go':
            # Gin/Echo patterns
            patterns = [
                r'\.(GET|POST|PUT|DELETE|PATCH)\(["\'](/[^"\']+)["\']',
            ]
        else:
            patterns = []
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    method = match[-2].upper() if len(match) > 2 else match[0].upper()
                    path = match[-1]
                    endpoints.add(f"{method} {path}")
        
        return endpoints
    
    def _check_contract_file_match(self, contract_file: Path) -> bool:
        """Kiểm tra contract file có matching code không"""
        contract_name = contract_file.stem.lower()
        
        for ext in self.code_extensions:
            for code_file in Path('.').rglob(f'*{contract_name}*{ext}'):
                return True
        
        return False
