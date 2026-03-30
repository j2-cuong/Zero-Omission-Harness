"""
Tests for ZOH Static Analyzer (Phase 3 Refined)
"""

import pytest
import json
import shutil
from unittest.mock import MagicMock, patch
from pathlib import Path
from zoh.analyzers.static_analyzer import StaticAnalyzer

@pytest.fixture
def analyzer(tmp_path):
    return StaticAnalyzer(project_root=str(tmp_path))

def test_ruff_parsing_standard_json(analyzer):
    # Mock Ruff Output
    mock_ruff_json = json.dumps([
        {
            "filename": "test.py",
            "location": {"row": 1, "column": 5},
            "code": "F401",
            "message": "unused-import"
        }
    ])
    
    with patch("zoh.analyzers.static_analyzer.shutil.which", return_value="/usr/local/bin/ruff"), \
         patch("zoh.analyzers.static_analyzer.subprocess.check_output", return_value=mock_ruff_json):
        
        results = analyzer._run_ruff()
        
        assert len(results) == 1
        assert results[0]["tool"] == "ruff"
        assert results[0]["code"] == "F401"
        assert results[0]["message"] == "unused-import"

def test_mypy_parsing_text_interface(analyzer):
    # Mock Mypy Output (Text-based)
    mock_mypy_stdout = "main.py:10: 5: error: Incompatible types [type-arg]"
    
    with patch("zoh.analyzers.static_analyzer.shutil.which", return_value="/usr/local/bin/mypy"), \
         patch("zoh.analyzers.static_analyzer.subprocess.run") as mock_run:
        
        mock_run.return_value = MagicMock(stdout=mock_mypy_stdout, returncode=1)
        
        results = analyzer._run_mypy()
        
        assert len(results) == 1
        assert results[0]["tool"] == "mypy"
        assert "Incompatible types" in results[0]["message"]

def test_eslint_skip_without_config(analyzer, tmp_path):
    # Setup node project but NO config file
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    
    results = analyzer._run_eslint()
    assert results == [] # Should skip and return empty

def test_eslint_run_with_config(analyzer, tmp_path):
    # Setup node project WITH config file
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".eslintrc.json").write_text("{}", encoding="utf-8")
    
    mock_eslint_json = json.dumps([
        {
            "filePath": str(tmp_path / "index.js"),
            "messages": [
                {
                    "ruleId": "no-unused-vars",
                    "severity": 2,
                    "message": "unused variable",
                    "line": 5,
                    "column": 10
                }
            ]
        }
    ])
    
    with patch("zoh.analyzers.static_analyzer.shutil.which", return_value="/usr/bin/npx"), \
         patch("zoh.analyzers.static_analyzer.subprocess.check_output", return_value=mock_eslint_json):
        
        results = analyzer._run_eslint()
        
        assert len(results) == 1
        assert results[0]["tool"] == "eslint"
        assert results[0]["code"] == "no-unused-vars"

def test_tool_not_found_returns_empty(analyzer):
    with patch("zoh.analyzers.static_analyzer.shutil.which", return_value=None):
        assert analyzer._run_ruff() == []
        assert analyzer._run_mypy() == []
        assert analyzer._run_eslint() == []
