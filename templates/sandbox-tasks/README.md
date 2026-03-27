# Sandbox 任务模板

> 基于 NuwaClaw Sandbox 实施的可复用模板

---

## 快速开始

### 1. 创建沙箱实例

```bash
# 使用 sandbox-create 模板
cp templates/sandbox-create.md harness/base/tasks/my-sandbox.md

# 编辑配置
vim harness/base/tasks/my-sandbox.md
```

### 2. 执行沙箱命令

```bash
# 使用 sandbox-execute 模板
./scripts/harness execute --task sandbox-execute
```

### 3. 清理资源

```bash
# 使用 sandbox-cleanup 模板
./scripts/harness cleanup --task sandbox-cleanup
```

---

## 任务模板

### sandbox-create

**用途**: 创建沙箱实例

**输入参数**:
```typescript
{
  mode: "off" | "on-demand" | "non-main" | "all",
  platform: { darwin, linux, win32 },
  network: { enabled, allowedDomains, deniedDomains },
  filesystem: { allowRead, denyRead, allowWrite, denyWrite },
  resources: { memory, cpu, timeout }
}
```

**输出**:
```typescript
{
  sandbox: SandboxInterface,
  status: { available, type, platform }
}
```

**前置条件**:
- platform-detect gate passed
- config-validate gate passed

---

### sandbox-execute

**用途**: 在沙箱中安全执行命令

**输入参数**:
```typescript
{
  sandbox: SandboxInterface,
  command: string,
  cwd: string,
  options?: {
    timeout: number,
    signal: AbortSignal,
    onOutput: (data) => void
  }
}
```

**输出**:
```typescript
{
  exitCode: number,
  stdout: string,
  stderr: string,
  duration: number
}
```

**安全策略**:
- 命令黑名单检查
- 网络访问验证
- 文件系统权限检查

---

### sandbox-cleanup

**用途**: 清理沙箱资源

**输入参数**:
```typescript
{
  sandbox: SandboxInterface,
  options?: {
    force: boolean,
    timeout: number,
    keepLogs: boolean
  }
}
```

**输出**:
```typescript
{
  status: "success" | "partial" | "failed",
  cleaned: {
    processes: number,
    tempFiles: number,
    memory: number,
    connections: number
  }
}
```

---

## 平台配置

### macOS (darwin)

**配置文件**: `harness/projects/darwin/sandbox-config.md`

**技术**: sandbox-exec (Seatbelt)

**要求**:
- macOS 10.5+
- 应用正确签名

**配置模板**:
```scheme
(version 1)
(allow default)
(allow file-read* (subpath "${WORKSPACE}"))
(allow file-write* (subpath "${WORKSPACE}"))
(deny file-read* (subpath "~/.ssh"))
```

---

### Linux

**配置文件**: `harness/projects/linux/sandbox-config.md`

**技术**: bubblewrap (bwrap)

**要求**:
- bubblewrap
- socat
- ripgrep

**安装**:
```bash
# Debian/Ubuntu
sudo apt install bubblewrap socat ripgrep

# Fedora
sudo dnf install bubblewrap socat ripgrep
```

**配置模板**:
```bash
bwrap \
  --ro-bind /usr /usr \
  --bind ${WORKSPACE} ${WORKSPACE} \
  --unshare-all \
  --die-with-parent \
  bash -c "${COMMAND}"
```

---

### Windows (win32)

**配置文件**: `harness/projects/win32/sandbox-config.md`

**技术**: Codex Sandbox (Rust)

**要求**:
- Windows 10/11
- nuwax-sandbox.exe

**配置模板**:
```json
{
  "command_timeout": 300,
  "memory_limit": "2g",
  "network": {
    "enabled": true,
    "allowed_domains": ["github.com"]
  }
}
```

---

## 质量门禁

### Gate 1: config-validate

```typescript
async function gate_configValidate(config: SandboxConfig) {
  if (!config.mode) return { passed: false, reason: "Missing mode" };
  if (!["off", "on-demand", "non-main", "all"].includes(config.mode)) {
    return { passed: false, reason: "Invalid mode" };
  }
  return { passed: true };
}
```

### Gate 2: platform-detect

```typescript
async function gate_platformDetect() {
  const platform = os.platform();
  if (!["darwin", "linux", "win32"].includes(platform)) {
    return { passed: false, reason: `Unsupported: ${platform}` };
  }
  return { passed: true, data: { platform } };
}
```

### Gate 3: sandbox-init

```typescript
async function gate_sandboxInit(sandbox: SandboxInterface) {
  if (!await sandbox.isAvailable()) {
    return { passed: false, reason: "Sandbox not available" };
  }
  return { passed: true };
}
```

### Gate 4: execute-test

```typescript
async function gate_executeTest(sandbox: SandboxInterface) {
  try {
    const result = await sandbox.execute("echo test", "/tmp");
    if (result.exitCode !== 0) {
      return { passed: false, reason: result.stderr };
    }
    return { passed: true };
  } catch (error) {
    return { passed: false, reason: error.message };
  }
}
```

### Gate 5: integration-test

```typescript
async function gate_integrationTest() {
  const tests = [
    testBasicExecution(),
    testNetworkIsolation(),
    testFilesystemIsolation(),
  ];
  
  for (const test of tests) {
    const result = await test();
    if (!result.passed) return result;
  }
  
  return { passed: true };
}
```

---

## 最佳实践

### 1. 错误处理

```typescript
try {
  const sandbox = await createSandbox(config);
  const result = await executeInSandbox(sandbox, command, cwd);
} catch (error) {
  if (error.code === 'SANDBOX_UNAVAILABLE') {
    // 降级到无沙箱执行
    return executeUnsandboxed(command, cwd);
  }
  throw error;
}
```

### 2. 资源清理

```typescript
const sandbox = await createSandbox(config);

try {
  await executeInSandbox(sandbox, command, cwd);
} finally {
  await cleanupSandbox(sandbox);  // 总是清理
}
```

### 3. 超时控制

```typescript
const result = await executeInSandbox(sandbox, command, cwd, {
  timeout: 300,  // 5 分钟
  signal: abortController.signal
});
```

---

## 示例项目

- [NuwaClaw Sandbox](https://github.com/nuwax-ai/nuwaclaw) - 完整实现
- [OpenAI Codex](https://github.com/openai/codex) - Windows Sandbox 参考
- [Anthropic Sandbox Runtime](https://www.npmjs.com/package/@anthropic-ai/sandbox-runtime) - 跨平台方案

---

**更新时间**: 2026-03-27
**维护者**: dongdada29
