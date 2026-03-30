"""
ZOH AST Parser - Programmatic Contract Verification
Supports: Python (FastAPI, Flask, Django), TypeScript/JavaScript (Node.js subprocess)
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import libcst as cst
    from libcst import matchers as m
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False

logger = logging.getLogger("zoh.ast_parser")


class PythonRouteCollector(cst.CSTVisitor):
    """Vistor to collect routes from Python code using libcst matchers"""
    
    def __init__(self):
        self.routes = []
        
    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        for decorator in node.decorators:
            # Match @app.get("/path"), @router.post("/path"), etc.
            if m.matches(decorator.decorator, m.Call(
                func=m.Attribute(
                    value=m.Name(value=m.MatchIfTrue(lambda v: v in ("app", "router"))),
                    attr=m.Name(value=m.MatchIfTrue(lambda v: v in ("get", "post", "put", "delete", "patch", "route")))
                )
            )):
                self._extract_route(decorator.decorator, node.name.value)
            
            # Match @app.route("/path", methods=["GET"])
            elif m.matches(decorator.decorator, m.Call(
                func=m.Attribute(
                    value=m.Name(value="app"),
                    attr=m.Name(value="route")
                )
            )):
                self._extract_route(decorator.decorator, node.name.value)
                
        return True

    def _extract_route(self, call_node: cst.Call, handler: str):
        path = "/"
        methods = ["GET"]
        
        # First argument is usually the path
        if call_node.args:
            path_arg = call_node.args[0].value
            if isinstance(path_arg, cst.SimpleString):
                path = path_arg.evaluated_value
        
        # Check for methods keyword
        for arg in call_node.args:
            if m.matches(arg, m.Arg(keyword=m.Name("methods"))):
                if isinstance(arg.value, cst.List):
                    methods = [el.value.evaluated_value.upper() for el in arg.value.elements if isinstance(el.value, cst.SimpleString)]
        
        # Handle @app.get, @app.post etc.
        if m.matches(call_node.func, m.Attribute()):
            attr_name = call_node.func.attr.value
            if attr_name in ("get", "post", "put", "delete", "patch"):
                methods = [attr_name.upper()]

        for method in methods:
            self.routes.append({
                "method": method,
                "path": path,
                "handler": handler
            })


class PythonASTParser:
    """Analyzes Python files for API endpoints"""
    
    def __init__(self):
        if not HAS_LIBCST:
            logger.warning("libcst not installed. Python AST parsing disabled.")

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        if not HAS_LIBCST:
            return []
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                module = cst.parse_module(f.read())
            
            collector = PythonRouteCollector()
            module.visit(collector)
            return collector.routes
        except Exception as e:
            logger.error(f"Error parsing Python file {file_path}: {e}")
            return []


class TSASTParser:
    """Analyzes TS/JS files using a Node.js helper script"""
    
    def __init__(self, deps_dir: str = ".agent/.zoh_deps"):
        self.deps_dir = Path(deps_dir)
        self.parser_script = Path(__file__).parent / "ts_parser.js"

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        if not self._check_node():
            return []
            
        try:
            # Set NODE_PATH to include our local deps
            env = os.environ.copy()
            node_modules = self.deps_dir / "node_modules"
            if node_modules.exists():
                env["NODE_PATH"] = str(node_modules.absolute())
            
            result = subprocess.run(
                ["node", str(self.parser_script), str(file_path)],
                capture_output=True,
                text=True,
                env=env,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning(f"TS Parser failed for {file_path}: {result.stderr}")
                return []
                
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error calling TS parser for {file_path}: {e}")
            return []

    def _check_node(self) -> bool:
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            return True
        except:
            logger.error("\033[91mNode.js not found. TS/JS parsing skipped.\033[0m")
            return False


class UnifiedASTParser:
    """Entry point for all AST-based parsing"""
    
    def __init__(self):
        self.py_parser = PythonASTParser()
        self.ts_parser = TSASTParser()

    def get_endpoints(self, file_path: Path) -> List[Dict[str, Any]]:
        ext = file_path.suffix
        if ext == ".py":
            return self.py_parser.parse(file_path)
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            return self.ts_parser.parse(file_path)
        return []
