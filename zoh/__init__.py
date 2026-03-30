"""
Zero-Omission-Harness (ZOH) - AI-driven software development framework

Package structure:
    zoh/
        __init__.py
        cli.py          - CLI entry point
        __main__.py     - For python -m zoh
        core/           - Core modules
            config.py   - Config loader
            state.py    - State validator
            checkpoint.py - Checkpoint manager
            lock.py     - Lock manager
        validators/     - Validation modules
            base.py     - Base classes
            code_contract.py
            map_code.py
            doc_reality.py
            state_transition.py
        validator.py    - Main validator orchestrator
"""

__version__ = "1.0.0"
__author__ = "ZOH Team"

from .core.config import ConfigLoader
from .core.state import StateValidator
from .core.checkpoint import CheckpointManager, create_checkpoint, rollback_to_checkpoint, list_checkpoints
from .core.lock import LockManager, acquire_lock, release_lock, check_lock_status

__all__ = [
    'ConfigLoader',
    'StateValidator',
    'CheckpointManager',
    'create_checkpoint',
    'rollback_to_checkpoint',
    'list_checkpoints',
    'LockManager',
    'acquire_lock',
    'release_lock',
    'check_lock_status',
]
