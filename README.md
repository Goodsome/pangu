# Pangu (盘古)

盘古是一个基于 **Python 3.14+** 和 **uv Workspace** 构建的领域驱动设计（DDD）风格模块化单体仓库（Monorepo），融合代码知识图谱与生成演进、通用计算机视觉引擎、系统输入控制以及数据榜单服务等多个限界上下文与应用服务。

## 🏗️ 目录架构

```text
pangu/
├── apps/                 # 应用程序入口层
│   ├── pangu_cli/        # 主命令行工具
│   ├── pangu_mcp/        # Model Context Protocol 服务
│   ├── d4_backend/       # 榜单后端 API
│   └── d4_robot/         # 自动化机器人程序
├── contexts/             # 领域限界上下文 (Bounded Contexts)
│   ├── architecture/     # 架构模式与模型控制
│   ├── code_dom/         # 代码 DOM 与语法树建模
│   ├── code_structure/   # 代码结构分析
│   ├── code_generation/  # 代码生成
│   ├── code_refactoring/ # 代码重构
│   ├── code_evolution/   # 代码演进
│   ├── d4_leaderboard/   # 榜单与数据分析
│   └── d4_automation/    # 自动化决策与控制
├── packages/             # 可复用独立功能包
│   ├── cv_engine/        # 计算机视觉图像处理引擎
│   ├── vision_stream/    # 视觉流视频捕获与分析
│   ├── sys_input/        # 系统级输入控制
│   └── d4_client/        # 客户端网络与协议封装
└── foundation/           # 底层通用基础设施
```

## 🧠 三阶段代码知识图谱

代码分析按粒度递进拆分为三个上下文，以控制不同分析层级的时间与内存成本：

| 阶段 | 上下文 | 图谱元素 | 能力 |
| --- | --- | --- | --- |
| 宏观架构级 | architecture | 模块/包节点，`DEPENDS_ON` / `IMPORTS` 边 | 调用链路梳理、循环依赖发现、解耦成本评估 |
| 符号级 | code_structure | 类/函数/变量符号节点，`DEFINES` / `INHERITS` / `REFERENCES` 边 | 跨模块移动符号、重构影响面计算、全局 Import 更新 |
| 微观 AST 级 | code_dom | 语句/表达式 AST 值对象（双向 AST ↔ 领域对象映射） | 单文件按需解析、代码生成与改写（Ruff 格式化闭环） |

## 🛠️ 技术栈

- **包管理与构建**：uv Workspace（Python ≥ 3.14）
- **数据校验**：Pydantic 2.x / pydantic-settings
- **持久化**：PostgreSQL（SQLAlchemy 2.0 async + psycopg3）、Neo4j、Redis、Alembic
- **质量工具链**：pytest、ruff、basedpyright

## 🚀 快速开始

```bash
uv sync         # 同步依赖并创建虚拟环境
uv run pytest   # 运行测试
uv run pangu --help
```
