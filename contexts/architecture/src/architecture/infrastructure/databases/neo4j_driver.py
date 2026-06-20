from collections.abc import Iterator

from neo4j import Driver, GraphDatabase


def init_neo4j_driver(uri: str = "bolt://localhost:7687") -> Iterator[Driver]:
    """管理 Neo4j 驱动生命周期的生成器函数"""
    driver = GraphDatabase.driver(uri, auth=None)
    yield driver
    # 当容器关闭时，资源会被安全释放
    driver.close()
