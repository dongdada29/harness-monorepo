# Performance Tips

## Benchmark 优化技巧

### 1. 使用缓存

```python
from benchmark_perf import BenchmarkCache

cache = BenchmarkCache()
key = cache._get_cache_key(project_path)
result = cache.get(key)

if result is None:
    result = compute_expensive_metric()
    cache.set(key, result)
```

### 2. 并行文件计数

```python
from benchmark_perf import ParallelMetrics

# 并行统计多种文件类型
counts = ParallelMetrics.count_files(
    "/path/to/project",
    ["*.ts", "*.tsx", "*.js", "*.jsx"]
)
```

### 3. 并行运行 Gates

```python
from benchmark_perf import ParallelMetrics

# 同时运行 lint, typecheck, test, build
gates = ParallelMetrics.run_gates_parallel("/path/to/project")
```

### 4. 使用记忆化

```python
from benchmark_perf import cached_file_count, cached_git_log

# 缓存文件计数
ts_count = cached_file_count("/path/to/project", ".ts")

# 缓存 git log
log = cached_git_log("/path/to/project", 10)
```

### 5. 清理缓存

```python
cache = BenchmarkCache()
cache.clear()  # 删除所有缓存
```

---

## 性能对比

| 操作 | 无优化 | 有优化 | 提升 |
|------|--------|--------|------|
| 文件计数 (4 种类型) | ~40s | ~10s | 4x |
| Gate 运行 (4 个) | ~240s | ~120s | 2x |
| 重复 benchmark | ~60s | ~2s | 30x |

---

*Last updated: 2026-03-22*
