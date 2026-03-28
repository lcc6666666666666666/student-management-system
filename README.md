# 教学管理系统 (课程设计)

这是一个面向数据库课程设计场景构建的全栈教学管理系统。项目采用现代化的前后端分离架构，完整覆盖了学生、教师、管理员三种角色的核心业务流程，并包含数据统计与可视化功能，可作为 Web 开发、数据库应用或软件工程课程设计的优秀范例。

## ✨ 项目特色

- **前后端分离架构**: 前端使用 Vue 3，后端使用 FastAPI，职责清晰，易于开发和维护。
- **三角色权限模型**: 内置学生、教师、管理员三种角色，通过 JWT 和路由守卫实现精细化的菜单和接口权限控制。
- **完整的业务闭环**: 覆盖了从管理员创建课程、教师分配课程、学生在线选课、教师录入成绩到学生查看成绩的完整流程。
- **数据驱动的仪表盘**: 每个角色登录后都有专属的数据仪表盘，直观展示核心业务指标，如选课人数、平均分、通过率等。
- **现代化的技术栈**:
  - **前端**: Vue 3 (Vite) + TypeScript + Element Plus + Pinia + Vue Router
  - **后端**: Python 3 + FastAPI + SQLAlchemy (ORM) + PyMySQL
  - **数据库**: MySQL 8.0
- **高质量代码实践**: 后端采用分层设计（接口、服务、数据模型），前端采用模块化和组件化开发，代码结构清晰，可读性强。

## 🏛️ 项目架构

项目由 `frontend` 和 `backend` 两个独立的子项目组成。

### 后端 (Backend)

基于 FastAPI 构建，采用分层架构，确保代码的高内聚和低耦合。

```
backend/
├── app/
│   ├── api/v1/         # API 接口层 (Endpoints)
│   ├── core/           # 核心组件 (数据库配置, 安全, 全局设置)
│   ├── models/         # SQLAlchemy ORM 模型
│   ├── schemas/        # Pydantic 数据校验模型
│   └── services/       # 业务逻辑服务层
├── run.py              # 项目启动脚本
└── requirements.txt    # Python 依赖
```

- **`app/api/v1/endpoints`**: 定义所有 HTTP 路由，负责接收请求、校验参数并调用服务层。
- **`app/services`**: 封装核心业务逻辑，如用户认证、课程管理、成绩录入等。
- **`app/core`**: 管理数据库连接、密码哈希、JWT 生成与验证等底层功能。
- **`app/schemas`**: 定义 API 的请求体和响应体结构，FastAPI 会基于此自动进行数据验证和生成 OpenAPI 文档。

### 前端 (Frontend)

基于 Vue 3 构建，采用组件化和模块化的开发模式。

```
frontend/
├── src/
│   ├── api/            # API 请求封装
│   ├── assets/         # 静态资源 (CSS, 图片)
│   ├── components/     # 可复用 UI 组件
│   ├── layout/         # 整体布局组件 (侧边栏, 头部)
│   ├── router/         # Vue Router 路由配置与导航守卫
│   ├── store/          # Pinia 全局状态管理
│   ├── utils/          # 工具函数
│   └── views/          # 页面级组件
├── package.json        # Node.js 依赖
└── vite.config.ts      # Vite 配置文件
```

- **`src/views`**: 存放页面级组件，每个文件代表一个独立的页面。
- **`src/router`**: 定义应用的页面路由、导航守卫（用于登录验证和权限检查）。
- **`src/store`**: 使用 Pinia 管理全局状态，如用户登录信息、Token 等。
- **`src/api`**: 统一管理所有对后端接口的请求，便于维护和复用。
- **`src/components`**: 存放被多个页面复用的 UI 组件，如统计卡片、图表等。

## 🚀 快速开始

### 1. 环境准备

- Node.js >= 18.0
- Python >= 3.10
- MySQL >= 8.0

### 2. 后端启动

```bash
# 1. 进入后端目录
cd backend

# 2. (推荐) 创建并激活 Python 虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库
#    - 复制 .env.example 为 .env
#    - 修改 .env 文件中的 DATABASE_URL，填入你的 MySQL 用户名、密码和数据库名
#    - 确保你的 MySQL 服务已启动，并已创建对应的数据库

# 5. 启动服务
python run.py
```

后端服务将运行在 `http://localhost:8000`，API 文档位于 `http://localhost:8000/docs`。

### 3. 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

前端开发服务器将运行在 `http://localhost:5173` (或终端提示的其他端口)。

现在，你可以打开浏览器访问前端地址，使用默认的演示账号（如 `student01`, `teacher01`, `admin01`，密码均为 `123456`）登录系统。