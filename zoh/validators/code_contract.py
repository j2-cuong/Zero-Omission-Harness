"""
Code-Contract Validator
Kiểm tra sự đồng bộ giữa Contract và Code Implementation
"""

import re
from pathlib import Path
from typing import Dict, List, Set

from .base import BaseValidator, ValidationResult, ValidationStatus, Severity


class CodeContractValidator(BaseValidator):
    """Validator kiểm tra contract vs code"""
    
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
        
        return results
    
    def _extract_contract_endpoints(self) -> Set[str]:
        """Extract API endpoints from contract files"""
        endpoints = set()
        
        if not self.contract_dir.exists():
            return endpoints
        
        for contract_file in self.contract_dir.glob('*.md'):
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for endpoint patterns: GET /path, POST /path, etc.
                pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]+)'
                matches = re.findall(pattern, content)
                for method, path in matches:
                    endpoints.add(f"{method} {path}")
            except:
                pass
        
        return endpoints
    
    def _extract_code_endpoints(self) -> Set[str]:
        """Extract API endpoints from code files"""
        endpoints = set()
        
        for ext in self.code_extensions:
            for code_file in Path('.').rglob(f'*{ext}'):
                try:
                    with open(code_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for route definitions
                    # Flask/Django/FastAPI patterns
                    patterns = [
                        r'@(?:app|router)\.route\([\'"](/[^\'"]+)[\'"]\s*,\s*methods=\[[\'"](\w+)[\'"]',
                        r'@(app\.)?(get|post|put|delete|patch)\([\'"](/[^\'"]+)[\'"]',
                        r'@router\.(get|post|put|delete|patch)\([\'"](/[^\'"]+)[\'"]',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                if len(match) == 2:
                                    method, path = match
                                    endpoints.add(f"{method.upper()} {path}")
                                elif len(match) == 3:
                                    _, method, path = match
                                    endpoints.add(f"{method.upper()} {path}")
                except:
                    pass
        
        return endpoints
