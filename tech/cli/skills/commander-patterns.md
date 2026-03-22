# CLI Commander Patterns Skill

> Tech Stack: Node.js + TypeScript + Commander  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Commander 基础

### 1.1 基本命令

```ts
import { Command } from 'commander';

const program = new Command();

program
  .name('mycli')
  .description('CLI description')
  .version('1.0.0');

program.parse(process.argv);
```

### 1.2 子命令

```ts
program
  .command('init')
  .description('Initialize project')
  .action(() => {
    console.log('Init project');
  });
```

---

## 2. 参数处理

| 参数 | 说明 |
|------|------|
| `<required>` | 必需参数 |
| `<required> [optional]` | 可选参数 |
| `-n <name>` | 短选项 |
| `--name <name>` | 长选项 |

---

## 3. Options

```ts
program
  .option('-n, --name <name>', 'User name')
  .option('-f, --force', 'Force action')
  .parse();
```

---

## 4. 交互式提示

```ts
import inquirer from 'inquirer';

const { name } = await inquirer.prompt({
  type: 'input',
  name: 'name',
  message: 'Project name?',
});
```

---

## 5. 模板

```bash
#!/usr/bin/env node
import { Command } from 'commander';

const program = new Command();

program
  .name('cli-tool')
  .description('CLI tool')
  .version('1.0.0');

program.parse(process.argv);
```
