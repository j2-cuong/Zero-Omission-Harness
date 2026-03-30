# .workflow/interview/OUTPUT_FORMAT.md
> **Vai trò:** Format chuẩn để lưu kết quả phỏng vấn — single source of truth trước khi sinh .agent/
> **Input:** Câu trả lời từ tất cả các interview tiers (0-6)
> **Output:** INTERVIEW_OUTPUT.yaml chứa toàn bộ context
> **Rule:** File này là checkpoint — AI có thể dừng và resume từ đây.

---

## Philosophy: Interview as Checkpoint

```
Tier 0-6 Interview
        ↓
INTERVIEW_OUTPUT.yaml  ← CHECKPOINT (AI có thể dừng)
        ↓
Phân tích → Sinh .agent/
```

**Lợi ích:**
- AI không bị mất context sau phỏng vấn dài
- Có thể review và sửa trước khi tiếp tục
- Multiple AI có thể làm việc từ cùng một output
- Version control cho requirements

---

## Output File Location

```
.workflow/interview/
├── completed/
│   └── INTERVIEW_OUTPUT_{timestamp}.yaml  # Archive
└── INTERVIEW_OUTPUT.yaml                    # Current (active)
```

---

## Schema INTERVIEW_OUTPUT.yaml

```yaml
interview:
  metadata:
    version: "1.0.0"
    date: "2026-03-30"
    ai_id: "Claude-3.7"
    tiers_completed: [0, 1, 2, 3, 4, 5, 6]  # Hoặc subset nếu skip
    status: "complete|partial|needs_review"
    
  # === TIER 0: Basic Info ===
  project:
    name: ""
    version: "0.1.0"
    purpose: ""
    state: "greenfield|brownfield|refactor"
    
  # === TIER 1: Architecture ===
  architecture:
    components: []
    data_flow: ""
    concurrency: "single-threaded|multi-threaded|async|coroutines"
    
  # === TIER 2: Contracts ===
  contracts:
    internal_api: "yes|no"
    external_api: "none|REST|GraphQL|gRPC"
    ipc: "none|named-pipes|sockets|shared-memory|gRPC"
    pinvoke: "none|csharp-to-cpp|cpp-to-csharp|both"
    
  # === TIER 3: Constraints (Optional) ===
  constraints:
    performance:
      latency_ms: null
      throughput_rps: null
    memory:
      limit_mb: null
      type: "none|embedded|server"
    security:
      has_sensitive_data: false
      compliance: []
      
  # === TIER 4: Technology (Deep Dive) ===
  technology:
    frameworks:
      primary: ""
      secondary: []
      testing: ""
      logging: ""
      
    data_storage:
      local:
        type: "file|sqlite|registry"
        format: "json|xml|binary"
      remote:
        type: "database|api|cloud"
        protocol: ""
      cache:
        type: "none|memory|redis|disk"
        strategy: ""
      config:
        source: "env|file|cli"
        
    network:
      protocol: "none|http|websocket|grpc|tcp"
      authentication: "none|apikey|oauth|jwt|cert"
      retry_strategy: "none|immediate|exponential"
      timeout_ms: 5000
      
    build_deploy:
      build_system: ""
      ci_cd: "none|github-actions|azure-devops|gitlab"
      deployment_target: "local|server|cloud|mobile|embedded"
      packaging: "executable|library|container|installer"
      update_mechanism: "manual|auto|rolling"
      
    dev_tools:
      ide: ""
      debugger: ""
      profiler: ""
      static_analysis: []
      version_control: "git|svn|mercurial"
      
    platform_specific:
      windows: []
      linux: []
      macos: []
      
  # === TIER 5: Performance (Deep Dive) ===
  performance:
    requirements:
      startup_time_ms: null
      response_time_ms: null
      throughput_rps: null
      concurrent_users: null
      data_volume_gb: null
      
    resource_constraints:
      memory_peak_mb: null
      memory_per_request_mb: null
      cpu_cores: null
      cpu_target_percent: null
      disk_space_gb: null
      iops: null
      network_mbps: null
      
    bottleneck_prediction: []
    
    optimization_strategy:
      caching_layers: []
      async_processing: false
      batch_operations: false
      connection_pooling: false
      lazy_loading: false
      
    profiling_plan:
      tools: []
      metrics: []
      benchmarks: []
      
    trade_offs:
      memory_vs_speed: ""
      latency_vs_throughput: ""
      complexity_vs_performance: ""
      
  # === TIER 6: Exceptions (Deep Dive) ===
  exceptions:
    error_handling:
      approach: "exceptions|error-codes|hybrid|logging"
      recovery_strategy: []
      
    expected_failures:
      io_errors: ["file_not_found", "permission_denied"]
      network_errors: ["timeout", "connection_reset"]
      input_errors: ["invalid_format", "out_of_range"]
      resource_errors: ["out_of_memory", "too_many_files"]
      
    unexpected_failures:
      crash_handling:
        generate_dump: true
        auto_restart: false
        error_reporting: ""
      data_integrity:
        transactions: false
        idempotency: false
        validation: []
        backup_recovery: ""
        
    edge_cases:
      input_boundaries: []
      resource_exhaustion: []
      timing_issues: []
      external_changes: []
      
    logging:
      levels: ["ERROR", "WARN", "INFO"]
      include_context: true
      include_stack_trace: true
      observability:
        distributed_tracing: false
        metrics: false
        alerting: false
        
  # === BUILD CONFIG (Derived) ===
  build:
    languages:
      primary: ""
      secondary: []
    dependencies: []
    compiler_flags: []
    
  # === QUALITY GATES ===
  quality:
    test_coverage: "none|unit|integration|e2e|full"
    special_tests: []
    cicd: ""
    
  # === DOCUMENTATION ===
  documentation:
    outputs: []
    consumers: ""
    
  # === ANALYSIS NOTES ===
  analysis:
    # AI ghi chú trong quá trình phỏng vấn
    open_questions: []
    assumptions: []
    risks: []
    recommendations: []
    
  # === NEXT STEPS ===
  next_actions:
    - "Phân tích và tạo .agent/"
    - "Generate component_tree.yaml"
    - "Setup STATE.md"
```

---

## Validation Checklist

Trước khi đánh dấu interview complete:

```yaml
validation:
  required_fields:
    - "project.name"
    - "project.purpose"
    - "architecture.components"
    - "technology.frameworks.primary"
    
  conditional_required:
    - if: "contracts.external_api != none"
      then: "network.authentication"
      
    - if: "architecture.concurrency == multi-threaded"
      then: "performance.optimization_strategy"
      
    - if: "constraints.security.has_sensitive_data"
      then: "constraints.security.compliance"
      
  recommendations:
    - "Nên có ít nhất 1 testing framework"
    - "Nên có logging strategy"
    - "Nên có error handling approach"
```

---

## Resume from Checkpoint

Nếu AI cần dừng sau phỏng vấn:

```yaml
# INTERVIEW_OUTPUT.yaml đã lưu
# AI mới đọc file này:

resume_workflow:
  - read: ".workflow/interview/INTERVIEW_OUTPUT.yaml"
  - validate: "Check completeness"
  - if_complete: 
      action: "Phân tích và tạo .agent/"
  - if_partial:
      action: "Tiếp tục interview từ tier chưa xong"
```

---

*File này là bridge giữa interview và implementation.*
