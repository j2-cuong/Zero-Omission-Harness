# .router/05_ARCH.md
> **Vai trò:** Điều phối architecture tasks — text-based diagrams, refactoring, structure analysis.
> **Input:** Arch request từ user
> **Output:** Load context để vẽ diagram hoặc refactor structure
> **Rule:** Architecture phải reflect code reality — dùng text-based formats (Mermaid/YAML) để dễ diff và cập nhật.

---

## Text-First Architecture Philosophy

```
Code thay đổi  →  Cập nhật text-based map  →  Diff trackable
     ↑                ↓                         ↓
   Developer    Mermaid/YAML/ASCII          Git history
                      ↓
              Render SVG (khi cần)
```

**Source of truth:** Text files (`.mmd`, `.yaml`, `.txt`)
**Derived outputs:** SVG/PNG (render khi cần cho presentation)

---

## Arch Task Detection

| User Request | Task Type | Output |
|--------------|-----------|--------|
| `vẽ sơ đồ`, `diagram`, `call graph` | **Generate Diagram** | `.map/current/*.mmd` |
| `kiến trúc`, `architecture`, `structure` | **Update Structure** | `.map/current/component_tree.yaml` |
| `refactor structure`, `reorganize` | **Restructure** | Modify `.agent/01_STRUCTURE.md` + diff |
| `dependency analysis`, `dependencies` | **Dependency Map** | `.map/current/component_tree.yaml` |
| `contract update`, `API thay đổi` | **Contract Update** | Update `.agent/03_*.md` + `.map/diff/` |

---

## Context Loading

**Tất cả arch tasks đều cần:**
1. **`.map/STRUCTURE.md`** — philosophy và format guide
2. **`.agent/01_STRUCTURE.md`** — current structure
3. **`.agent/STATE.md`** — phase và arch-related flags

**Theo task type:**

| Task | Files bổ sung |
|------|---------------|
| Generate Diagram | `.map/current/*.yaml` → generate `.mmd` |
| Update Structure | `.map/current/component_tree.yaml` |
| Restructure | Tất cả `.agent/*.md` + tạo `.map/diff/` |
| Dependency Map | `.map/current/component_tree.yaml` |
| Contract Update | `.agent/DECISION_LOG.md` + `.map/diff/DIFF_FORMAT.md` |

---

## Text-Based Map Generation

### 1. Component Tree (YAML)
```yaml
# .map/current/component_tree.yaml
components:
  core:
    description: "Xử lý logic chính"
    depends_on: []
    entry_points: ["main.cpp:core_init"]
```

**Cập nhật khi:**
- Thêm/xóa component
- Thay đổi dependencies
- Thêm entry points

### 2. Data Flow (Mermaid)
```mermaid
# .map/current/data_flow.mmd
graph TD
    A[User Input] --> B[CLI]
    B --> C[Core]
    C --> D[Storage]
```

**Cập nhật khi:**
- Thay đổi luồng dữ liệu
- Thêm/bớt steps
- Thay đổi protocols

### 3. Call Graph (ASCII/Text)
```
# .map/current/callgraph_core.txt
core::process()
├── validate()
├── transform()
└── store()
```

**Cập nhật khi:**
- Thêm functions mới
- Thay đổi call chains
- Refactor internal logic

---

## Architecture Consistency Check

Kiểm tra drift giữa:
- `.map/current/component_tree.yaml` (text map)
- Code reality (thực tế)
- `.agent/01_STRUCTURE.md` (intended structure)

**Nếu phát hiện mismatch:**
1. Flag trong `STATE.md` (`consistency_flags.map = false`)
2. Report drift details
3. Đề xuất: update map | refactor code | cả hai

---

## Diff & Version Tracking

Khi architecture thay đổi:

1. **Generate diff:** So sánh old vs new
2. **Save diff:** `.map/diff/{version_or_task}.yaml`
3. **Link to task:** `.map/refs/TASK-{id}.yaml`
4. **Update snapshot:** `.map/refs/v{X.Y.Z}/`

### Breaking Change Detection

Tự động detect:
- Xóa component có dependents
- Thay đổi interface signature
- Remove/rename public API
- Thay đổi data flow bắt buộc

**Nếu breaking:**
- Log vào `.map/diff/BREAKING-{date}.yaml`
- Bắt buộc major version bump
- Cần migration guide

