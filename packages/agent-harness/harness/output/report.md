# Output Reports

> Platform: Agent  
> Version: 1.0.0

---

## 报告类型

| 报告 | 说明 | 生成时机 |
|------|------|----------|
| `build-report.json` | 构建报告 | 构建后 |
| `test-report.json` | 测试报告 | 测试后 |
| `coverage-report.json` | 覆盖率报告 | 测试后 |

## 构建报告

```json
{
  "success": true,
  "platform": "darwin",
  "version": "1.0.0",
  "timestamp": "2026-03-25T01:30:00Z",
  "artifacts": [
    "dist/MyApp-1.0.0.dmg"
  ]
}
```

## 测试报告

```json
{
  "total": 100,
  "passed": 95,
  "failed": 5,
  "skipped": 0,
  "coverage": 82.5
}
```

## 生成位置

```
output/
├── build-report.json
├── test-report.json
└── coverage/
    └── lcov.info
```
