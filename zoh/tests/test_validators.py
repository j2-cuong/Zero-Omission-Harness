import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from zoh.validators.ast_parser import PythonASTParser, TSASTParser, UnifiedASTParser

# --- Fixtures for Python AST Content ---

FASTAPI_CODE = """
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@router.post("/users", status_code=201)
@router.post("/accounts")  # Stacked decorator
def create_user():
    return {"message": "User created"}

@app.route("/legacy", methods=["GET", "POST"])
def legacy_handler():
    return "OK"
"""

# --- Tests for PythonASTParser ---

def test_python_ast_extraction(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text(FASTAPI_CODE)
    
    parser = PythonASTParser()
    endpoints = parser.parse(py_file)
    
    # Expected: 4 logic entries (GET /items/{item_id}, POST /users, POST /accounts, GET /legacy, POST /legacy)
    # Note: our current simple extractor treats each decorator as an endpoint
    
    paths = [e["path"] for e in endpoints]
    methods = [e["method"] for e in endpoints]
    
    assert "/items/{item_id}" in paths
    assert "GET" in methods
    assert "/users" in paths
    assert "/accounts" in paths
    assert "POST" in methods
    assert "/legacy" in paths
    assert "GET" in methods or "POST" in methods

# --- Tests for TSASTParser ---

def test_ts_ast_extraction_mock(tmp_path, mocker):
    ts_file = tmp_path / "routes.ts"
    ts_file.write_text("// dummy ts code")
    
    # Mock subprocess.run to simulate Node.js output
    mock_output = [
        {"method": "GET", "path": "/api/v1/status", "handler": "getStatus"},
        {"method": "POST", "path": "/api/v1/login", "handler": "login"}
    ]
    
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps(mock_output),
        stderr=""
    )
    
    # Mock node check
    mocker.patch("zoh.validators.ast_parser.TSASTParser._check_node", return_value=True)
    
    parser = TSASTParser()
    endpoints = parser.parse(ts_file)
    
    assert len(endpoints) == 2
    assert endpoints[0]["method"] == "GET"
    assert endpoints[1]["path"] == "/api/v1/login"

# --- Tests for UnifiedASTParser ---

def test_unified_parser_dispatch(tmp_path, mocker):
    py_file = tmp_path / "test.py"
    py_file.write_text("@app.get('/')\ndef index(): pass")
    
    parser = UnifiedASTParser()
    
    # Test Python dispatch
    endpoints = parser.get_endpoints(py_file)
    assert len(endpoints) == 1
    assert endpoints[0]["path"] == "/"
    
    # Test unknown extension
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("nothing")
    assert parser.get_endpoints(txt_file) == []

# --- Edge Case: Stacked Decorators ---

def test_stacked_decorators_logic(tmp_path):
    code = """
@app.get("/alias1")
@app.get("/alias2")
def multi_route():
    pass
"""
    f = tmp_path / "stacked.py"
    f.write_text(code)
    
    parser = PythonASTParser()
    endpoints = parser.parse(f)
    
    paths = [e["path"] for e in endpoints]
    assert "/alias1" in paths
    assert "/alias2" in paths
    assert len(endpoints) == 2
