from dependency_injector import containers
from dependency_injector.providers import Configuration, Container
from spike.container import Container as SpikeContainer


class AppContainer(containers.DeclarativeContainer):
    config: Configuration = Configuration()

    spike_container: Container[SpikeContainer] = Container(SpikeContainer)


def create_container(init_resources: bool = True) -> AppContainer:
    """Bootstrap the DI container with configuration."""
    container = AppContainer()
    if init_resources:
        container.init_resources()
    return container


async def create_container_async(init_resources: bool = True) -> AppContainer:
    """Bootstrap the DI container with configuration."""
    container = AppContainer()
    if init_resources:
        _init = container.init_resources()
        if _init:
            await _init
    return container
