# Pangu (盘古) 项目 Agent 指导文档

## 📌 项目概述

**Pangu (盘古)** 是一个基于 **Python 3.14+** 和 **uv Workspace** 构建的领域驱动设计 (DDD) 风格的模块化单体仓库 (Monorepo)。项目融合了代码语法树分析与生成演进、计算机视觉 (CV) 引擎、系统输入控制以及自动化机器人等多个限界上下文与应用服务。

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
