"""
Code-Contract Validator (Refactored to AST-based)
Kiểm tra sự đồng bộ giữa Contract và Code Implementation using AST analysis
"""

from pathlib import Path
from typing import Dict, List, Set, Any

from zoh.validators.base import BaseValidator, ValidationResult, ValidationStatus, Severity
from zoh.validators.ast_parser import UnifiedASTParser


class CodeContractValidator(BaseValidator):
    """Validator kiểm tra contract vs code - Programmatic AST Enforcement"""
    
    def __init__(self, config):
        super().__init__(config)
        self.contract_dir = Path('.agent/contracts')
        self.code_extensions = config.get('paths.code', ['.py', '.js', '.ts', '.jsx', '.tsx'])
        self.ast_parser = UnifiedASTParser()
    
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
        
        # Check 2: Extract API endpoints from contracts (Markdown)
        import re
        contract_endpoints = self._extract_contract_endpoints()
        
        # Check 3: Extract API endpoints from code (AST)
        code_endpoints = self._extract_code_endpoints()
        
        # Check 4: Compare endpoints
        threshold = self.config.get('thresholds.contract_code_match', 100)
        total = len(contract_endpoints) or 1
        missing_in_code = contract_endpoints - code_endpoints
        match_rate = ((total - len(missing_in_code)) / total) * 100
        
        if match_rate < threshold:
            results.append(self._create_result(
                "contract_code_match",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                f"Contract-Code match rate: {match_rate:.1f}% (threshold: {threshold}%)",
                {
                    "match_rate": match_rate,
                    "threshold": threshold,
                    "missing_in_code": list(missing_in_code)[:10],
                    "extra_in_code": list(code_endpoints - contract_endpoints)[:10]
                }
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
        """Extract API endpoints from contract files using simple MD regex"""
        import re
        endpoints = set()
        
        for contract_file in self.contract_dir.glob('*.md'):
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Match patterns: GET /path, POST /path
                pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]+)'
                matches = re.findall(pattern, content)
                for method, path in matches:
                    endpoints.add(f"{method} {path}")
            except:
                pass
        
        return endpoints
    
    def _extract_code_endpoints(self) -> Set[str]:
        """Extract API endpoints from code files using AST Parsers"""
        endpoints = set()
        
        # Search all relevant files
        for ext in self.code_extensions:
            for code_file in Path('.').rglob(f'*{ext}'):
                # Ignore common noise
                if any(x in str(code_file) for x in ('.git', 'node_modules', '.venv', '__pycache__')):
                    continue
                
                try:
                    found = self.ast_parser.get_endpoints(code_file)
                    for item in found:
                        method = item.get('method', 'GET').upper()
                        path = item.get('path', '/')
                        endpoints.add(f"{method} {path}")
                except Exception:
                    # Silently skip failed files to keep validator running
                    continue
        
        return endpoints
