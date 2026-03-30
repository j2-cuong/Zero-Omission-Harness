"""
ZOH State Validator
"""

import os
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .config import ConfigLoader


class StateValidator:
    """Validate state transitions theo STATE_MACHINE.yaml"""
    
    def __init__(
        self,
        config: ConfigLoader = None,
        state_file: str = None,
        state_machine_file: str = None
    ):
        self.config = config or ConfigLoader()
        self.state_file = Path(state_file or self.config.get('state.state_file', '.state/STATE.md'))
        self.state_machine_file = Path(state_machine_file or self.config.get('state.state_machine', '.state/STATE_MACHINE.yaml'))
        self.history_dir = Path(self.config.get('state.history_dir', '.state/history'))
        
        self.state_machine = self._load_state_machine()
        self.cli_only = self.config.get('state.transition_cli_only', True)
    
    def _load_state_machine(self) -> Dict:
        """Load STATE_MACHINE.yaml"""
        if not self.state_machine_file.exists():
            return self._default_state_machine()
        
        try:
            with open(self.state_machine_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Error loading state machine: {e}")
            return self._default_state_machine()
    
    def _default_state_machine(self) -> Dict:
        """Default state machine nếu file không tồn tại"""
        return {
            'states': ['interview', 'planning', 'coding', 'scan', 'fix', 'testing', 'release'],
            'allowed_transitions': {
                'interview': ['planning'],
                'planning': ['coding'],
                'coding': ['scan', 'testing'],
                'scan': ['fix'],
                'fix': ['testing', 'scan'],
                'testing': ['release', 'coding'],
                'release': ['interview']
            },
            'guards': {
                'coding': ['file_exists:.agent/02_TASK_LIST.md'],
                'testing': ['validation_gate_passed:GATE-1', 'validation_gate_passed:GATE-2'],
                'release': ['task_list_complete:.agent/02_TASK_LIST.md,90']
            }
        }
    
    def _load_current_state(self) -> Dict[str, str]:
        """Parse STATE.md để lấy current state"""
        if not self.state_file.exists():
            return {'phase': 'unknown', 'status': 'unknown', 'version': ''}
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            state = {}
            
            phase_match = re.search(r'phase:\s*(\w+)', content, re.IGNORECASE)
            state['phase'] = phase_match.group(1) if phase_match else 'unknown'
            
            status_match = re.search(r'status:\s*(\w+)', content, re.IGNORECASE)
            state['status'] = status_match.group(1) if status_match else 'unknown'
            
            version_match = re.search(r'version:\s*([\w.]+)', content, re.IGNORECASE)
            state['version'] = version_match.group(1) if version_match else ''
            
            updated_match = re.search(r'last_updated:\s*([^\n]+)', content, re.IGNORECASE)
            state['last_updated'] = updated_match.group(1).strip() if updated_match else ''
            
            return state
        except Exception as e:
            print(f"⚠️  Error parsing state: {e}")
            return {'phase': 'unknown', 'status': 'unknown'}
    
    def evaluate_guard(self, guard: str) -> Tuple[bool, str]:
        """
        Evaluate guard condition
        
        Guards supported:
        - file_exists:path
        - task_list_complete:file,threshold
        - validation_gate_passed:gate_name
        - no_active_lock
        - true
        """
        if not guard or guard == 'true':
            return True, "Always true"
        
        if ':' in guard:
            guard_type, params = guard.split(':', 1)
        else:
            guard_type = guard
            params = ''
        
        guard_type = guard_type.strip()
        params = params.strip()
        
        if guard_type == 'file_exists':
            exists = Path(params).exists()
            return exists, f"File exists: {params}" if exists else f"File missing: {params}"
        
        elif guard_type == 'task_list_complete':
            if ',' in params:
                file_path, threshold_str = params.split(',', 1)
                threshold = float(threshold_str.strip())
            else:
                file_path = params
                threshold = 80.0
            
            complete, actual = self._check_task_list_complete(file_path.strip(), threshold)
            return complete, f"Task list {actual:.1f}% complete (threshold: {threshold}%)"
        
        elif guard_type == 'validation_gate_passed':
            gate_file = Path(f".gates/{params}_PASSED")
            passed = gate_file.exists()
            return passed, f"Gate {params} passed" if passed else f"Gate {params} not passed"
        
        elif guard_type == 'no_active_lock':
            lock_file = Path('.state/lock.json')
            if not lock_file.exists():
                return True, "No active lock"
            
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                expires = datetime.fromisoformat(lock_data.get('expires_at', '2000-01-01'))
                if datetime.utcnow() > expires:
                    return True, "Lock expired"
                return False, f"Lock held by {lock_data.get('owner', 'unknown')}"
            except:
                return True, "Lock file corrupted"
        
        elif guard_type == 'config_mode_is':
            current_mode = self.config.get('mode', 'light')
            matches = current_mode == params
            return matches, f"Config mode is {current_mode}"
        
        elif guard_type == 'all_validators_passed':
            report_file = self._get_latest_validation_report()
            if not report_file:
                return False, "No validation report found"
            
            try:
                with open(report_file, 'r') as f:
                    report = json.load(f)
                passed = report.get('overall_status') == 'pass'
                return passed, "All validators passed" if passed else "Some validators failed"
            except:
                return False, "Cannot read validation report"
        
        else:
            return False, f"Unknown guard type: {guard_type}"
    
    def _check_task_list_complete(self, file_path: str, threshold: float) -> Tuple[bool, float]:
        """Check if task list is complete above threshold"""
        path = Path(file_path)
        if not path.exists():
            return False, 0.0
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            unchecked = content.count('[ ]')
            checked = content.count('[x]') + content.count('[X]')
            
            total = unchecked + checked
            if total == 0:
                return False, 0.0
            
            percentage = (checked / total) * 100
            return percentage >= threshold, percentage
        except Exception as e:
            print(f"⚠️  Error checking task list: {e}")
            return False, 0.0
    
    def _get_latest_validation_report(self) -> Optional[Path]:
        """Get path to latest validation report"""
        reports_dir = Path('.agent/consistency/reports')
        if not reports_dir.exists():
            return None
        
        reports = sorted(reports_dir.glob('consistency_*.md'), reverse=True)
        if reports:
            return reports[0]
        return None
    
    def validate_transition(self, to_phase: str) -> Dict[str, Any]:
        """Validate if transition to phase is allowed"""
        current_state = self._load_current_state()
        current_phase = current_state.get('phase', 'unknown')
        
        result = {
            'valid': False,
            'current_phase': current_phase,
            'allowed': False,
            'guards_passed': False,
            'failed_guards': [],
            'messages': []
        }
        
        allowed_transitions = self.state_machine.get('allowed_transitions', {})
        valid_next = allowed_transitions.get(current_phase, [])
        
        if to_phase not in valid_next:
            result['messages'].append(f"Transition from '{current_phase}' to '{to_phase}' not allowed")
            result['messages'].append(f"Allowed transitions: {valid_next}")
            return result
        
        result['allowed'] = True
        
        guards = self.state_machine.get('guards', {}).get(to_phase, [])
        failed_guards = []
        
        for guard in guards:
            passed, message = self.evaluate_guard(guard)
            if not passed:
                failed_guards.append(f"{guard}: {message}")
        
        result['failed_guards'] = failed_guards
        
        if failed_guards:
            result['messages'].append(f"Guards failed for transition to '{to_phase}':")
            for guard in failed_guards:
                result['messages'].append(f"  • {guard}")
            return result
        
        result['guards_passed'] = True
        result['valid'] = True
        result['messages'].append(f"Transition to '{to_phase}' is valid")
        
        return result
    
    def transition(self, to_phase: str, force: bool = False) -> Dict[str, Any]:
        """Perform state transition (returns result dict, doesn't execute)"""
        current_state = self._load_current_state()
        current_phase = current_state.get('phase', 'unknown')
        
        result = {
            'success': False,
            'message': '',
            'from_phase': current_phase,
            'to_phase': to_phase
        }
        
        if not force:
            validation = self.validate_transition(to_phase)
            if not validation['valid']:
                result['message'] = '\n'.join(validation['messages'])
                return result
        
        success = self._write_new_state(to_phase)
        
        if success:
            result['success'] = True
            result['message'] = f"Transitioned from '{current_phase}' to '{to_phase}'"
            self._create_audit_entry('transition_success', {
                'from_phase': current_phase,
                'to_phase': to_phase,
                'force': force
            })
        else:
            result['message'] = "Failed to write new state"
        
        return result
    
    def _write_new_state(self, new_phase: str) -> bool:
        """Write new state to STATE.md"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = re.sub(
                    r'^(phase:\s*)\w+$',
                    rf'\g<1>{new_phase}',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                
                content = re.sub(
                    r'^(last_updated:\s*)[^\n]*$',
                    rf'\g<1>{datetime.utcnow().isoformat()}',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                
                content = re.sub(
                    r'^(status:\s*)\w+$',
                    r'\g<1>active',
                    content,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                content = f"""# State

phase: {new_phase}
status: active
version: 1.0.0
last_updated: {datetime.utcnow().isoformat()}

## Consistency Flags

- code: synced
- map: synced
- doc: synced

## Blockers

None

## Notes

Auto-generated by state_validator
"""
                self.state_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return True
        except Exception as e:
            print(f"❌ Error writing state: {e}")
            return False
    
    def _create_audit_entry(self, event: str, data: dict):
        """Create audit trail entry"""
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        audit_file = self.history_dir / f"{timestamp}_{event}.json"
        
        audit_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
    
    def get_current_phase(self) -> str:
        """Get current phase"""
        state = self._load_current_state()
        return state.get('phase', 'unknown')
    
    def get_allowed_transitions(self) -> List[str]:
        """Get allowed transitions from current phase"""
        current_phase = self.get_current_phase()
        return self.state_machine.get('allowed_transitions', {}).get(current_phase, [])
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state"""
        current_state = self._load_current_state()
        current_phase = current_state.get('phase', 'unknown')
        
        return {
            'phase': current_phase,
            'status': current_state.get('status', 'unknown'),
            'version': current_state.get('version', ''),
            'last_updated': current_state.get('last_updated', ''),
            'allowed_transitions': self.get_allowed_transitions(),
            'cli_only': self.cli_only
        }
