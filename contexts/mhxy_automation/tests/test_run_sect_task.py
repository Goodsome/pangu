"""RunSectTask execute_batch 日志隔离测试。"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from mhxy_automation.application.use_cases.run_sect_task import RunSectTask


def test_execute_batch_logs_to_different_files(tmp_path: Path) -> None:
    async def _test() -> None:
        mock_client_0 = MagicMock()
        mock_client_0.__aenter__ = AsyncMock(return_value=mock_client_0)
        mock_client_0.__aexit__ = AsyncMock(return_value=None)
        mock_client_0.begin_frame = AsyncMock()

        mock_client_1 = MagicMock()
        mock_client_1.__aenter__ = AsyncMock(return_value=mock_client_1)
        mock_client_1.__aexit__ = AsyncMock(return_value=None)
        mock_client_1.begin_frame = AsyncMock()

        def mock_factory(index: int) -> MagicMock:
            return mock_client_0 if index == 0 else mock_client_1

        use_case = RunSectTask()

        with patch(
            "mhxy_automation.application.use_cases.run_sect_task.create_mhxy_client_by_index",
            side_effect=mock_factory,
        ):
            await use_case.execute_batch(
                window_indices=[0, 1], one_tick=True, log_dir=tmp_path
            )

        log_0 = tmp_path / "client_0.log"
        log_1 = tmp_path / "client_1.log"

        assert log_0.exists()
        assert log_1.exists()

        content_0 = log_0.read_text(encoding="utf-8")
        content_1 = log_1.read_text(encoding="utf-8")

        assert "[Client-0]" in content_0
        assert "[Client-1]" not in content_0

        assert "[Client-1]" in content_1
        assert "[Client-0]" not in content_1

    asyncio.run(_test())


def test_execute_f12_key_exit() -> None:
    async def _test() -> None:
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.begin_frame = AsyncMock()

        use_case = RunSectTask()

        with (
            patch(
                "mhxy_automation.application.use_cases.run_sect_task.create_mhxy_client_by_index",
                return_value=mock_client,
            ),
            patch(
                "mhxy_automation.application.use_cases.run_sect_task.is_key_pressed",
                return_value=True,
            ),
        ):
            await use_case.execute(window_index=0, one_tick=False)

        assert use_case.stop_event.is_set()

    asyncio.run(_test())
