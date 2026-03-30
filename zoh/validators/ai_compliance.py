"""
ZOH AI Compliance Validator
Verifies prompts against project rules using AI models
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from zoh.core.config import ConfigLoader
from zoh.core.ai_provider import OpenAIProvider, DummyProvider, AIProvider

logger = logging.getLogger("zoh.ai_compliance")

class AIComplianceValidator:
    """Validator that uses AI to check if the current intent follows master rules"""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
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

    def validate_intent(self, user_request: str) -> bool:
        """
        Validate user request against rules
        Raises Exception if non-compliant to force sys.exit(1)
        """
        rules = self._load_rules()
        
        # Build prompt and query AI
        result = self.provider.verify_compliance(user_request, rules)
        
        if not result.get("compliant", False):
            reason = result.get("reason", "Unknown reason")
            logger.error(f"\033[91m❌ AI COMPLIANCE FAILED!\033[0m")
            logger.error(f"Reason: {reason}")
            raise Exception(f"AI Compliance violation: {reason}")
            
        return True

    def _load_rules(self) -> str:
        """Load Master Prompt (00_MASTER.md) and Gates (.gates/*.md)"""
        rules = []
        
        # 1. Master Prompt
        master_file = Path(".agent/00_MASTER.md")
        if master_file.exists():
            rules.append(f"### PROJECT RULES (MASTER):\n{master_file.read_text(encoding='utf-8')}")
            
        # 2. Validation Gates
        gates_dir = Path(".gates")
        if gates_dir.exists():
            for gate_file in gates_dir.glob("*.md"):
                rules.append(f"### GATE ({gate_file.stem}):\n{gate_file.read_text(encoding='utf-8')}")
                
        return "\n\n".join(rules)
