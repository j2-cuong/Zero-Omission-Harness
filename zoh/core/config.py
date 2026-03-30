"""
ZOH Core Configuration
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Tải cấu hình từ CONFIG.yaml"""
    
    DEFAULT_CONFIG = {
        'mode': 'light',
        'thresholds': {
            'contract_code_match': 100,
            'map_file_sync': 90,
            'doc_accuracy': 80,
            'state_consistency': 100
        },
        'auto_fix': {
            'enabled': True,
            'safe_fixes_only': True,
            'require_approval': True,
            'dry_run_first': True,
            'allowed_fixes': ['map_file_sync', 'doc_timestamp_update', 'hash_cache_refresh'],
            'light_mode_auto_fix': ['hash_cache_refresh', 'timestamp'],
        },
        'blocking': {
            'on_critical': True,
            'on_error': True,
            'on_warning': False,
            'use_score_as_gate': False
        },
        'scoring': {
            'enabled': True,
            'weights': {
                'code_contract': 40,
                'state_transition': 30,
                'map_code': 15,
                'doc_reality': 15
            },
            'threshold_warning': 70,
            'threshold_block': 50
        },
        'lock': {
            'enabled': True,
            'mode': 'local',
            'heartbeat_interval': 300,
            'timeout_hours': 2,
            'auto_release_on_exit': True,
            'require_lock_for_validation': False,
            'auto_release_after_validation': True
        },
        'token': {
            'management': 'manual',
            'alert_at': 80,
            'budget_file': '.token/budget.yaml',
            'log_dir': '.token/logs'
        },
        'state': {
            'transition_cli_only': True,
            'state_file': '.state/STATE.md',
            'state_machine': '.state/STATE_MACHINE.yaml',
            'history_dir': '.state/history',
            'auto_checkpoint': True,
            'guards': {
                'file_exists': True,
                'task_list_complete': True,
                'validation_gate_passed': True,
                'no_active_lock': True
            }
        },
        'checkpoint': {
            'enabled': True,
            'dir': '.state/checkpoints',
            'auto_create_before_validation': True,
            'auto_rollback_on_critical_fail': True
        },
        'paths': {
            'code': ['.py', '.js', '.ts', '.go', '.java', '.rs', '.cpp', '.hpp', '.cs'],
            'map': ['.map/', 'ARCHITECTURE.md'],
            'doc': ['.doc/', 'README.md', 'docs/'],
            'contract': ['.agent/contracts/'],
            'state': ['.state/STATE.md', '.state/STATE_MACHINE.yaml']
        },
        'cli': {
            'name': 'zoh',
            'version': '1.0.0',
            'output': {
                'format': 'rich',
                'color': True,
                'verbose': False
            },
            'log_level': 'INFO',
            'log_file': '.agent/consistency/cli.log'
        }
    }
    
    def __init__(self, config_path: str = "CONFIG.yaml"):
        self.config_path = Path(config_path)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Load config từ file nếu tồn tại"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge_config(user_config)
            except Exception as e:
                print(f"⚠️  Warning: Cannot load config file: {e}")
                print("   Using default configuration")
    
    def _merge_config(self, user_config: Dict):
        """Deep merge user config với default"""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict) and isinstance(self.config[key], dict):
                self._deep_update(self.config[key], value)
            else:
                self.config[key] = value
    
    def _deep_update(self, original: Dict, update: Dict):
        """Recursive dict update"""
        for key, value in update.items():
            if key in original and isinstance(value, dict) and isinstance(original[key], dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value
    
    def get(self, key: str, default=None):
        """Get config value với dot notation"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire config dict"""
        return self.config.copy()
