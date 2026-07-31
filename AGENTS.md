# Pangu (盘古) 项目 Agent 指导文档

## 📌 项目概述

**Pangu (盘古)** 是一个基于 **Python 3.14+** 和 **uv Workspace** 构建的领域驱动设计 (DDD) 风格的模块化单体仓库 (Monorepo)。项目融合了代码语法树分析与生成演进、计算机视觉 (CV) 引擎、系统输入控制以及自动化机器人等多个限界上下文与应用服务。

---

## 🏗️ 目录架构与模块划分

```text
pangu/
├── apps/                 # 应用程序入口层
│   ├── pangu_cli/        # 盘古主命令行工具 (pangu)
│   ├── pangu_mcp/        # Model Context Protocol 服务 (pangu_mcp)
│   └── d4_robot/         # 自动化机器人程序 (d4-bot)
├── contexts/             # 领域限界上下文 (Bounded Contexts)
│   ├── architecture/     # 架构模式与模型控制
│   ├── code_dom/         # 代码 DOM 与语法树建模
│   ├── code_structure/   # 代码结构分析
│   ├── code_generation/  # 代码生成上下文
│   ├── code_refactoring/ # 代码重构上下文
│   ├── code_evolution/   # 代码演进上下文
│   ├── d4_leaderboard/   # 榜单与数据分析上下文
│   └── d4_automation/    # 自动化决策与控制上下文
├── packages/             # 可复用独立功能包
│   ├── cv_engine/        # 计算机视觉图像处理引擎
│   ├── vision_stream/    # 视觉流视频捕获与分析
│   ├── sys_input/        # 系统级输入控制 (键盘/鼠标/硬件模拟)
│   └── d4_client/        # 客户端网络与协议封装
├── foundation/           # 底层通用基础设施 (通用工具库、基类)
├── scripts/              # 辅助运维与开发脚本
└── pyproject.toml        # uv Workspace 项目全局依赖配置
```

---

## 🛠️ 技术栈与基础设施

* **包管理器与构建**: `uv` Workspace
* **核心语言**: Python `>= 3.14`
* **数据校验与配置**: Pydantic `2.x` 风格 (`pydantic`, `pydantic-settings`)
* **持久化与数据库**:
  * **主数据库**: PostgreSQL (使用 `sqlalchemy[asyncio]` 2.0 风格 + `psycopg3`)
  * **图数据库**: Neo4j (`neo4j >= 6.2.0`)
  * **缓存与队列**: Redis (`redis[hiredis]`)
  * **数据库迁移**: Alembic (`alembic`)
* **测试与代码质量**:
  * 测试工具: `pytest` (`uv run pytest`)
  * 代码分析与格式化: `ruff`, `basedpyright`

---

## ⚖️ 编程规范与 Agent 工作流要求

1. **命令行执行规范**:
   * 必须统一使用 `uv` 运行 Python 工具与测试命令：
     * 单元测试：`uv run pytest`
     * 执行 Python 脚本：`uv run python <script.py>`
2. **代码风格要求**:
   * **Pydantic**: 严格遵循 Pydantic 2.0 风格语法（`BaseModel`, `Field`, `model_validator` 等）。
   * **SQLAlchemy**: 严格遵循 SQLAlchemy 2.0 声明式与异步风格，充分利用 PostgreSQL 特性。
3. **质量闭环与代码校验**:
   * 每次更新 Python 代码后，必须加载并触发 `lint-fix` 技能对修改的文件执行代码检查、类型诊断与格式化抛光。
