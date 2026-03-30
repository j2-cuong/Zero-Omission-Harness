"""
ZOH CLI Entry Point
Optimized to delegate logic to specific command modules
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Typer import with fallback
try:
    import typer
    from typer import Option, Argument
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    HAS_TYPER = True
    console = Console()
except ImportError:
    HAS_TYPER = False
    console = None

# Import ZOH core modules
from zoh.core.config import ConfigLoader
from zoh.core.state import StateValidator
from zoh.core.checkpoint import create_checkpoint, rollback_to_checkpoint, list_checkpoints
from zoh.core.lock import acquire_lock, release_lock, check_lock_status
from zoh.validator import run_validation

# Import Phase 3 command logic
from zoh.commands.init import InitManager, show_recommendation_table
from zoh.commands.sim import SimulationRunner
from zoh.commands.metrics import MetricsAggregator, show_dashboard
from zoh.commands.dashboard import launch_dashboard

# Create CLI app
if HAS_TYPER:
    app = typer.Typer(
        name="zoh",
        help="Zero-Omission-Harness CLI",
        add_completion=False
    )
else:
    app = None

# Global config
config = ConfigLoader()

if HAS_TYPER:
    @app.command()
    def validate(
        phase: Optional[str] = Option(None, "--phase", "-p", help="Validate for specific phase"),
        output: Optional[str] = Option(None, "--output", "-o", help="Output report path"),
        strict: bool = Option(False, "--strict", help="Strict mode"),
        verbose: bool = Option(False, "--verbose", "-v", help="Verbose output")
    ):
        """Run consistency validation"""
        console.print(Panel.fit("🔍 ZERO-OMISSION-HARNESS VALIDATION", style="bold blue"))
        
        mode = config.get('mode', 'light')
        if strict:
            mode = 'strict'
        
        console.print(f"Mode: [bold]{mode}[/bold]")
        
        try:
            report = run_validation(
                config_path=str(Path("CONFIG.yaml")),
                output_path=output
            )
            
            table = Table(title="Validation Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Run ID", report.run_id)
            table.add_row("Overall Score", f"{report.overall_score:.1f}/100")
            table.add_row("Status", report.overall_status.value.upper())
            table.add_row("Passed", str(report.passed))
            table.add_row("Failed", str(report.failed))
            table.add_row("Warnings", str(report.warnings))
            
            console.print(table)
            
            if report.overall_status.value == "fail":
                raise typer.Exit(code=1)
                
        except Exception as e:
            console.print(f"[bold red]❌ Validation failed: {e}[/bold red]")
            raise typer.Exit(code=1)
    
    @app.command()
    def transition(
        to_phase: str = Argument(..., help="Target phase"),
        force: bool = Option(False, "--force", help="Skip guards (dangerous)"),
        checkpoint: bool = Option(True, "--checkpoint/--no-checkpoint", help="Create checkpoint")
    ):
        """Transition to new phase (AI MUST use this)"""
        console.print(Panel.fit(f"🔄 STATE TRANSITION: {to_phase}", style="bold yellow"))
        
        # Create checkpoint
        if checkpoint and config.get('checkpoint.enabled', True):
            console.print("📦 Creating checkpoint...")
            try:
                cp_id = create_checkpoint(f"pre_transition_{to_phase}")
                console.print(f"   Checkpoint: [green]{cp_id}[/green]")
            except Exception as e:
                console.print(f"   [yellow]⚠️  {e}[/yellow]")
        
        # Acquire lock
        if config.get('lock.enabled', True):
            console.print("🔒 Acquiring lock...")
            try:
                if acquire_lock(to_phase, config.get('lock.timeout_hours', 2)):
                    console.print("   [green]Lock acquired[/green]")
                else:
                    console.print("   [red]❌ Cannot acquire lock[/red]")
                    raise typer.Exit(code=1)
            except Exception as e:
                console.print(f"   [yellow]⚠️  {e}[/yellow]")
        
        # Perform transition
        validator = StateValidator(config)
        
        if force:
            console.print("[yellow]⚠️  Force mode - skipping guards[/yellow]")
            result = validator.transition(to_phase, force=True)
        else:
            result = validator.transition(to_phase)
        
        if result['success']:
            console.print(f"[bold green]✅ Transitioned to '{to_phase}'[/bold green]")
        else:
            console.print(f"[bold red]❌ Transition failed: {result['message']}[/bold red]")
            raise typer.Exit(code=1)
    
    @app.command()
    def init(
        path: Optional[str] = Argument(None, help="Destination directory (optional)"),
        preset: str = Option("default", "--preset", "-p", help="Preset: default, react, dotnet"),
        mode: str = Option("full", "--mode", "-m", help="Mode: full, light, strict"),
        force: bool = Option(False, "--force", help="Overwrite existing files")
    ):
        """Initialize ZOH structure with project analysis"""
        import shutil
        target_path = Path(path) if path else Path(".")
        
        console.print(Panel.fit(f"🏗️ INITIALIZE ZOH: {preset.upper()}", 
                                subtitle=f"Target: {target_path.absolute()}",
                                style="bold green"))
        
        # 1. Project Analysis (Phase 3)
        init_mgr = InitManager(target_path)
        stats = init_mgr.analyze_project_size()
        show_recommendation_table(stats)
        
        # 2. Template Selection
        template_dir = Path(__file__).parent / "templates" / preset
        if not template_dir.exists():
            console.print(f"[red]❌ Preset '{preset}' not found[/red]")
            raise typer.Exit(code=1)
            
        config_file = target_path / "CONFIG.yaml"
        if config_file.exists() and not force:
            console.print(f"[yellow]⚠️  Already initialized. Use --force to overwrite.[/yellow]")
            raise typer.Exit(code=1)
            
        # 3. Mode Handling
        if not target_path.exists():
            target_path.mkdir(parents=True)
            
        light_allowed = ['.agent', 'CONFIG.YAML', 'CONFIG.yaml']
        is_light = mode.lower() == "light"
            
        # 4. Copy Files
        try:
            for item in template_dir.iterdir():
                if is_light and item.name not in light_allowed:
                    continue
                    
                dest = target_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            
            # 5. Git Safety Setup (Phase 2 & 3)
            init_mgr.setup_git_safety()
            
            console.print(f"   [green]✅ Initialized from {preset} preset[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error during init: {e}[/red]")
            raise typer.Exit(code=1)

    @app.command()
    def sim(
        files: Optional[List[str]] = Argument(None, help="Modified files (defaults to git status)")
    ):
        """Run impact analysis (with Static Analysis & AI)"""
        console.print(Panel.fit("🛡️ IMPACT ANALYSIS (SIMULATION)", style="bold blue"))
        
        if not files:
            import subprocess
            try:
                git_status = subprocess.check_output(['git', 'status', '--porcelain'], encoding='utf-8')
                files = [line[3:].strip() for line in git_status.splitlines() if line.startswith((' M', 'M '))]
            except:
                files = []
        
        if not files:
            console.print("   [green]No modified files detected[/green]")
            return
            
        runner = SimulationRunner(config)
        console.print("🔍 Running static analysis & generating report...")
        
        try:
            report_path = runner.run_sim(files)
            console.print(f"   [green]✅ Impact report generated: {report_path}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Simulation failed: {e}[/red]")

    @app.command()
    def metrics():
        """Show project telemetry and health metrics"""
        aggregator = MetricsAggregator()
        stats = aggregator.aggregate()
        show_dashboard(stats)

    @app.command()
    def status():
        """Show current system status"""
        console.print(Panel.fit("📊 SYSTEM STATUS", style="bold blue"))
        
        table = Table()
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        
        # State
        validator = StateValidator(config)
        table.add_row("Current Phase", validator.get_current_phase())
        
        # Lock
        try:
            lock_data = check_lock_status()
            table.add_row("Lock Status", "🔒 Locked" if lock_data else "🔓 Unlocked")
        except:
            table.add_row("Lock Status", "⚠️ Unknown")
        
        # Mode
        table.add_row("Mode", config.get('mode', 'light').upper())
        
        console.print(table)

    @app.command()
    def dashboard(port: int = Option(8080, "--port", "-p", help="Dashboard port")):
        """Launch the ZOH Web Dashboard for project telemetry"""
        launch_dashboard(port=port)

    @app.command()
    def mcp():
        """Run ZOH as an MCP Server (Model Context Protocol)"""
        from zoh.mcp_server import main
        import asyncio
        asyncio.run(main())

    @app.command()
    def task(action: str, task_id: Optional[str] = None):
        """Simple task management (List/Complete)"""
        if action == "list":
            console.print("📋 Project Tasks (Scan .agent/02_TASK_LIST.md)...")
            # Logic here...
        elif action == "complete" and task_id:
            console.print(f"✅ Marking task {task_id} complete...")
            # Logic here...

    @app.command()
    def checkpoint(action: str, label: Optional[str] = None, checkpoint_id: Optional[str] = None):
        """Manage safety checkpoints"""
        if action == "create":
            create_checkpoint(label)
        elif action == "list":
            for cp in list_checkpoints():
                console.print(f"   {cp['id']} - {cp['timestamp']}")

else:
    # No Typer Fallback
    def main():
        print("ZOH CLI requires 'typer' and 'rich'.")
        sys.exit(1)

def cli_main():
    if app:
        app()
    else:
        main()

if __name__ == "__main__":
    cli_main()
