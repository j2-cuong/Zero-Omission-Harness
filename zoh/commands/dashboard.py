"""
ZOH Dashboard Command
Launches the FastAPI server and opens the browser
"""

import os
import sys
import asyncio
import webbrowser
import uvicorn
import logging
from pathlib import Path
from multiprocessing import Process

from rich.console import Console
from rich.panel import Panel

console = Console()

def run_dashboard_server(host: str = "127.0.0.1", port: int = 8080):
    """Run uvicorn server in a separate process"""
    uvicorn.run("zoh.dashboard.app:app", host=host, port=port, log_level="error")

def launch_dashboard(port: int = 8080):
    """
    1. Start the FastAPI server (subprocess)
    2. Open the default web browser
    3. Wait for termination
    """
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    
    console.print(Panel.fit(f"🚀 Launching ZOH Web Dashboard at {url}", 
                            style="bold blue", 
                            subtitle="Press Ctrl+C to stop"))
    
    # 1. Start Server in a background process
    p = Process(target=run_dashboard_server, args=(host, port))
    p.start()
    
    try:
        # 2. Open Browser
        import time
        time.sleep(2) # Give server a moment to start
        webbrowser.open(url)
        
        # 3. Wait for process
        console.print("   [green]Server is live. Browser opened.[/green]")
        p.join()
        
    except KeyboardInterrupt:
        console.print("\n   [yellow]Stopping ZOH Dashboard...[/yellow]")
        p.terminate()
        p.join()
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]❌ Error launching dashboard: {e}[/red]")
        p.terminate()
        p.join()
        sys.exit(1)
