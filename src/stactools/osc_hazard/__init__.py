import stactools.core
from stactools.cli.registry import Registry
from stactools.osc_hazard.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.osc_hazard import commands

    registry.register_subcommand(commands.create_oschazard_command)
