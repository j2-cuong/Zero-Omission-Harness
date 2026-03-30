"""
State Transition Validator
Kiểm tra tính hợp lệ của state transitions
"""

import re
from pathlib import Path
from typing import Dict, List

from .base import BaseValidator, ValidationResult, ValidationStatus, Severity


class StateTransitionValidator(BaseValidator):
    """Validator kiểm tra state transitions"""
    
    def __init__(self, config):
        super().__init__(config)
        self.state_file = Path('.state/STATE.md')
        self.state_machine_file = Path('.state/STATE_MACHINE.yaml')
    
    def validate(self) -> List[ValidationResult]:
        """Validate state transitions"""
        results = []
        
        # Check 1: State file exists
        if not self.state_file.exists():
            results.append(self._create_result(
                "state_file_exists",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                "STATE.md not found",
                {"path": str(self.state_file)}
            ))
            return results
        
        # Check 2: State machine file exists
        if not self.state_machine_file.exists():
            results.append(self._create_result(
                "state_machine_file_exists",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                "STATE_MACHINE.yaml not found",
                {"path": str(self.state_machine_file)}
            ))
            return results
        
        # Check 3: Parse current state
        current_state = self._parse_state_file()
        
        if current_state['phase'] == 'unknown':
            results.append(self._create_result(
                "state_parse",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                "Cannot parse current state from STATE.md",
                {}
            ))
            return results
        
        # Check 4: Validate state consistency flags
        flags = current_state.get('consistency_flags', {})
        
        for flag_name, flag_value in flags.items():
            if flag_value != 'synced':
                results.append(self._create_result(
                    f"state_flag_{flag_name}",
                    ValidationStatus.WARNING,
                    Severity.WARNING,
                    f"State flag '{flag_name}' is '{flag_value}' (expected: synced)",
                    {"flag": flag_name, "value": flag_value}
                ))
        
        # Check 5: Check for blockers
        blockers = current_state.get('blockers', [])
        
        if blockers and blockers != ['None']:
            results.append(self._create_result(
                "state_blockers",
                ValidationStatus.FAIL,
                Severity.ERROR,
                f"State has {len(blockers)} active blocker(s)",
                {"blockers": blockers[:5]}
            ))
        else:
            results.append(self._create_result(
                "state_blockers",
                ValidationStatus.PASS,
                Severity.INFO,
                "No active blockers",
                {}
            ))
        
        # Overall state check
        if len([r for r in results if r.status == ValidationStatus.FAIL]) == 0:
            results.append(self._create_result(
                "state_valid",
                ValidationStatus.PASS,
                Severity.INFO,
                f"State is valid (phase: {current_state['phase']})",
                {"phase": current_state['phase']}
            ))
        
        return results
    
    def _parse_state_file(self) -> Dict:
        """Parse STATE.md file"""
        result = {
            'phase': 'unknown',
            'status': 'unknown',
            'version': '',
            'consistency_flags': {},
            'blockers': []
        }
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse phase
            phase_match = re.search(r'phase:\s*(\w+)', content, re.IGNORECASE)
            if phase_match:
                result['phase'] = phase_match.group(1)
            
            # Parse status
            status_match = re.search(r'status:\s*(\w+)', content, re.IGNORECASE)
            if status_match:
                result['status'] = status_match.group(1)
            
            # Parse version
            version_match = re.search(r'version:\s*([\w.]+)', content, re.IGNORECASE)
            if version_match:
                result['version'] = version_match.group(1)
            
            # Parse consistency flags
            flag_pattern = r'-\s*(code|map|doc):\s*(\w+)'
            for match in re.finditer(flag_pattern, content, re.IGNORECASE):
                result['consistency_flags'][match.group(1)] = match.group(2)
            
            # Parse blockers
            blockers_section = re.search(r'##\s*Blockers\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
            if blockers_section:
                blockers_text = blockers_section.group(1)
                blockers = [b.strip('- ').strip() for b in blockers_text.strip().split('\n') if b.strip()]
                result['blockers'] = [b for b in blockers if b and b != 'None']
        
        except Exception as e:
            pass
        
        return result
