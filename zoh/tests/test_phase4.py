"""
Final Verification Tests for Phase 4
Tests MCP Server tools and Dashboard API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from pathlib import Path

from zoh.dashboard.app import app
from zoh.mcp_server import handle_call_tool

client = TestClient(app)

# --- Dashboard API Tests ---

def test_dashboard_api_metrics():
    """Verify that the dashboard API returns the standard metrics structure"""
    with patch("zoh.commands.metrics.MetricsAggregator.aggregate") as mock_agg:
        mock_agg.return_value = {
            "token_stats": {"total_consumed": 5000},
            "validation_stats": {"success": 10, "fail": 2},
            "bug_stats": {"open": 1, "fixed": 5}
        }
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["token_stats"]["total_consumed"] == 5000
        assert data["bug_stats"]["fixed"] == 5

def test_dashboard_html_rendering():
    """Verify the HTML dashboard contains Plotly.js"""
    response = client.get("/")
    assert response.status_code == 200
    assert "plotly-2.24.1.min.js" in response.text
    assert "ZOH Project Governance Dashboard" in response.text

# --- MCP Tool Tests ---

@pytest.mark.asyncio
async def test_mcp_read_project_map_error(tmp_path, monkeypatch):
    """Verify MCP error handling when .map is missing"""
    monkeypatch.chdir(tmp_path)
    result = await handle_call_tool("read_project_map", {})
    assert "Error: .map/ directory not found" in result[0].text

@pytest.mark.asyncio
async def test_mcp_validate_state_success():
    """Verify MCP validation tool calling"""
    with patch("zoh.mcp_server.run_validation") as mock_val:
        mock_report = MagicMock()
        mock_report.overall_status.value = "pass"
        mock_report.overall_score = 95
        mock_report.to_dict.return_value = {"score": 95}
        mock_val.return_value = mock_report
        
        result = await handle_call_tool("validate_state", {})
        assert "Validation Status: PASSED" in result[0].text
        assert "Score: 95/100" in result[0].text
