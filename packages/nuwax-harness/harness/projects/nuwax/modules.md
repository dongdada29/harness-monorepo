# Nuwax Agent OS 模块开发指南

> Nuwax Agent OS 各模块的详细开发规范

---

## 模块概览

| 模块 | 说明 | 技术栈 |
|------|------|--------|
| **AppDev** | Web IDE 开发环境 | React + SSE |
| **Chat** | AI 聊天对话 | React |
| **Workflow** | 工作流编排 | React + AntV X6 |
| **Agent** | Agent 管理 | React |
| **Skills** | Skills 市场 | React |

---

## 1. AppDev Web IDE

### 核心架构

```
src/pages/AppDev/
├── index.tsx                    # 主入口
├── components/
│   ├── FileTree/                # 文件树
│   │   ├── index.tsx
│   │   ├── FileTree.tsx
│   │   ├── FileTree.less
│   │   └── types.ts
│   ├── Editor/                  # 编辑器
│   ├── Terminal/                # 终端
│   └── ChatPanel/              # AI 聊天面板
│       ├── index.tsx
│       ├── ChatPanel.tsx
│       ├── ChatMessage.tsx
│       └── types.ts
├── hooks/
│   ├── useAppDevFileManagement.ts  # 文件管理
│   ├── useAppDevServer.ts          # 服务器管理
│   └── useAppDevChat.ts            # 聊天对话
├── services/
│   └── appDevService.ts
└── types/
    └── sse.ts                   # SSE 消息类型
```

### SSE 通信规范

#### 消息类型
```typescript
// types/sse.ts
export enum SSEMessageType {
  // AI 思考过程
  AGENT_THOUGHT_CHUNK = 'agent_thought_chunk',
  
  // AI 回复内容
  AGENT_MESSAGE_CHUNK = 'agent_message_chunk',
  
  // 工具调用
  TOOL_CALL = 'tool_call',
  
  // 会话结束
  PROMPT_END = 'prompt_end',
  
  // 错误
  ERROR = 'error',
}

export interface SSEMessage {
  type: SSEMessageType;
  sessionId: string;
  data?: string;
  timestamp: number;
}
```

#### sseManager 使用
```typescript
// utils/sseManager.ts
import { SSEManager } from '@/utils/sseManager';

class MyComponent {
  private sseManager = new SSEManager();
  
  connect() {
    this.sseManager.connect('/api/app-dev/chat', {
      onMessage: (msg) => this.handleMessage(msg),
      onError: (err) => this.handleError(err),
      onOpen: () => console.log('Connected'),
    });
  }
  
  handleMessage(msg: SSEMessage) {
    switch (msg.type) {
      case SSEMessageType.AGENT_THOUGHT_CHUNK:
        this.updateThinking(msg.data);
        break;
      case SSEMessageType.AGENT_MESSAGE_CHUNK:
        this.appendMessage(msg.data);
        break;
      case SSEMessageType.TOOL_CALL:
        this.handleToolCall(msg.data);
        break;
    }
  }
}
```

### 文件管理 Hook

```typescript
// hooks/useAppDevFileManagement.ts
import { useState, useCallback } from 'react';

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
}

export function useAppDevFileManagement() {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  
  const refreshTree = useCallback(async () => {
    // 调用 API 获取文件树
  }, []);
  
  const openFile = useCallback(async (path: string) => {
    // 打开文件
  }, []);
  
  const saveFile = useCallback(async (path: string, content: string) => {
    // 保存文件
  }, []);
  
  return {
    files,
    currentFile,
    refreshTree,
    openFile,
    saveFile,
  };
}
```

---

## 2. Chat 聊天模块

### 消息类型
```typescript
// types/chat.ts
export interface ChatMessage {
  id: string;
  type: 'ai' | 'user' | 'button' | 'section' | 'thinking' | 'tool_call';
  content?: string;
  sessionId?: string;
  isStreaming?: boolean;
  timestamp: number;
  metadata?: {
    toolName?: string;
    toolParams?: Record<string, unknown>;
    thinking?: string;
  };
}
```

