from collections.abc import AsyncIterator, Iterator

from neo4j import AsyncDriver, AsyncGraphDatabase, Driver, GraphDatabase


def init_neo4j_driver(uri: str = "bolt://localhost:7687") -> Iterator[Driver]:
    """管理 Neo4j 驱动生命周期的生成器函数"""
    driver = GraphDatabase.driver(uri, auth=None)
    yield driver
    # 当容器关闭时，资源会被安全释放
    driver.close()

async def init_async_neo4j_driver(uri: str = "bolt://localhost:7687") -> AsyncIterator[AsyncDriver]:
    """管理异步 Neo4j 驱动生命周期的异步生成器"""
    driver = AsyncGraphDatabase.driver(uri, auth=None)
    
    # 验证连接是否成功（可选，但推荐，可以在启动时尽早发现配置错误）
    await driver.verify_connectivity()
    
    yield driver
    
    # 当容器关闭时，资源会被安全地异步释放
    await driver.close()