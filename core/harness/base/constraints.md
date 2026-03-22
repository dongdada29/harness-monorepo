# Harness Core Constraints

> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Core Principles

- Default Deny (默认拒绝)
- Sandbox Inside = Fully Trusted
- Checkpoint Before Action
- Metric Everything

---

## 2. Checkpoint System

| Checkpoint | 说明 |
|------------|------|
| CP0 | 初始化 |
| CP1 | 任务规划 |
| CP2 | 执行 |
| CP3 | 验证 |
| CP4 | 完成 |

---

## 3. Allowed Paths

- ~/workspace/**
- ~/projects/**
- /tmp/harness/**

---

## 4. Blocked Paths

- ~/.ssh/**
- /etc/**
- ~/.aws/**