### 组件模板

```tsx
// components/ChatMessage/index.tsx
import { Avatar, Spin } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import styles from './ChatMessage.less';

interface Props {
  message: ChatMessage;
  onRetry?: () => void;
}

export const ChatMessage: React.FC<Props> = ({ message, onRetry }) => {
  const isAI = message.type === 'ai' || message.type === 'thinking';
  
  return (
    <div className={styles.message}>
      <Avatar icon={isAI ? <RobotOutlined /> : <UserOutlined />} />
      <div className={styles.content}>
        {message.type === 'thinking' ? (
          <Spin size="small" />
        ) : (
          message.content
        )}
      </div>
    </div>
  );
};
```

---

## 3. Workflow 工作流模块

### AntV X6 配置

```typescript
// types/workflow.ts
import { Graph } from '@antv/x6';

export interface WorkflowNode {
  id: string;
  type: 'start' | 'end' | 'action' | 'condition';
  x: number;
  y: number;
  label: string;
  config?: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}
```

### 画布组件

```tsx
// components/WorkflowCanvas/index.tsx
import { useEffect, useRef } from 'react';
import { Graph } from '@antv/x6';

interface Props {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  onNodeClick?: (nodeId: string) => void;
}

export const WorkflowCanvas: React.FC<Props> = ({ nodes, edges, onNodeClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<Graph | null>(null);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    graphRef.current = new Graph({
      container: containerRef.current,
      autoResize: true,
      panning: true,
      mousewheel: true,
    });
    
    return () => graphRef.current?.dispose();
  }, []);
  
  useEffect(() => {
    if (graphRef.current) {
      graphRef.current.fromJSON({ nodes, edges });
    }
  }, [nodes, edges]);
  
  return <div ref={containerRef} className={styles.canvas} />;
};
```

---

## 4. API 服务模板

```typescript
// services/request.ts
import { extend } from 'umi-request';

const request = extend({
  prefix: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

request.interceptors.response.use((response) => {
  return response;
});

export default request;

// services/appDev.ts
import request from './request';
import type { ApiResponse, PaginationParams } from './types';

export interface AppDev {
  id: string;
  name: string;
  status: 'running' | 'stopped';
  createdAt: string;
}

export async function getAppDevList(params: PaginationParams) {
  return request<ApiResponse<AppDev[]>>('/app-dev/list', { method: 'GET', params });
}

export async function createAppDev(data: Partial<AppDev>) {
  return request<ApiResponse<AppDev>>('/app-dev/create', { method: 'POST', data });
}
```

---

## 5. 状态管理

```typescript
// models/appDev.ts
import { Effect, Reducer } from 'umi';

export interface AppDevModelState {
  list: AppDev[];
  current?: AppDev;
  loading: boolean;
}

export interface AppDevModelType {
  namespace: 'appDev';
  state: AppDevModelState;
  effects: {
    fetchList: Effect;
    create: Effect;
  };
  reducers: {
    setList: Reducer<AppDevModelState>;
  };
}

const appDevModel: AppDevModelType = {
  namespace: 'appDev',
  state: { list: [], loading: false },
  
  effects: {
    *fetchList(_, { call, put }) {
      const res = yield call(getAppDevList, { page: 1, pageSize: 20 });
      yield put({ type: 'setList', payload: res.data });
    },
  },
  
  reducers: {
    setList(state, action) {
      return { ...state, list: action.payload };
    },
  },
};

export default appDevModel;
```

---

## 6. 常见问题

### SSE 连接断开
```typescript
// 添加心跳检测
class SSEManager {
  private heartbeatTimer?: NodeJS.Timer;
  
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000);
  }
  
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
  }
}
```

### AntV X6 性能
```typescript
// 使用虚拟化
new Graph({
  async: true,  // 异步渲染
  autoResize: true,
});

// 大量节点时禁用动画
new Graph({
  animated: false,
});
```
