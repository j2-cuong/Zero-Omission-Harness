"""
ZOH Static Analysis Integration
Orchestrates Mypy, Ruff, and ESLint via subprocess with structured parsing
"""

import subprocess
import json
import logging
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("zoh.static_analyzer")

class StaticAnalyzer:
    """Orchestrates static analysis tools and standardizes their output"""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
        
    def run_all(self) -> List[Dict[str, Any]]:
        """Run all detected static analysis tools"""
        results = []
        
        # 1. Python Analysis
        results.extend(self._run_ruff())
        results.extend(self._run_mypy())
        
        # 2. JS/TS Analysis
        results.extend(self._run_eslint())
        
        return results

    def _run_ruff(self) -> List[Dict[str, Any]]:
        """Run Ruff check with JSON output (Graceful fallback)"""
        tool = shutil.which("ruff")
        if not tool:
            logger.warning("Ruff linter not found. Skipping.")
            return []
            
        try:
            output = subprocess.check_output(
                [tool, "check", ".", "--format", "json"],
                cwd=self.root,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            
            errors = json.loads(output)
            return [
                {
                    "file": err.get("filename"),
                    "line": err.get("location", {}).get("row"),
                    "col": err.get("location", {}).get("column"),
                    "code": err.get("code"),
                    "message": err.get("message"),
                    "tool": "ruff",
                    "severity": "error"
                } for err in errors
            ]
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Ruff analysis encountered an error: {e}")
            return []

    def _run_mypy(self) -> List[Dict[str, Any]]:
        """Run Mypy check with structured output (Graceful fallback)"""
        tool = shutil.which("mypy")
        if not tool:
            logger.warning("Mypy type checker not found. Skipping.")
            return []
            
        try:
            # Mypy output format: file:line:col: severity: message [code]
            process = subprocess.run(
                [tool, ".", "--no-error-summary", "--hide-error-context"],
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            results = []
            for line in process.stdout.splitlines():
                if ":" in line:
                    parts = line.split(":", 3)
                    if len(parts) >= 3:
                        results.append({
                            "file": parts[0].strip(),
                            "line": parts[1].strip(),
                            "message": parts[-1].strip(),
                            "tool": "mypy",
                            "severity": "error" if "error" in line.lower() else "warning"
                        })
            return results
        except Exception as e:
            logger.warning(f"Mypy analysis encountered an error: {e}")
            return []

    def _run_eslint(self) -> List[Dict[str, Any]]:
        """
        Run ESLint with JSON output.
        STRICT: Only runs if an ESLint configuration file is detected.
        """
        config_files = [
            ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.mjs",
            ".eslintrc.json", ".eslintrc.yml", ".eslintrc.yaml",
            "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs"
        ]
        
        found_config = any((self.root / cfg).exists() for cfg in config_files)
        
        # Also check package.json for "eslintConfig" field
        if not found_config and (self.root / "package.json").exists():
            try:
                with open(self.root / "package.json", "r") as f:
                    pkg = json.load(f)
                    if "eslintConfig" in pkg:
                        found_config = True
            except:
                pass

        if not found_config:
            logger.warning("ESLint configuration not found. Skipping JS/TS analysis to respect project rules.")
            return []
            
        # Use npx to find local eslint
        tool = shutil.which("npx")
        if not tool:
            logger.warning("npx/npm not found. Cannot run ESLint.")
            return []
            
        try:
            output = subprocess.check_output(
                [tool, "eslint", ".", "--format", "json"],
                cwd=self.root,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            
            results = []
            data = json.loads(output)
            for file_entry in data:
                filename = file_entry.get("filePath")
                # Make relative to root
                rel_file = os.path.relpath(filename, self.root) if filename else "unknown"
                
                for msg in file_entry.get("messages", []):
                    results.append({
                        "file": rel_file,
                        "line": msg.get("line"),
                        "col": msg.get("column"),
                        "code": msg.get("ruleId"),
                        "message": msg.get("message"),
                        "tool": "eslint",
                        "severity": "error" if msg.get("severity") == 2 else "warning"
                    })
            return results
        except Exception as e:
            logger.warning(f"ESLint analysis encountered an error: {e}")
            return []
