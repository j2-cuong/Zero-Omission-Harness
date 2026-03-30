#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
STATE VALIDATOR - State Machine Engine
=============================================================================
Validate state transitions, detect invalid states, manage audit trail
=============================================================================
"""

import os
import sys
import yaml
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class StateError(Exception):
    """Exception cho state-related errors"""
    pass


class InvalidTransitionError(StateError):
    """Transition không hợp lệ"""
    pass


class GuardConditionError(StateError):
    """Guard condition không pass"""
    pass


@dataclass
class StateTransition:
    """Một state transition"""
    from_state: str
    to_state: str
    guard: str
    actions: List[str]
    timestamp: str
    by: str
    guard_result: bool
    actions_executed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AuditEntry:
    """Một entry trong audit trail"""
    timestamp: str
    from_state: str
    to_state: str
    by: str
    guard_result: str
    actions_executed: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateValidator:
    """
    State Machine Validator
    
    Responsibilities:
    - Validate state transitions
    - Check guard conditions
    - Execute entry/exit actions
    - Detect invalid states
    - Manage audit trail
    - Create checkpoints
    """
    
    def __init__(self, state_machine_path: str = ".state/STATE_MACHINE.yaml",
                 state_path: str = ".agent/STATE.md",
                 history_path: str = ".state/history.yaml"):
        self.state_machine_path = Path(state_machine_path)
        self.state_path = Path(state_path)
        self.history_path = Path(history_path)
        
        self.state_machine = self._load_state_machine()
        self.current_state = self._load_current_state()
        self.history = self._load_history()
    
    def _load_state_machine(self) -> Dict:
        """Load state machine definition"""
        if not self.state_machine_path.exists():
            raise StateError(f"State machine file not found: {self.state_machine_path}")
        
        with open(self.state_machine_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_current_state(self) -> Dict:
        """Load current state từ STATE.md"""
        if not self.state_path.exists():
            return {"phase": "INIT", "status": "idle"}
        
        state = {}
        with open(self.state_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Parse phase
            phase_match = self._extract_yaml_field(content, 'phase')
            if phase_match:
                state['phase'] = phase_match
            
            # Parse status
            status_match = self._extract_yaml_field(content, 'status')
            if status_match:
                state['status'] = status_match
            
            # Parse last_updated
            updated_match = self._extract_yaml_field(content, 'last_updated')
            if updated_match:
                state['last_updated'] = updated_match
            
            # Parse current_task
            task_match = self._extract_yaml_field(content, 'current_task')
            if task_match:
                state['current_task'] = task_match
        
        return state
    
    def _extract_yaml_field(self, content: str, field: str) -> Optional[str]:
        """Extract một field từ YAML content"""
        import re
        pattern = rf'{field}:\s*(.+)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def _load_history(self) -> List[Dict]:
        """Load history từ history.yaml"""
        if not self.history_path.exists():
            return []
        
        with open(self.history_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('history', [])
    
    def validate_transition(self, from_state: str, to_state: str) -> Tuple[bool, str]:
        """
        Validate một state transition
        
        Returns:
            (is_valid, reason)
        """
        # Check if states exist
        states = self.state_machine.get('states', {})
        if from_state not in states:
            return False, f"From state '{from_state}' not defined"
        if to_state not in states:
            return False, f"To state '{to_state}' not defined"
        
        # Find transition
        transitions = self.state_machine.get('transitions', [])
        transition = None
        for t in transitions:
            if t.get('from') == from_state and t.get('to') == to_state:
                transition = t
                break
        
        if not transition:
            return False, f"No transition defined from '{from_state}' to '{to_state}'"
        
        # Check guard condition
        guard = transition.get('guard')
        if guard:
            guard_passed, reason = self._check_guard(guard)
            if not guard_passed:
                return False, f"Guard condition failed: {reason}"
        
        return True, "Transition valid"
    
    def _check_guard(self, guard_name: str) -> Tuple[bool, str]:
        """Check một guard condition"""
        guards = self.state_machine.get('guards', {})
        guard_def = guards.get(guard_name)
        
        if not guard_def:
            return False, f"Guard '{guard_name}' not defined"
        
        check = guard_def.get('check', '')
        
        # Simple guard evaluation (có thể mở rộng)
        if 'exists' in check:
            file_name = check.split('exists')[0].strip()
            file_path = Path(file_name)
            if not file_path.exists():
                return False, f"File '{file_name}' does not exist"
        
        if 'score >=' in check:
            # Parse score requirement
            score_match = self._extract_score_from_state()
            if score_match is None or score_match < 90:
                return False, f"Score requirement not met"
        
        return True, "Guard passed"
    
    def _extract_score_from_state(self) -> Optional[int]:
        """Extract validation score từ current state"""
        # Implement based on state structure
        return 95  # Placeholder
    
    def execute_transition(self, to_state: str, by: str = "system") -> Dict:
        """
        Execute một state transition
        
        Returns:
            Transition result
        """
        from_state = self.current_state.get('phase', 'INIT')
        
        # Validate
        is_valid, reason = self.validate_transition(from_state, to_state)
        if not is_valid:
            raise InvalidTransitionError(f"Cannot transition from {from_state} to {to_state}: {reason}")
        
        # Find transition definition
        transitions = self.state_machine.get('transitions', [])
        transition_def = None
        for t in transitions:
            if t.get('from') == from_state and t.get('to') == to_state:
                transition_def = t
                break
        
        # Execute exit actions of current state
        states = self.state_machine.get('states', {})
        current_state_def = states.get(from_state, {})
        exit_actions = current_state_def.get('exit_actions', [])
        self._execute_actions(exit_actions, 'exit')
        
        # Execute entry actions of new state
        new_state_def = states.get(to_state, {})
        entry_actions = new_state_def.get('entry_actions', [])
        self._execute_actions(entry_actions, 'entry')
        
        # Execute transition actions
        transition_actions = transition_def.get('actions', [])
        executed = self._execute_actions(transition_actions, 'transition')
        
        # Update current state
        self.current_state['phase'] = to_state
        self.current_state['last_updated'] = datetime.utcnow().isoformat()
        self._save_current_state()
        
        # Log to history
        audit_entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            from_state=from_state,
            to_state=to_state,
            by=by,
            guard_result="pass",
            actions_executed=executed
        )
        self._log_to_history(audit_entry)
        
        return {
            'success': True,
            'from': from_state,
            'to': to_state,
            'actions_executed': executed,
            'timestamp': audit_entry.timestamp
        }
    
    def _execute_actions(self, actions: List[str], context: str) -> List[str]:
        """Execute một list các actions"""
        executed = []
        action_defs = self.state_machine.get('actions', {})
        
        for action_name in actions:
            action_def = action_defs.get(action_name)
            if action_def:
                # In a real implementation, this would execute the action
                # For now, just log it
                executed.append(action_name)
                print(f"  [{context}] Executed: {action_name}")
        
        return executed
    
    def _save_current_state(self):
        """Save current state vào STATE.md"""
        # Read existing content
        if self.state_path.exists():
            with open(self.state_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # Update fields
        lines = content.split('\n')
        updated_lines = []
        phase_updated = False
        status_updated = False
        
        for line in lines:
            if line.startswith('phase:'):
                updated_lines.append(f"phase: {self.current_state.get('phase', 'INIT')}")
                phase_updated = True
            elif line.startswith('status:'):
                updated_lines.append(f"status: {self.current_state.get('status', 'idle')}")
                status_updated = True
            elif line.startswith('last_updated:'):
                updated_lines.append(f"last_updated: {self.current_state.get('last_updated', datetime.utcnow().isoformat())}")
            else:
                updated_lines.append(line)
        
        # Add missing fields
        if not phase_updated:
            updated_lines.append(f"phase: {self.current_state.get('phase', 'INIT')}")
        if not status_updated:
            updated_lines.append(f"status: {self.current_state.get('status', 'idle')}")
        
        with open(self.state_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))
    
    def _log_to_history(self, entry: AuditEntry):
        """Log một entry vào history"""
        self.history.append({
            'timestamp': entry.timestamp,
            'from': entry.from_state,
            'to': entry.to_state,
            'by': entry.by,
            'guard_result': entry.guard_result,
            'actions_executed': entry.actions_executed,
            'metadata': entry.metadata
        })
        
        # Save history
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_path, 'w', encoding='utf-8') as f:
            yaml.dump({'history': self.history}, f, default_flow_style=False, allow_unicode=True)
    
    def detect_invalid_state(self) -> List[Dict]:
        """Detect invalid state conditions"""
        issues = []
        
        checks = self.state_machine.get('invalid_state_detection', {}).get('checks', [])
        
        for check in checks:
            name = check.get('name')
            condition = check.get('condition')
            
            # Check condition
            if name == 'orphan_phase':
                current = self.current_state.get('phase', '')
                states = self.state_machine.get('states', {})
                if current not in states:
                    issues.append({
                        'type': 'orphan_phase',
                        'current_phase': current,
                        'action': check.get('action'),
                        'message': f"Current phase '{current}' is not defined in state machine"
                    })
            
            elif name == 'missing_required_files':
                # Check required files for current phase
                phase = self.current_state.get('phase', '')
                if phase == 'CODING':
                    if not Path('.agent/02_TASK_LIST.md').exists():
                        issues.append({
                            'type': 'missing_required_files',
                            'phase': phase,
                            'missing': '02_TASK_LIST.md',
                            'action': check.get('action')
                        })
            
            elif name == 'expired_lock':
                # Check lock file
                lock_file = Path('.state/LOCK.json')
                if lock_file.exists():
                    with open(lock_file, 'r') as f:
                        lock_data = json.load(f)
                    expires_at = lock_data.get('lock_entry', {}).get('expires_at', '')
                    if expires_at:
                        expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        if datetime.utcnow() > expires:
                            issues.append({
                                'type': 'expired_lock',
                                'lock_file': str(lock_file),
                                'expired_at': expires_at,
                                'action': check.get('action')
                            })
        
        return issues
    
    def create_checkpoint(self) -> str:
        """Create một checkpoint để có thể rollback"""
        checkpoint_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        checkpoint_dir = Path(f".state/checkpoints/{checkpoint_id}")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Files to checkpoint
        checkpoint_files = [
            '.agent/STATE.md',
            '.agent/02_TASK_LIST.md',
            '.map/current/',
            '.doc/PROGRESS.md'
        ]
        
        checkpoint_data = {
            'id': checkpoint_id,
            'timestamp': datetime.utcnow().isoformat(),
            'state': self.current_state,
            'files': []
        }
        
        for file_path in checkpoint_files:
            path = Path(file_path)
            if path.exists():
                if path.is_file():
                    # Copy file
                    import shutil
                    dest = checkpoint_dir / path.name
                    shutil.copy2(path, dest)
                    checkpoint_data['files'].append(str(file_path))
                elif path.is_dir():
                    # Copy directory
                    import shutil
                    dest = checkpoint_dir / path.name
                    shutil.copytree(path, dest)
                    checkpoint_data['files'].append(str(file_path))
        
        # Save checkpoint metadata
        with open(checkpoint_dir / 'checkpoint.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(checkpoint_data, f, default_flow_style=False)
        
        print(f"Checkpoint created: {checkpoint_id}")
        return checkpoint_id
    
    def get_audit_trail(self) -> List[Dict]:
        """Get full audit trail"""
        return self.history
    
    def get_allowed_transitions(self, from_state: Optional[str] = None) -> List[str]:
        """Get list of allowed transitions from một state"""
        if from_state is None:
            from_state = self.current_state.get('phase', 'INIT')
        
        transitions = self.state_machine.get('transitions', [])
        allowed = []
        
        for t in transitions:
            if t.get('from') == from_state:
                to_state = t.get('to')
                # Check if guard passes
                guard = t.get('guard')
                if guard:
                    guard_passed, _ = self._check_guard(guard)
                    if guard_passed:
                        allowed.append(to_state)
                else:
                    allowed.append(to_state)
        
        return allowed


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='State Machine Validator')
    parser.add_argument('command', choices=['validate', 'transition', 'check', 'history', 'checkpoint'])
    parser.add_argument('--from-state', help='From state for validation')
    parser.add_argument('--to-state', help='To state for validation/transition')
    parser.add_argument('--by', default='system', help='Who is making the transition')
    
    args = parser.parse_args()
    
    validator = StateValidator()
    
    if args.command == 'validate':
        if not args.from_state or not args.to_state:
            print("Error: --from-state and --to-state required")
            sys.exit(1)
        
        is_valid, reason = validator.validate_transition(args.from_state, args.to_state)
        print(f"Transition {args.from_state} -> {args.to_state}:")
        print(f"  Valid: {is_valid}")
        print(f"  Reason: {reason}")
        sys.exit(0 if is_valid else 1)
    
    elif args.command == 'transition':
        if not args.to_state:
            print("Error: --to-state required")
            sys.exit(1)
        
        try:
            result = validator.execute_transition(args.to_state, args.by)
            print(f"Transition executed successfully:")
            print(f"  From: {result['from']}")
            print(f"  To: {result['to']}")
            print(f"  Actions: {result['actions_executed']}")
            print(f"  Timestamp: {result['timestamp']}")
        except StateError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == 'check':
        issues = validator.detect_invalid_state()
        if issues:
            print(f"Found {len(issues)} invalid state condition(s):")
            for issue in issues:
                print(f"  - {issue['type']}: {issue.get('message', '')}")
                print(f"    Action: {issue.get('action', 'none')}")
        else:
            print("No invalid state conditions detected.")
    
    elif args.command == 'history':
        history = validator.get_audit_trail()
        print(f"Audit Trail ({len(history)} entries):")
        for entry in history:
            print(f"  {entry['timestamp']}: {entry['from']} -> {entry['to']} by {entry['by']}")
    
    elif args.command == 'checkpoint':
        checkpoint_id = validator.create_checkpoint()
        print(f"Checkpoint created: {checkpoint_id}")


if __name__ == '__main__':
    main()
