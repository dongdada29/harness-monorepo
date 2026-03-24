# Universal Configuration

> Platform: Electron  
> Version: 1.0.0

---

## 跨平台配置

Electron 支持多平台构建。

## 支持平台

| 平台 | 格式 |
|------|------|
| macOS | .dmg, .pkg |
| Windows | .exe, .msi |
| Linux | .AppImage, .deb |

## 构建命令

```bash
# macOS
pnpm build:mac

# Windows
pnpm build:win

# Linux
pnpm build:linux

# All
pnpm build:all
```

## 应用配置

```json
{
  "app": {
    "id": "com.example.app",
    "name": "MyApp",
    "version": "1.0.0"
  }
}
```
