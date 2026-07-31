from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import inspect

from fastapi import FastAPI
import uvicorn

from d4_leaderboard.container import Container as D4LeaderboardContainer
from d4_leaderboard.interfaces.http import router as leaderboard_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # 1. 初始化限界上下文容器中的 Resource 资源（数据库连接池、Redis 等）
    leaderboard_container: D4LeaderboardContainer = app.state.leaderboard_container
    init_res = leaderboard_container.init_resources()
    if inspect.isawaitable(init_res):
        await init_res

    yield

    # 2. 应用关闭时优雅释放资源（自动触发 AsyncEngine.dispose() 等）
    shutdown_res = leaderboard_container.shutdown_resources()
    if inspect.isawaitable(shutdown_res):
        await shutdown_res


def create_app() -> FastAPI:
    app = FastAPI(
        title="D4 Backend Services",
        description="Unified backend server for D4 ecosystem apps and contexts",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 初始化并 Wire D4 Leaderboard 限界上下文容器
    leaderboard_container = D4LeaderboardContainer()
    leaderboard_container.wire(modules=["d4_leaderboard.interfaces.http"])
    app.state.leaderboard_container = leaderboard_container

    # 挂载限界上下文路由
    app.include_router(leaderboard_router)

    return app


app = create_app()


def main() -> None:
    uvicorn.run(
        "d4_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
