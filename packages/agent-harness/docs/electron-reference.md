# Electron + Ant Design 项目配置参考

> 可直接复制到项目使用的配置

---

## 目录结构

```
electron-app/
├── src/
│   ├── main/                 # Electron 主进程
│   │   ├── index.ts         # 入口
│   │   ├── ipc/             # IPC 处理器
│   │   │   ├── handlers.ts   # IPC 处理函数
│   │   │   └── channels.ts  # 通道定义
│   │   └── preload/
│   │       └── index.ts     # 预加载脚本
│   ├── renderer/            # 渲染进程（React）
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/     # 组件
│   │   │   └── UserTable.tsx
│   │   ├── pages/          # 页面
│   │   │   └── UserManagement.tsx
│   │   ├── hooks/          # Hooks
│   │   ├── store/          # 状态管理
│   │   └── styles/
│   └── shared/             # 共享类型
│       └── types.ts
├── electron-builder.json
├── vite.config.ts
└── tsconfig.json
```

---

## IPC 通信模板

### src/shared/types.ts

```typescript
// IPC 通道定义
export const IPC_CHANNELS = {
  USER_GET_LIST: 'user:getList',
  USER_CREATE: 'user:create',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
} as const;

// 用户类型
export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

// API 响应
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// IPC 请求类型
export interface UserListRequest {
  page: number;
  pageSize: number;
}
```

### src/main/ipc/channels.ts

```typescript
import { IPC_CHANNELS, User, UserListRequest, ApiResponse } from '../../shared/types';

export function registerIpcHandlers() {
  // 获取用户列表
  ipcMain.handle(IPC_CHANNELS.USER_GET_LIST, async (_event, req: UserListRequest): Promise<ApiResponse<User[]>> => {
    try {
      const users = await userService.getList(req.page, req.pageSize);
      return { success: true, data: users };
    } catch (error) {
      return { success: false, error: error.message };
    }
  });
}
```

### src/main/preload/index.ts

```typescript
import { contextBridge, ipcRenderer } from 'electron';
import { IPC_CHANNELS, User, UserListRequest, ApiResponse } from '../../shared/types';

// 暴露给渲染进程的 API
contextBridge.exposeInMainWorld('electronAPI', {
  // 用户相关
  user: {
    getList: (req: UserListRequest) => ipcRenderer.invoke(IPC_CHANNELS.USER_GET_LIST, req),
    create: (user: Omit<User, 'id' | 'createdAt'>) => 
      ipcRenderer.invoke(IPC_CHANNELS.USER_CREATE, user),
    update: (id: string, user: Partial<User>) => 
      ipcRenderer.invoke(IPC_CHANNELS.USER_UPDATE, { id, user }),
    delete: (id: string) => ipcRenderer.invoke(IPC_CHANNELS.USER_DELETE, id),
  },
});
```

### src/renderer/hooks/useElectron.ts

```typescript
// 渲染进程中使用 electronAPI
const useUserList = (page: number, pageSize: number) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    window.electronAPI.user.getList({ page, pageSize })
      .then((res) => {
        if (res.success && res.data) {
          setUsers(res.data);
        }
      })
      .finally(() => setLoading(false));
  }, [page, pageSize]);

  return { users, loading };
};
```

---

## Ant Design 组件模板

### UserTable.tsx

```typescript
import { Table, Button, Space, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { User } from '../../shared/types';

interface Props {
  users: User[];
  loading: boolean;
  onEdit: (user: User) => void;
  onDelete: (id: string) => void;
}

const UserTable: React.FC<Props> = ({ users, loading, onEdit, onDelete }) => {
  const columns: ColumnsType<User> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => onEdit(record)}>
            Edit
          </Button>
          <Button type="link" danger onClick={() => onDelete(record.id)}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return <Table columns={columns} dataSource={users} loading={loading} rowKey="id" />;
};
```

### UserModal.tsx

```typescript
import { Modal, Form, Input, message } from 'antd';

interface Props {
  open: boolean;
  user?: User | null;
  onSubmit: (values: any) => void;
  onCancel: () => void;
}

const UserModal: React.FC<Props> = ({ open, user, onSubmit, onCancel }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue(user);
    } else {
      form.resetFields();
    }
  }, [user, form]);

  const handleOk = () => {
    form.validateFields().then((values) => {
      onSubmit(values);
      form.resetFields();
    });
  };

  return (
    <Modal title={user ? 'Edit User' : 'Create User'} open={open} onOk={handleOk} onCancel={onCancel}>
      <Form form={form} layout="vertical">
        <Form.Item name="name" label="Name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};
```

---

## Electron 特定检查清单

### 功能开发

- [ ] 主进程入口正确配置
- [ ] IPC 通道已注册
- [ ] preload 脚本已配置 contextBridge
- [ ] 渲染进程能通过 window.electronAPI 调用
- [ ] 遵循 Ant Design 规范
- [ ] 打包后能正常运行

### Bug 修复

- [ ] 确认是主进程还是渲染进程问题
- [ ] 查看对应日志
- [ ] 确认 IPC 通信正常
- [ ] 确认打包配置正确

### 日志查看

```bash
# 主进程日志
tail -f ~/Library/Logs/electron-app.log

# 开发模式日志
npm run dev
# 查看终端输出
```
