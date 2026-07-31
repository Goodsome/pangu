import pytest
from fastapi import FastAPI
from d4_backend.main import create_app


@pytest.fixture(autouse=True)
def setup_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "D4_LEADERBOARD_DB_URL", "postgresql+psycopg://user:pass@localhost:5432/db"
    )


def test_create_app() -> None:
    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "D4 Backend Services"
