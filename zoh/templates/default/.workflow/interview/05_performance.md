# .workflow/interview/05_performance.md
> **Tier:** 5 — Performance & optimization deep dive
> **When:** Khi cần hiệu năng tốt hoặc constraints nghiêm ngặt
> **Next:** Tier 6 hoặc DONE
> **Token estimate:** ~700

---

## 5.1 Performance Requirements (Quantified)

**Hỏi:** Các yêu cầu hiệu năng cụ thể là gì?

**Latency:**
- Startup time: < X giây
- Response time: < X ms cho operation Y
- Time-to-first-byte: < X ms

**Throughput:**
- Requests/giây: X req/s
- Records/giây: X records/s
- Data bandwidth: X MB/s

**Scalability:**
- Concurrent users: X users
- Data volume: X GB/TB/PB
- Horizontal scaling: có cần không?

**Gợi ý nếu user chưa có số:**
- "Thường người dùng chấp nhận chờ bao lâu?"
- "Có giới hạn hardware không?"
- "Cần xử lý peak load không?"

---

## 5.2 Resource Constraints

**Hỏi:** Giới hạn tài nguyên cụ thể?

**Memory:**
- Peak memory: X MB/GB
- Memory per connection/request: X MB
- Long-running stability: memory leak không được vượt X MB

**CPU:**
- Core count giả định: X cores
- CPU usage target: < X%
- Real-time requirements: hard/soft real-time?

**Disk/IO:**
- Disk space: X GB
- IOPS requirement: X IOPS
- Network bandwidth: X Mbps/Gbps

**Power (nếu embedded/mobile):**
- Battery life target
- Power consumption limit

---

## 5.3 Bottleneck Prediction

**Hỏi:** Dự đoán bottleneck sẽ ở đâu?

**Gợi ý user nghĩ về:**
- **I/O bound:** Database, file system, network
- **CPU bound:** Computation, parsing, encoding
- **Memory bound:** Large data structures, caching
- **Lock contention:** Multi-threading, shared resources

**Đề xuất optimization strategy:**
- Caching layers
- Async processing
- Batch operations
- Connection pooling
- Lazy loading

---

## 5.4 Profiling & Monitoring

**Hỏi:** Làm sao để đo và monitor hiệu năng?

**Profiling:**
- CPU profiler: vtune, perf, Visual Studio Profiler
- Memory profiler: valgrind, dotMemory, heaptrack
- I/O tracing: strace, dtrace, ETW

**Monitoring (runtime):**
- Metrics: latency histogram, throughput counter
- Alerting: thresholds cho latency, error rate
- Dashboard: real-time monitoring

**Benchmarking:**
- Load testing: k6, JMeter, Locust
- Stress testing: tìm breaking point
- Soak testing: long-running stability

---

## 5.5 Optimization Trade-offs

**Hỏi:** Sẵn sàng trade-off gì cho hiệu năng?

**Thường gặp:**
- Memory vs Speed: cache nhiều → nhanh nhưng tốn RAM
- Latency vs Throughput: batch processing
- Complexity vs Performance: optimization code phức tạp hơn
- Accuracy vs Speed: approximation algorithms

---

## Output sau Tier 5

```yaml
tier: 5
result:
  performance:
    latency: {}       # Startup, response, TTFB
    throughput: {}    # req/s, records/s, MB/s
    scalability: {}   # Users, data volume
    
  resource_constraints:
    memory: {}        # Peak, per-request
    cpu: {}           # Cores, usage target
    disk_io: {}       # Space, IOPS
    
  bottleneck_prediction: []
  optimization_strategy: []
  
  profiling_plan:
    tools: []
    metrics: []
    benchmarks: []
    
  trade_offs_accepted: []

next_tier: 6  # Exceptions
```
