"""
ZOH MCP Server
Exposes ZOH tools (Validation, Transitions, Maps) to AI Models (Claude, etc.)
Model Context Protocol - STDIO Transport
"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp.server.stdio import stdio_server
from mcp.server import Server, NotificationOptions
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from zoh.validator import run_validation
from zoh.core.state import StateValidator
from zoh.core.config import ConfigLoader

# Initialize ZOH core
config = ConfigLoader()
config_path = str(Path("CONFIG.yaml"))

# Configure logging to stderr (stdio server uses stdout for protocol)
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("zoh.mcp")

# --- MCP Server Setup ---
server = Server("zoh-governance-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available ZOH governance tools"""
    return [
        Tool(
            name="validate_state",
            description="Run full ZOH consistency validation (AST + Source Code + State)",
            inputSchema={
                "type": "object",
                "properties": {
                    "phase": {"type": "string", "description": "Optional phase to validate"}
                }
            }
        ),
        Tool(
            name="transition_phase",
            description="Transition project to a new phase. ZOH will verify checksum locks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_phase": {"type": "string", "description": "Target phase name (e.g. 'coding', 'review')"},
                    "logic": {"type": "string", "description": "Short explanation for transition"}
                },
                "required": ["to_phase"]
            }
        ),
        Tool(
            name="read_project_map",
            description="Retrieve the project architecture and file map from .map/ directory",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool execution requests from the AI"""
    if name == "validate_state":
        try:
            report = run_validation(config_path=config_path)
            status = "PASSED" if report.overall_status.value == "pass" else "FAILED"
            content = f"Validation Status: {status}\nScore: {report.overall_score}/100\nDetails: {report.to_dict()}"
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "transition_phase":
        to_phase = arguments.get("to_phase") if arguments else None
        if not to_phase:
            return [TextContent(type="text", text="Error: to_phase is required")]
            
        validator = StateValidator(config)
        result = validator.transition(to_phase)
        
        if result['success']:
            return [TextContent(type="text", text=f"Successfully transitioned to {to_phase}")]
        else:
            return [TextContent(type="text", text=f"Transition FAILED: {result['message']}")]

    elif name == "read_project_map":
        # Scan .map/ and return content
        map_dir = Path(".map")
        if not map_dir.exists():
            return [TextContent(type="text", text="Error: .map/ directory not found.")]
            
        files_data = {}
        for map_file in map_dir.glob("*.md"):
            files_data[map_file.name] = map_file.read_text(encoding="utf-8")
            
        return [TextContent(type="text", text=json.dumps(files_data, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="zoh-governance-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
