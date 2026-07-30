import asyncio
from typing import Annotated

from d4_automation.application.use_cases.run_blue_gate import RunBlueGate
from typer import Option


async def _async_main(window_index: int):
    use_case = RunBlueGate()
    cancel_event = asyncio.Event()

    try:
        await use_case.execute(window_index, cancel_event)
    except KeyboardInterrupt:
        cancel_event.set()


def run_blue_gate(window_index: Annotated[int, Option("--idx")] = 0):
    asyncio.run(_async_main(window_index))
