"""
Tests for ZOH Initialization Decision Matrix (Phase 3 Refined)
"""

import pytest
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from zoh.commands.init import InitManager

def test_analyze_project_size_light(tmp_path):
    # Setup dummy project with small LOC and no git
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    
    with patch("subprocess.check_output") as mock_git:
        # Mock git failure (no git repo)
        mock_git.side_effect = FileNotFoundError()
        
        init_mgr = InitManager(tmp_path)
        stats = init_mgr.analyze_project_size()
        
        assert stats["recommended_mode"] == "light"
        assert stats["loc"] <= 20
        assert stats["contributors"] == 1

def test_analyze_project_size_strict(tmp_path):
    # Setup dummy project with large LOC and many contributors
    (tmp_path / "main.py").write_text("print('hello')\n" * 12000, encoding="utf-8")
    
    with patch("subprocess.check_output") as mock_git:
        # Mock git with 5 contributors
        mock_git.return_value = "5 cuong\n3 hung\n2 nam\n1 dat\n1 cuong2"
        
        init_mgr = InitManager(tmp_path)
        stats = init_mgr.analyze_project_size()
        
        assert stats["recommended_mode"] == "strict"
        assert stats["loc"] > 10000
        assert stats["contributors"] == 5

def test_analyze_project_size_standard(tmp_path):
    # Setup medium project
    (tmp_path / "main.py").write_text("print('hello')\n" * 1000, encoding="utf-8")
    
    with patch("subprocess.check_output") as mock_git:
        mock_git.return_value = "1 cuong"
        
        init_mgr = InitManager(tmp_path)
        stats = init_mgr.analyze_project_size()
        
        assert stats["recommended_mode"] == "standard"
        assert stats["loc"] > 500
        assert stats["contributors"] == 1

def test_loc_prefix_exclusion_strict(tmp_path):
    # Setup project with excluded directories
    # main project folder
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    
    # Excluded folders
    for d in ["node_modules", ".venv", "venv", "env", ".git", "dist", "build", "__pycache__", ".next", ".zoh"]:
        d_path = tmp_path / d
        d_path.mkdir(parents=True, exist_ok=True)
        (d_path / "index.js").write_text("console.log('hi');\n" * 1000, encoding="utf-8")
        
    init_mgr = InitManager(tmp_path)
    stats = init_mgr.analyze_project_size()
    
    # Should only count main.py (1 line), NOT the 10,000 lines in excluded folders
    assert stats["loc"] < 10
    assert stats["recommended_mode"] == "light"
