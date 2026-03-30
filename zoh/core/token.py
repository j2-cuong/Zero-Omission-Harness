"""
ZOH Token & Budget Manager
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime


class TokenManager:
    """Quản lý budget token và chi phí theo phase"""
    
    def __init__(self, config: 'ConfigLoader'):
        self.config = config
        self.budget_file = Path(config.get('token.budget_file', '.token/budget.yaml'))
        self.log_dir = Path(config.get('token.log_dir', '.token/logs'))
        
    def get_budget(self, phase: str) -> int:
        """Lấy budget cho một phase từ config"""
        budget = self.config.get(f'token.phases.{phase}.budget', 0)
        return budget
        
    def get_usage(self, phase: str) -> int:
        """Lấy usage hiện tại của một phase từ budget file"""
        if not self.budget_file.exists():
            return 0
            
        try:
            with open(self.budget_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                return data.get('usage', {}).get(phase, 0)
        except:
            return 0
            
    def update_usage(self, phase: str, amount: int):
        """Cập nhật usage cho một phase"""
        self.budget_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        if self.budget_file.exists():
            try:
                with open(self.budget_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
            except:
                pass
                
        if 'usage' not in data:
            data['usage'] = {}
            
        current = data['usage'].get(phase, 0)
        data['usage'][phase] = current + amount
        data['last_updated'] = datetime.utcnow().isoformat()
        
        with open(self.budget_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f)
            
    def is_within_budget(self, phase: str) -> bool:
        """Kiểm tra xem phase hiện tại có còn budget không"""
        budget = self.get_budget(phase)
        if budget <= 0: # 0 means unlimited or not tracked
            return True
            
        usage = self.get_usage(phase)
        return usage < budget
        
    def get_remaining(self, phase: str) -> int:
        """Lấy lượng token còn lại"""
        budget = self.get_budget(phase)
        usage = self.get_usage(phase)
        return max(0, budget - usage)
