# Output Reports

> Platform: Nuwax  
> Version: 1.0.0

---

## 报告类型

| 报告 | 说明 | 生成时机 |
|------|------|----------|
| `build-report.json` | 构建报告 | 构建后 |
| `mcp-report.json` | MCP 调用报告 | MCP 操作后 |
| `test-report.json` | 测试报告 | 测试后 |

## MCP 报告

```json
{
  "invocations": 10,
  "successful": 9,
  "failed": 1,
  "totalDuration": 5000
}
```

## 报告位置

```
output/
├── build-report.json
├── mcp-report.json
└── test-report.json
```
