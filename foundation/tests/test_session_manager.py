from dataclasses import dataclass
from typing import Any, override
from unittest.mock import MagicMock
import pytest
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.ports.base_session import BaseSession
from foundation.persistence.ports.session_manager import SessionManager
from foundation.persistence.repositories.sql_alchemy_outbox_repository import (
    SqlAlchemyOutboxRepository,
)
from foundation.persistence.sessions.file_system_session import FileSystemSession
from foundation.persistence.sessions.sqlalchemy_session import SqlAlchemySession


class DummyIntegrationEvent(IntegrationEvent):
    pass


class MockSession(BaseSession):
    committed: bool = False
    rolled_back: bool = False
    closed: bool = False

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    @override
    def commit(self) -> None:
        self.committed = True

    @override
    def rollback(self) -> None:
        self.rolled_back = True

    @override
    def close(self) -> None:
        self.closed = True


@dataclass
class DummySessionManager(SessionManager[MockSession]):
    pass


def test_session_manager_lifecycle():
    mock_session = MockSession()
    manager = DummySessionManager(session_factory=lambda: mock_session)

    with manager:
        assert manager.session is mock_session
        manager.commit()
        assert mock_session.committed

    assert mock_session.closed


def test_session_manager_rollback_on_exception():
    mock_session = MockSession()
    manager = DummySessionManager(session_factory=lambda: mock_session)

    with pytest.raises(ValueError, match="Test Exception"):
        with manager:
            raise ValueError("Test Exception")

    assert mock_session.rolled_back
    assert mock_session.closed


def test_sqlalchemy_session_wrapper():
    mock_raw_session: Any = MagicMock()
    sqlalchemy_session = SqlAlchemySession(mock_raw_session)

    sqlalchemy_session.commit()
    mock_raw_session.commit.assert_called_once()

    sqlalchemy_session.rollback()
    mock_raw_session.rollback.assert_called_once()

    sqlalchemy_session.close()
    mock_raw_session.close.assert_called_once()

    sqlalchemy_session.add("test_model")
    mock_raw_session.add.assert_called_once_with("test_model")


def test_sqlalchemy_outbox_repository():
    mock_raw_session: Any = MagicMock()
    sqlalchemy_session = SqlAlchemySession(mock_raw_session)
    outbox_repo = SqlAlchemyOutboxRepository(sqlalchemy_session)

    event = DummyIntegrationEvent()
    outbox_repo.save(event)
    mock_raw_session.add.assert_called_once()


def test_file_system_session():
    fs_session = FileSystemSession()
    fs_session.commit()
    fs_session.rollback()
    fs_session.close()
