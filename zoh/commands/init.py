"""
ZOH Initialization Command Manager
Includes logic for strict project size detection and CLI recommendations
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class InitManager:
    """Manages project initialization and environment setup"""
    
    def __init__(self, target_path: Path):
        self.target_path = target_path

    def analyze_project_size(self) -> Dict[str, Any]:
        """
        Analyze current project to recommend a ZOH mode
        Metrics: LOC (Lines of Code), Contributors
        """
        loc = self._count_loc()
        contributors = self._count_contributors()
        
        # Recommendation Logic (Decision Matrix v2.0)
        if loc < 500 and contributors <= 1:
            recommended_mode = "light"
            explanation = "Minimalist project detected (Solo, < 500 LOC). Light mode recommended."
        elif loc < 10000:
            recommended_mode = "standard"
            explanation = "Standard project detected. Full core governance recommended."
        else:
            recommended_mode = "strict"
            explanation = "Complex or Collaborative project detected (>10k LOC or 3+ Devs). Strict mode recommended."
            
        return {
            "loc": loc,
            "contributors": contributors,
            "recommended_mode": recommended_mode,
            "explanation": explanation
        }

    def _count_loc(self) -> int:
        """
        Count lines of code (py, js, ts) with STRICT exclusion list.
        Excludes: node_modules, .venv, venv, env, .git, dist, build, __pycache__, .next, .zoh
        """
        total_loc = 0
        extensions = {'.py', '.js', '.ts', '.tsx', '.cs', '.cpp', '.h'}
        
        # --- PHASE 3: STRICT EXCLUSION LIST ---
        exclude_dirs = {
            'node_modules', '.venv', 'venv', 'env', '.git', 
            'dist', 'build', '__pycache__', '.next', '.zoh'
        }
        
        for root, dirs, files in os.walk(self.target_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            total_loc += sum(1 for line in f if line.strip())
                    except:
                        continue
        return total_loc

    def _count_contributors(self) -> int:
        """Get number of unique git contributors via shortlog"""
        try:
            output = subprocess.check_output(
                ["git", "shortlog", "-sn"],
                cwd=self.target_path,
                stderr=subprocess.STDOUT,
                encoding="utf-8"
            )
            # Count lines in output
            lines = output.strip().splitlines()
            return len(lines)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return 1 # Fallback to solo if no git repo

    def setup_git_safety(self):
        """Append ZOH pre-commit and setup .gitattributes"""
        git_dir = self.target_path / ".git"
        if not git_dir.exists():
            return
            
        # 1. Pre-commit Hook (Append mode)
        hook_file = git_dir / "hooks" / "pre-commit"
        zoh_hook = "\n# ZOH Consistency Check\nzoh validate --strict || exit 1\n"
        
        if hook_file.exists():
            existing = hook_file.read_text(encoding="utf-8")
            if "zoh validate" not in existing:
                with open(hook_file, "a", encoding="utf-8") as h:
                    h.write(zoh_hook)
        else:
            code = "#!/bin/bash\n" + zoh_hook
            hook_file.write_text(code, encoding="utf-8")
            
        # Set executable permissions
        try:
            mode = os.stat(hook_file).st_mode
            os.chmod(hook_file, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except:
            pass

        # 2. .gitattributes (Merge strategy)
        attr_file = self.target_path / ".gitattributes"
        attr_content = "\n# ZOH State Management\n*.md merge=ours linguist-generated\n.state/* merge=ours\n"
        
        if attr_file.exists():
            existing = attr_file.read_text(encoding="utf-8")
            if "merge=ours" not in existing:
                with open(attr_file, "a", encoding="utf-8") as f:
                    f.write(attr_content)
        else:
            attr_file.write_text(attr_content, encoding="utf-8")

def show_recommendation_table(stats: Dict[str, Any]):
    """Show rich table with LOC/Contributor stats and recommended mode"""
    table = Table(title="🔍 ZOH Project Sizing Analysis")
    table.add_column("Project Metric", style="cyan", no_wrap=True)
    table.add_row("Detected Source LOC", f"{stats['loc']:,}")
    table.add_row("Unique Contributors", str(stats['contributors']))
    
    # Mode Color logic
    mode = stats['recommended_mode'].upper()
    color = "green" if mode == "LIGHT" else "yellow" if mode == "STANDARD" else "bold red"
    
    table.add_row("Recommended Mode", f"[{color}]{mode}[/{color}]")
    
    console.print(table)
    console.print(Panel(f"[bold]Reasoning:[/bold] {stats['explanation']}", subtitle="Decision Matrix v2.0", border_style="blue"))
