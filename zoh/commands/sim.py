"""
ZOH Simulation Command
Refactored to include real-world static analysis (Mypy, Ruff, ESLint) 
and AI-driven Impact Analysis Reports.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from zoh.analyzers.static_analyzer import StaticAnalyzer
from zoh.core.config import ConfigLoader
from zoh.core.ai_provider import OpenAIProvider, DummyProvider, AIProvider

logger = logging.getLogger("zoh.sim")

class SimulationRunner:
    """Orchestrates Impact Analysis by combining static analysis and AI reasoning"""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.analyzer = StaticAnalyzer()
        self.provider = self._init_provider()
        
    def _init_provider(self) -> AIProvider:
        """Initialize provider based on config/environment"""
        provider_name = self.config.get("ai_provider", "openai").lower()
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Mode check: Dummy if missing key and not in strict mode
        is_strict = self.config.get("mode") == "strict"
        
        if provider_name == "dummy" or (not api_key and not is_strict):
            return DummyProvider()
            
        return OpenAIProvider(api_key=api_key)

    def run_sim(self, files: List[str]) -> Path:
        """
        Run simulation:
        1. Get REAL results from Static Analyzers (Mypy, Ruff, ESLint).
        2. Combine these results with the target files context.
        3. Prompt AI for an Impact Analysis report.
        """
        # 1. Real Data: Run Static Analyzers
        static_results = self.analyzer.run_all()
        
        # 2. Build AI Context
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "target_files": files,
            "static_analysis_errors": static_results,
            "impact_boundaries": self._get_impact_boundaries(files)
        }
        
        # 3. Request AI reasoning
        report_content = self._generate_ai_report(context)
        
        # 4. Save to .sim/ with timestamp
        sim_dir = Path(".sim")
        sim_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = sim_dir / f"impact_{timestamp}.md"
        report_path.write_text(report_content, encoding="utf-8")
        
        return report_path

    def _get_impact_boundaries(self, files: List[str]) -> List[str]:
        """Simple dependency scan placeholder"""
        # In a future phase, this will use the dependency graph
        return [f"Potentially affected: {f}" for f in files]

    def _generate_ai_report(self, context: Dict[str, Any]) -> str:
        """AI Synthesizes static errors and code intent into a human-readable report"""
        prompt = f"""
        You are a Senior System Architect. 
        Analyze the following modification attempt and the static analysis results.
        
        CONTEXT:
        {json.dumps(context, indent=2)}
        
        TASK:
        Generate a detailed IMPACT REPORT in Markdown.
        Include:
        - Summary of actual linter/compiler errors found.
        - Analysis of cascading risks (how these errors affect other parts of the system).
        - Blast Radius assessment (Level 1: Low to Level 3: Critical).
        - Actionable fix strategies.
        
        FORMAT: Strictly Markdown.
        """
        
        # Using verify_compliance as a generic request for this phase
        result = self.provider.verify_compliance(prompt, "You are a Senior Architect generating Impact Reports.")
        
        if result.get("compliant"):
            return f"# ZOH Impact Report\n\nGenerated: {context['timestamp']}\n\n{result.get('reason', 'Analysis error')}"
        else:
            return f"# ZOH Impact Report (FALLBACK)\n\nReason: AI returned non-compliant status during analysis.\n{result.get('reason', '')}"

def apply_sim(files: List[str], config: ConfigLoader):
    """Entry point for CLI simulation command"""
    runner = SimulationRunner(config)
    return runner.run_sim(files)
