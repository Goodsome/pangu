import logging
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from codegen.shared.infrastructure.orm_models.base import BaseORM


@dataclass
class Database:
    """Database connection handling using SQLAlchemy."""

    connection_string: str
    _engine: Engine = field(init=False)
    _session_factory: sessionmaker[Session] = field(init=False)

    def __post_init__(self) -> None:
        self._engine = create_engine(self.connection_string, pool_pre_ping=True)
        self._session_factory = sessionmaker(
            bind=self._engine, expire_on_commit=False, autoflush=False
        )

    def get_session(self) -> Session:
        """Create a new database session."""
        return self._session_factory()

    def close(self) -> None:
        """Close the database connection pool."""
        self._engine.dispose()

    def init_db(self) -> None:
        """Create database tables if they don't exist."""
        try:
            BaseORM.metadata.create_all(self._engine)
            logging.info("Database tables created successfully.")
        except Exception as e:
            logging.error(f"Failed to create database tables: {e}")
            raise e

    @property
    def session_factory(self) -> sessionmaker[Session]:
        return self._session_factory

    @property
    def engine(self) -> Engine:
        """Get the underlying SQLAlchemy engine."""
        return self._engine


def init_database(connection_string: str) -> Iterator[Database]:
    """数据库资源的生命周期管理"""
    db = Database(connection_string)
    try:
        with db.engine.connect() as _:
            pass
        db.init_db()
        logging.info("Database initialized and connected successfully.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise e
    yield db
    logging.info("Closing database connection pool...")
    db.close()
