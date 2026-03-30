"""
ZOH Metrics Aggregator
Displays token usage, validation trends, and drift statistics via Rich Table
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class MetricsAggregator:
    """Aggregates project telemetry data from ZOH internal logs"""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
        self.token_dir = self.root / ".token"
        self.bug_dir = self.root / ".bug"
        self.history_dir = self.root / ".state/history"

    def aggregate(self) -> Dict[str, Any]:
        """Aggregate stats from all governance channels"""
        return {
            "token_stats": self._get_token_usage(),
            "validation_stats": self._get_validation_trends(),
            "bug_stats": self._get_bug_summary()
        }

    def _get_token_usage(self) -> Dict[str, Any]:
        """Parse .token/ usage logs for aggregate consumption"""
        total_tokens = 0
        if self.token_dir.exists():
            for log_file in self.token_dir.rglob("*.md"):
                try:
                    import re
                    content = log_file.read_text(encoding="utf-8")
                    # Match pattern "usage: 1234" (Case insensitive)
                    matches = re.findall(r'usage:\s*(\d+)', content, re.IGNORECASE)
                    total_tokens += sum(int(m) for m in matches)
                except:
                    continue
        return {"total_consumed": total_tokens}

    def _get_validation_trends(self) -> Dict[str, Any]:
        """Scan state history for transition success vs. failure ratio"""
        success = 0
        fail = 0
        
        if self.history_dir.exists():
            for audit_file in self.history_dir.glob("*.json"):
                try:
                    with open(audit_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("event") == "transition_success":
                            success += 1
                        elif data.get("event") == "transition_fail":
                            fail += 1
                except:
                    continue
        return {"success": success, "fail": fail}

    def _get_bug_summary(self) -> Dict[str, Any]:
        """Summary metrics from .bug/02_BUG_LIST.md (Open/Fixed)"""
        bug_list_file = self.bug_dir / "02_BUG_LIST.md"
        if not bug_list_file.exists():
            return {"open": 0, "fixed": 0}
            
        try:
            content = bug_list_file.read_text(encoding="utf-8")
            # Count standard markdown checkboxes
            open_count = content.count("[ ]")
            fixed_count = content.count("[x]")
            return {"open": open_count, "fixed": fixed_count}
        except:
            return {"open": 0, "fixed": 0}

def show_dashboard(stats: Dict[str, Any]):
    """Show rich dashboard with project telemetry summary"""
    console.print(Panel.fit("📊 ZOH PROJECT TELEMETRY DASHBOARD", style="bold blue", border_style="cyan"))
    
    # 1. Validation Table
    val_table = Table(title="🛡️ Validation Integrity", border_style="blue")
    val_table.add_column("Phase Transitions", style="cyan")
    val_table.add_column("Count", style="magenta", justify="right")
    
    val_table.add_row("Phase Success", str(stats['validation_stats']['success']))
    val_table.add_row("Enforcement Blocks", f"[bold red]{stats['validation_stats']['fail']}[/bold red]")
    
    # 2. Token Table
    token_table = Table(title="🪙 Token Governance", border_style="yellow")
    token_table.add_column("AI Resource", style="cyan")
    token_table.add_column("Consumption", style="magenta", justify="right")
    token_table.add_row("Total AI Tokens Summed", f"{stats['token_stats']['total_consumed']:,}")
    
    # 3. Bug Table
    bug_table = Table(title="🏗️ Drift & Architecture Bugs", border_style="green")
    bug_table.add_column("Issue Status", style="cyan")
    bug_table.add_column("Integrity Count", style="magenta", justify="right")
    bug_table.add_row("Open Architectural Drifts", str(stats['bug_stats']['open']))
    bug_table.add_row("Secured / Resolved", f"[bold green]{stats['bug_stats']['fixed']}[/bold green]")
    
    # Display ALL
    console.print(val_table)
    console.print(token_table)
    console.print(bug_table)
