#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
STATE-TRANSITION VALIDATOR (Priority 2)
Kiểm tra state transitions hợp lệ và phát hiện invalid states
=============================================================================
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional
from validators.base import BaseValidator, ValidationResult, ValidationStatus, Severity


class StateTransitionValidator(BaseValidator):
    """
    Validator dễ làm - kiểm tra state machine và transitions
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.state_file = Path('.state/STATE.md')
        self.state_machine_file = Path('.state/STATE_MACHINE.yaml')
    
    def validate(self) -> List[ValidationResult]:
        """Validate state transitions"""
        results = []
        
        # Check 1: State files exist
        if not self.state_file.exists():
            results.append(self._create_result(
                "state_file_exists",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                "STATE.md not found",
                {"path": str(self.state_file)}
            ))
            return results
        
        if not self.state_machine_file.exists():
            results.append(self._create_result(
                "state_machine_file_exists",
                ValidationStatus.WARNING,
                Severity.WARNING,
                "STATE_MACHINE.yaml not found",
                {"path": str(self.state_machine_file)}
            ))
        
        # Check 2: Parse current state
        current_state = self._parse_current_state()
        
        if not current_state:
            results.append(self._create_result(
                "state_parseable",
                ValidationStatus.FAIL,
                Severity.CRITICAL,
                "Cannot parse current state from STATE.md",
                {}
            ))
            return results
        
        results.append(self._create_result(
            "state_parseable",
            ValidationStatus.PASS,
            Severity.INFO,
            f"Current state: {current_state.get('phase', 'unknown')}",
            current_state
        ))
        
        # Check 3: Validate against state machine
        if self.state_machine_file.exists():
            sm_results = self._validate_against_state_machine(current_state)
            results.extend(sm_results)
        
        # Check 4: Check invalid state conditions
        invalid_conditions = self._check_invalid_state_conditions(current_state)
        
        if invalid_conditions:
            for condition in invalid_conditions:
                results.append(self._create_result(
                    f"invalid_state_condition_{condition['type']}",
                    ValidationStatus.FAIL,
                    Severity.CRITICAL if condition['severity'] == 'critical' else Severity.WARNING,
                    condition['message'],
                    condition,
                    auto_fixable=False
                ))
        else:
            results.append(self._create_result(
                "invalid_state_conditions",
                ValidationStatus.PASS,
                Severity.INFO,
                "No invalid state conditions",
                {}
            ))
        
        return results
    
    def _parse_current_state(self) -> Optional[Dict]:
        """Parse current state từ STATE.md"""
        if not self.state_file.exists():
            return None
        
        state = {}
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract phase
                phase_match = re.search(r'phase:\s*(\w+)', content, re.IGNORECASE)
                if phase_match:
                    state['phase'] = phase_match.group(1)
                
                # Extract status
                status_match = re.search(r'status:\s*(\w+)', content, re.IGNORECASE)
                if status_match:
                    state['status'] = status_match.group(1)
                
                # Extract last_updated
                updated_match = re.search(r'last_updated:\s*(.+)', content, re.IGNORECASE)
                if updated_match:
                    state['last_updated'] = updated_match.group(1).strip()
                
                return state
        except:
            return None
    
    def _validate_against_state_machine(self, current_state: Dict) -> List[ValidationResult]:
        """Validate state against STATE_MACHINE.yaml"""
        results = []
        
        try:
            with open(self.state_machine_file, 'r', encoding='utf-8') as f:
                state_machine = yaml.safe_load(f)
            
            states = state_machine.get('states', [])
            state_names = [s['name'] for s in states]
            
            current_phase = current_state.get('phase', '').upper()
            
            # Check if current phase is valid
            if current_phase not in state_names:
                results.append(self._create_result(
                    "state_machine_valid_state",
                    ValidationStatus.FAIL,
                    Severity.CRITICAL,
                    f"Current phase '{current_phase}' not defined in state machine",
                    {"valid_states": state_names}
                ))
            else:
                results.append(self._create_result(
                    "state_machine_valid_state",
                    ValidationStatus.PASS,
                    Severity.INFO,
                    f"Current phase '{current_phase}' is valid",
                    {}
                ))
            
            # Check allowed transitions
            transitions = state_machine.get('transitions', [])
            allowed_from_current = [
                t for t in transitions 
                if t.get('from', '').upper() == current_phase
            ]
            
            if allowed_from_current:
                to_states = [t.get('to') for t in allowed_from_current]
                results.append(self._create_result(
                    "state_machine_transitions",
                    ValidationStatus.PASS,
                    Severity.INFO,
                    f"Valid transitions from {current_phase}: {to_states}",
                    {"allowed_transitions": to_states}
                ))
            
        except Exception as e:
            results.append(self._create_result(
                "state_machine_parse",
                ValidationStatus.FAIL,
                Severity.ERROR,
                f"Cannot parse STATE_MACHINE.yaml: {e}",
                {}
            ))
        
        return results
    
    def _check_invalid_state_conditions(self, current_state: Dict) -> List[Dict]:
        """Check các điều kiện invalid state"""
        invalid = []
        
        phase = current_state.get('phase', '').lower()
        
        # Load state machine invalid conditions if available
        if self.state_machine_file.exists():
            try:
                with open(self.state_machine_file, 'r', encoding='utf-8') as f:
                    state_machine = yaml.safe_load(f)
                
                invalid_conditions = state_machine.get('invalid_state_conditions', [])
                
                for condition in invalid_conditions:
                    cond_str = condition.get('condition', '')
                    # Simple condition evaluation
                    if self._evaluate_condition(cond_str, current_state):
                        invalid.append({
                            'type': 'state_machine_rule',
                            'message': f"Invalid state condition: {cond_str}",
                            'severity': condition.get('severity', 'warning'),
                            'action': condition.get('action', 'notify'),
                            'condition': cond_str
                        })
            except:
                pass
        
        # Built-in checks
        if phase == 'coding':
            if not Path('.agent/02_TASK_LIST.md').exists():
                invalid.append({
                    'type': 'missing_task_list',
                    'message': "CODING phase without TASK_LIST.md",
                    'severity': 'critical',
                    'action': 'halt_and_notify'
                })
        
        if phase == 'testing':
            if not Path('.test').exists():
                invalid.append({
                    'type': 'missing_test_dir',
                    'message': "TESTING phase without .test directory",
                    'severity': 'critical',
                    'action': 'halt_and_notify'
                })
        
        # Check lock expiration
        lock_file = Path('.state/lock.json')
        if lock_file.exists() and phase in ['coding', 'testing']:
            import json
            from datetime import datetime
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                expires_at = lock_data.get('expires_at', '')
                if expires_at:
                    expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if datetime.utcnow() > expires:
                        invalid.append({
                            'type': 'expired_lock',
                            'message': f"Lock expired in {phase} phase",
                            'severity': 'warning',
                            'action': 'auto_release_lock'
                        })
            except:
                pass
        
        return invalid
    
    def _evaluate_condition(self, condition: str, state: Dict) -> bool:
        """Đơn giản hóa - chỉ hỗ trợ một số condition patterns cơ bản"""
        # This is a simplified evaluator
        # In production, consider using a proper expression evaluator
        phase = state.get('phase', '').lower()
        
        if "phase == 'coding'" in condition and "not exists" in condition:
            if phase == 'coding' and 'task_list' in condition.lower():
                return not Path('.agent/02_TASK_LIST.md').exists()
        
        return False
