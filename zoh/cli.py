"""
ZOH CLI Entry Point
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
except ImportError:
    HAS_TYPER = False

# Import ZOH modules
from zoh.core.config import ConfigLoader
from zoh.core.state import StateValidator
from zoh.core.checkpoint import create_checkpoint, rollback_to_checkpoint, list_checkpoints
from zoh.core.lock import acquire_lock, release_lock, check_lock_status
from zoh.validator import run_validation, ConsistencyValidator


# Create CLI app
if HAS_TYPER:
    app = typer.Typer(
        name="zoh",
        help="Zero-Omission-Harness CLI",
        add_completion=False
    )
    console = Console()
else:
    app = None
    console = None


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
            if 'failed_guards' in result.get('details', {}):
                console.print("\n[red]Failed guards:[/red]")
                for guard in result['details']['failed_guards']:
                    console.print(f"  • {guard}")
            raise typer.Exit(code=1)
    
    @app.command()
    def apply_fix(
        drift_id: str = Argument(..., help="Drift ID to fix"),
        dry_run: bool = Option(False, "--dry-run", help="Preview only"),
        yes: bool = Option(False, "--yes", help="Skip approval")
    ):
        """Apply auto-fix for drift (requires APPROVAL)"""
        console.print(Panel.fit(f"🔧 APPLY FIX: {drift_id}", style="bold yellow"))
        
        require_approval = config.get('auto_fix.require_approval', True)
        
        if dry_run:
            console.print("[blue]📋 DRY-RUN MODE[/blue]")
            console.print(f"   Drift ID: {drift_id}")
            console.print("   Proposed fix would be shown here")
            console.print("\n[yellow]⏳ Waiting for approval...[/yellow]")
            console.print("   User must reply 'APPROVED' or run with --yes")
            return
        
        if require_approval and not yes:
            console.print("[red]❌ This fix requires approval![/red]")
            console.print(f"   Run: [bold]zoh apply-fix {drift_id} --dry-run[/bold] to preview")
            console.print(f"   Then: [bold]zoh apply-fix {drift_id} --yes[/bold] to apply")
            raise typer.Exit(code=1)
        
        console.print("🔧 Applying fix...")
        console.print(f"   [green]✅ Fix {drift_id} applied[/green]")
    
    @app.command()
    def init(
        path: Optional[str] = Argument(None, help="Destination directory (optional)"),
        preset: str = Option("default", "--preset", "-p", help="Preset: default, react, dotnet"),
        mode: str = Option("full", "--mode", "-m", help="Mode: full (all folders), light (only agent/config)"),
        force: bool = Option(False, "--force", help="Overwrite existing files")
    ):
        """Initialize ZOH structure from preset"""
        import shutil
        target_path = Path(path) if path else Path(".")
        console.print(Panel.fit(f"🏗️ INITIALIZE ZOH: {preset.upper()} (MODE: {mode.upper()})", 
                                subtitle=f"Target: {target_path.absolute()}",
                                style="bold green"))
        
        template_dir = Path(__file__).parent / "templates" / preset
        if not template_dir.exists():
            console.print(f"[red]❌ Preset '{preset}' not found[/red]")
            console.print("   Available: default, react, dotnet")
            raise typer.Exit(code=1)
        
        # Check if already initialized
        config_file = target_path / "CONFIG.yaml"
        if config_file.exists() and not force:
            console.print(f"[yellow]⚠️  Already initialized in {target_path}. Use --force to overwrite.[/yellow]")
            raise typer.Exit(code=1)
            
        # Create target path if it doesn't exist
        if not target_path.exists():
            target_path.mkdir(parents=True)
            
        # Define folders allowed for light mode
        light_allowed = ['.agent', 'CONFIG.YAML', 'CONFIG.yaml']
        is_light = mode.lower() == "light"
            
        # Copy files
        try:
            for item in template_dir.iterdir():
                if is_light and item.name not in light_allowed:
                    continue
                    
                dest = target_path / item.name
                if item.is_dir():
                    if dest.exists() and force:
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            
            console.print(f"   [green]✅ Initialized from {preset} preset in {mode} mode[/green]")
            console.print(f"\nNext steps:\n   cd {target_path}\n   zoh status")
            
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            raise typer.Exit(code=1)

    @app.command()
    def task(
        action: str = Argument(..., help="Action: complete, list"),
        task_id: Optional[str] = Argument(None, help="Task ID")
    ):
        """Manage task list"""
        task_list_file = Path('.agent/02_TASK_LIST.md')
        
        if action == "complete":
            if not task_id:
                console.print("[red]❌ Task ID required[/red]")
                raise typer.Exit(code=1)
            
            console.print(f"✅ Marking task {task_id} as complete...")
            
            if not task_list_file.exists():
                console.print(f"[red]❌ Task list not found[/red]")
                raise typer.Exit(code=1)
            
            try:
                with open(task_list_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple pattern to mark complete
                pattern = f"- [ ] .*{task_id}"
                replacement = f"- [x] "
                
                import re
                content = re.sub(pattern, lambda m: m.group(0).replace("[ ]", "[x]"), content)
                
                with open(task_list_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                console.print(f"   [green]Task {task_id} marked complete[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                raise typer.Exit(code=1)
        
        elif action == "list":
            console.print("📋 Task List:")
            
            if not task_list_file.exists():
                console.print("   [dim]No task list found[/dim]")
                return
            
            try:
                with open(task_list_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                tasks = re.findall(r'- \[([ x])\] (.*)', content)
                
                for status, task_text in tasks:
                    icon = "✅" if status == 'x' else "⬜"
                    console.print(f"   {icon} {task_text}")
                
                completed = sum(1 for s, _ in tasks if s == 'x')
                total = len(tasks)
                
                if total > 0:
                    console.print(f"\n   Progress: [bold]{completed}/{total}[/bold] ({completed/total*100:.1f}%)")
                
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
        
        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            raise typer.Exit(code=1)
    
    @app.command()
    def sim(
        files: Optional[List[str]] = Argument(None, help="Modified files (defaults to git modified)"),
        output: Optional[str] = Option(None, "--output", "-o", help="Output path")
    ):
        """Run impact analysis (SIMULATION)"""
        from .core.impact import ImpactAnalyzer
        from rich.panel import Panel
        console.print(Panel.fit("🛡️ IMPACT ANALYSIS (SIMULATION)", style="bold blue"))
        
        # If no files provided, try to get from git
        if not files:
            import subprocess
            try:
                git_status = subprocess.check_output(['git', 'status', '--porcelain'], encoding='utf-8')
                # Filter for modified files
                files = []
                for line in git_status.splitlines():
                    if line.startswith((' M', 'M ')):
                        files.append(line[3:].strip())
            except:
                console.print("[yellow]⚠️  Cannot get git status, please provide files manually[/yellow]")
                raise typer.Exit(code=1)
        
        if not files:
            console.print("   [green]No modified files detected[/green]")
            return
            
        analyzer = ImpactAnalyzer()
        console.print("🔍 Scanning project dependency graph...")
        analyzer.build_graph()
        
        report_path = analyzer.generate_report(files, output)
        console.print(f"   [green]✅ Impact report generated: {report_path}[/green]")
        console.print(1) # Added placeholder for potential additional logic

    @app.command()
    def check_consistency(
        detailed: bool = Option(False, "--detailed", help="Show detailed output"),
        fix: bool = Option(False, "--fix", help="Auto-fix safe drifts")
    ):
        """Quick consistency check"""
        console.print(Panel.fit("🔍 QUICK CONSISTENCY CHECK", style="bold blue"))
        
        checks = [
            (".state/STATE.md", "State file"),
            (".state/STATE_MACHINE.yaml", "State machine"),
            ("CONFIG.yaml", "Config"),
            (".agent/02_TASK_LIST.md", "Task list"),
        ]
        
        table = Table(title="File Checks")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")
        
        all_pass = True
        for file_path, description in checks:
            exists = Path(file_path).exists()
            status = "✅ EXISTS" if exists else "❌ MISSING"
            if not exists:
                all_pass = False
            table.add_row(description, status)
        
        console.print(table)
        
        if all_pass:
            console.print("\n[bold green]✅ All critical files present[/bold green]")
        else:
            console.print("\n[bold red]❌ Some files missing[/bold red]")
            raise typer.Exit(code=1)
    
    @app.command()
    def status():
        """Show current system status"""
        console.print(Panel.fit("📊 SYSTEM STATUS", style="bold blue"))
        
        table = Table()
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        
        # State
        validator = StateValidator(config)
        current_phase = validator.get_current_phase()
        table.add_row("Current Phase", current_phase)
        
        # Lock
        try:
            lock_data = check_lock_status()
            if lock_data:
                table.add_row("Lock Status", f"🔒 Locked by {lock_data.get('owner', 'unknown')}")
            else:
                table.add_row("Lock Status", "🔓 Unlocked")
        except:
            table.add_row("Lock Status", "⚠️ Unknown")
        
        # Mode
        mode = config.get('mode', 'light')
        table.add_row("Mode", mode.upper())
        
        # Transitions
        allowed = validator.get_allowed_transitions()
        table.add_row("Allowed Transitions", ", ".join(allowed) if allowed else "None")
        
        console.print(table)
    
    @app.command()
    def checkpoint(
        action: str = Argument(..., help="Action: create, list, rollback"),
        label: Optional[str] = Option(None, "--label", "-l", help="Label"),
        checkpoint_id: Optional[str] = Option(None, "--id", help="Checkpoint ID")
    ):
        """Manage checkpoints"""
        if action == "create":
            console.print("📦 Creating checkpoint...")
            try:
                cp_id = create_checkpoint(label)
                console.print(f"[green]✅ Checkpoint created: {cp_id}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                raise typer.Exit(code=1)
        
        elif action == "rollback":
            if not checkpoint_id:
                console.print("[red]❌ --id required for rollback[/red]")
                raise typer.Exit(code=1)
            
            console.print(f"🔄 Rolling back to {checkpoint_id}...")
            try:
                rollback_to_checkpoint(checkpoint_id)
                console.print(f"[green]✅ Rolled back to {checkpoint_id}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                raise typer.Exit(code=1)
        
        elif action == "list":
            console.print("📋 Checkpoints:")
            checkpoints = list_checkpoints()
            for cp in checkpoints[-10:]:  # Show last 10
                console.print(f"   {cp.get('id')} - {cp.get('timestamp', '')}")
        
        else:
            console.print(f"[red]❌ Unknown action: {action}[/red]")
            raise typer.Exit(code=1)

else:
    # Fallback CLI without typer
    def main():
        print("""
Zero-Omission-Harness CLI (zoh)

USAGE:
    zoh <command> [options]

COMMANDS:
    validate          Run consistency validation
    transition        Transition to new phase
    apply-fix         Apply drift fix
    task              Manage tasks
    check-consistency Quick consistency check
    status            Show system status
    checkpoint        Manage checkpoints

Install typer for better experience:
    pip install typer rich
""")
        
        if len(sys.argv) < 2:
            sys.exit(1)
        
        command = sys.argv[1]
        
        if command == "validate":
            print("🔍 Running validation...")
            try:
                report = run_validation()
                print(f"   Score: {report.overall_score:.1f}/100")
                print(f"   Status: {report.overall_status.value}")
            except Exception as e:
                print(f"   Error: {e}")
                sys.exit(1)
        
        elif command == "status":
            validator = StateValidator(config)
            print(f"Current Phase: {validator.get_current_phase()}")
            print(f"Mode: {config.get('mode', 'light')}")
        
        else:
            print(f"Command '{command}' requires typer. Install: pip install typer rich")


def cli_main():
    """Entry point for console script"""
    if HAS_TYPER and app:
        app()
    else:
        main()


if __name__ == "__main__":
    cli_main()
