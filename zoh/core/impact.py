"""
ZOH Impact Analyzer (Phase 1)
Scope: C#, React, TypeScript, JavaScript
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional


class ImpactAnalyzer:
    """Phân tích vùng ảnh hưởng của thay đổi dựa trên Dependency Graph"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.graph: Dict[str, Set[str]] = {} # file -> list of files that depend on it
        
    def build_graph(self, extensions: List[str] = ['.cs', '.js', '.jsx', '.ts', '.tsx']):
        """Xây dựng đồ thị phụ thuộc"""
        self.graph = {}
        all_files = []
        for ext in extensions:
            all_files.extend(self.root_dir.rglob(f'*{ext}'))
            
        for file_path in all_files:
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
                
            parents = self._get_dependencies(file_path)
            for parent in parents:
                if parent not in self.graph:
                    self.graph[parent] = set()
                self.graph[parent].add(str(file_path))
                
    def _get_dependencies(self, file_path: Path) -> List[str]:
        """Trích xuất dependencies từ file content"""
        deps = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # C# using
            if file_path.suffix == '.cs':
                matches = re.findall(r'using\s+([\w.]+);', content)
                deps.extend(matches)
                
            # JS/TS imports
            elif file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                # import ... from '...'
                matches = re.findall(r"import\s+.*?\s+from\s+['\"](.*?)['\"]", content)
                for m in matches:
                    deps.append(self._resolve_path(file_path, m))
                    
                # require('...')
                matches = re.findall(r"require\(['\"](.*?)['\"]\)", content)
                for m in matches:
                    deps.append(self._resolve_path(file_path, m))
        except:
            pass
        return [d for d in deps if d]

    def _resolve_path(self, current_file: Path, import_path: str) -> Optional[str]:
        """Resolve đường dẫn import tương đối thành absolute-like path (stem)"""
        if import_path.startswith('.'):
            target = (current_file.parent / import_path).resolve()
            return target.stem
        return import_path.split('/')[-1] # Simple resolve for modules

    def get_impact(self, modified_files: List[str]) -> Dict[str, List[str]]:
        """Lấy danh sách các file bị ảnh hưởng bởi danh sách file thay đổi"""
        impact_map = {}
        for f in modified_files:
            file_stem = Path(f).stem
            # Tìm trong graph các file phụ thuộc vào stem này hoặc full path này
            affected = set()
            if f in self.graph:
                affected.update(self.graph[f])
            if file_stem in self.graph:
                affected.update(self.graph[file_stem])
                
            if affected:
                impact_map[f] = list(affected)
        return impact_map

    def generate_report(self, modified_files: List[str], output_path: str = None) -> str:
        """Sinh báo cáo Impact Analysis dưới dạng Markdown"""
        impact = self.get_impact(modified_files)
        
        run_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        if not output_path:
            output_path = f".sim/dry_run_{run_id}.md"
            
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        md = [
            f"# 🛡️ Impact Analysis Report - {run_id}",
            f"**Timestamp:** {datetime.utcnow().isoformat()}",
            "\n## 🎯 Modified Files & Blast Radius",
            "| File Thay Đổi | Số File Ảnh Hưởng | Độ Rủi Ro |",
            "| :--- | :---: | :---: |"
        ]
        
        for f, affected in impact.items():
            risk = "HIGH" if len(affected) > 5 else "MEDIUM" if len(affected) > 0 else "LOW"
            md.append(f"| `{f}` | {len(affected)} | {risk} |")
            
        if impact:
            md.append("\n## 🔬 Detailed Affected Files")
            for f, affected in impact.items():
                md.append(f"\n### `{f}` -> Dependencies:")
                for aff in affected:
                    md.append(f"- [ ] `{aff}`")
        else:
            md.append("\n**Không phát hiện ảnh hưởng trực tiếp đến các file khác.**")
            
        content = "\n".join(md)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return output_path

from datetime import datetime
