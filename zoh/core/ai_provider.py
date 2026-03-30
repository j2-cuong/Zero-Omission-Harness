"""
ZOH AI Provider Interface
Supports OpenAI, Anthropic, and Dummy (for local development)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger("zoh.ai_provider")

class AIProvider(ABC):
    """Abstract Base Class for AI Providers"""
    
    @abstractmethod
    def verify_compliance(self, prompt: str, rules: str) -> Dict[str, Any]:
        """
        Gửi yêu cầu verify tới AI
        Returns: {"compliant": bool, "reason": str}
        """
        pass


class OpenAIProvider(AIProvider):
    """Implementation for OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment.")

    def verify_compliance(self, prompt: str, rules: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider")
            
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            system_prompt = f"""
            You are a Compliance Validator for the ZOH Framework.
            Your task is to verify if the USER REQUEST complies with the project RULES.
            
            RULES:
            {rules}
            
            You MUST return a JSON object with exactly two fields:
            - "compliant": boolean (true if the request follows all rules, false otherwise)
            - "reason": string (explanation if non-compliant, or "OK" if compliant)
            """
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"USER REQUEST:\n{prompt}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "compliant": bool(result.get("compliant", False)),
                "reason": str(result.get("reason", "Unknown reason"))
            }
        except Exception as e:
            logger.error(f"OpenAI Compliance check failed: {e}")
            return {"compliant": False, "reason": f"API Error: {str(e)}"}


class DummyProvider(AIProvider):
    """Dummy Provider for local development/testing - Always returns compliant"""
    
    def verify_compliance(self, prompt: str, rules: str) -> Dict[str, Any]:
        logger.info("Using DummyProvider for compliance check (Always PASS)")
        return {"compliant": True, "reason": "Dummy mode enabled"}