---

## Linking: Task/Bug ↔ Map

### Task Reference
```yaml
# .map/refs/TASK-001.yaml
task_id: "TASK-001"
affected_map_nodes:
  components: ["storage"]
  data_flow_changes: ["core → storage"]
map_updated: true
```

### Bug Reference
```yaml
# .map/refs/BUG-2026-0301.yaml
bug_id: "BUG-2026-0301"
affected_nodes:
  component: "storage"
  function: "storage::write()"
  file: "src/storage/write.cpp"
map_snapshot: "v1.0.0"
```

---

## Rendering (Xuất ra SVG/PNG)

Text-based → Visual khi cần:

```bash
# Mermaid CLI
mermaid -i .map/current/data_flow.mmd -o docs/diagrams/

# Hoặc GitHub/GitLab auto-render
# Hoặc VSCode preview
```

**Lưu ý:** SVG là output, không phải source. Không commit SVG gốc.

---

## Token Budget: Architecture

| Task | Est. Tokens | Notes |
|------|-------------|-------|
| Update component tree | ~400 | YAML editing |
| Generate Mermaid diagram | ~600 | Text generation |
| Update call graph | ~500 | ASCII/Text |
| Create diff | ~600 | YAML diff format |
| Full restructure | ~1000 | Impact analysis |

---

## Lazy Loading Strategy (Tiết kiệm token cho .map/)

Khi làm việc với `.map/`, token có thể tăng nhanh. Dùng lazy loading:

### 1. Component-First Loading
Chỉ load component cần thiết:

```yaml
# Thay vì load tất cả map files:
files_to_load:
  - ".map/current/component_tree.yaml"  # Chỉ load tree
  # Không load callgraph của component khác
  
# Khi cần chi tiết 1 component:
files_to_load:
  - ".map/current/callgraph_{specific}.txt"
```

### 2. Tree-Only Mode
Nếu chỉ cần hiểu structure (không cần callgraph):

```yaml
quick_structure_check:
  load: ".map/current/component_tree.yaml"
  skip: ["callgraph_*.txt", "data_flow.mmd"]
  tokens_saved: ~40%
```

### 3. Diff-Only Loading
Khi review changes, chỉ load diff:

```yaml
review_mode:
  load: ".map/diff/{version}.yaml"
  skip: ".map/current/"  # Full map không cần thiết
  tokens_saved: ~60%
```

### 4. Two-Phase Map Tasks
Chia task lớn thành 2 phase:

```
Phase 1: Investigation (minimal map)
    ↓
Load: component_tree.yaml only
Analyze: Impact
    ↓
Phase 2: Update (specific files)
    ↓
Load: Chỉ files cần modify
```

### 5. Token Budget by Map Op

| Operation | Files | Est. Tokens | Lazy Load? |
|-----------|-------|-------------|------------|
| Read component list | 1 | ~200 | No need |
| Read full structure | 3-4 | ~600 | Tree-only |
| Update 1 component | 1-2 | ~400 | Yes |
| Full restructure | 5+ | ~1000 | Two-phase |
| Generate diff | 2 | ~500 | Diff-only |

---

## Post-Arch Actions

```yaml
post_arch:
  - update: ".agent/STATE.md"
    field: "consistency_flags.map"
    value: true
    
  - if_text_map_changed:
    regenerate: "SVG outputs (optional)"
    
  - if_structure_changed:
    create: ".map/diff/{trigger}.yaml"
    update: ".agent/01_STRUCTURE.md"
    
  - if_contract_changed:
    update: ".agent/DECISION_LOG.md"
    check: "Breaking changes?"
    
  - if_task_completed:
    create: ".map/refs/TASK-{id}.yaml"
```

---

## Cross-Language Boundaries

Nếu `languages.primary = multi`:

| Boundary | File | Format |
|----------|------|--------|
| C++ ↔ C# P/Invoke | `.map/current/boundary_pinvoke.mmd` | Mermaid |
| C++ ↔ C# IPC | `.map/current/boundary_ipc.yaml` | YAML |
| Native ↔ React | `.map/current/boundary_frontend.mmd` | Mermaid |

**Mỗi boundary ghi rõ:**
- Data format qua boundary
- Marshaling strategy
- Error handling
- Performance notes

---

*Text-based architecture: diffable, trackable, codeable.*
