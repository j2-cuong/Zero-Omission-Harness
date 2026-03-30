"""
Tests for AI Compliance Validator
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from zoh.validators.ai_compliance import AIComplianceValidator
from zoh.core.config import ConfigLoader

@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigLoader)
    config.get.side_effect = lambda key, default=None: {
        "ai_provider": "openai",
        "mode": "strict"
    }.get(key, default)
    return config

def test_ai_compliance_success(mock_config, tmp_path, monkeypatch):
    # Setup mock rules files
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    master_file = agent_dir / "00_MASTER.md"
    master_file.write_text("Rule: Follow instructions", encoding="utf-8")
    
    monkeypatch.chdir(tmp_path)
    
    validator = AIComplianceValidator(mock_config)
    
    # Mock Provider
    mock_provider = MagicMock()
    mock_provider.verify_compliance.return_value = {"compliant": True, "reason": "OK"}
    validator.provider = mock_provider
    
    assert validator.validate_intent("Add a new feature") is True
    mock_provider.verify_compliance.assert_called_once()

def test_ai_compliance_failure_raises_exception(mock_config, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    validator = AIComplianceValidator(mock_config)
    
    # Mock Provider failing
    mock_provider = MagicMock()
    mock_provider.verify_compliance.return_value = {"compliant": False, "reason": "Violation of rule X"}
    validator.provider = mock_provider
    
    with pytest.raises(Exception) as excinfo:
        validator.validate_intent("Do something bad")
    
    assert "AI Compliance violation: Violation of rule X" in str(excinfo.value)

def test_dummy_provider_selection(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Mode: Light, No API Key -> Should use Dummy
    config = MagicMock(spec=ConfigLoader)
    config.get.side_effect = lambda key, default=None: {
        "ai_provider": "openai",
        "mode": "light"
    }.get(key, default)
    
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    validator = AIComplianceValidator(config)
    from zoh.core.ai_provider import DummyProvider
    assert isinstance(validator.provider, DummyProvider)

def test_strict_mode_requires_real_provider(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Mode: Strict, No API Key -> Should STILL try to use OpenAI (and fail later if used)
    config = MagicMock(spec=ConfigLoader)
    config.get.side_effect = lambda key, default=None: {
        "ai_provider": "openai",
        "mode": "strict"
    }.get(key, default)
    
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    validator = AIComplianceValidator(config)
    from zoh.core.ai_provider import OpenAIProvider
    assert isinstance(validator.provider, OpenAIProvider)
