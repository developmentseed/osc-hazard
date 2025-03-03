import logging
from pathlib import Path

import click
from click import Command, Group

from stactools.osc_hazard.constants import SUPPORTED_INDICATORS
from stactools.osc_hazard import cubify, stac

logger = logging.getLogger(__name__)


def create_oschazard_command(cli: Group) -> Command:
    """Creates the stactools-osc-hazard command line utility."""

    @cli.group(
        "oschazard",
        short_help=("Commands for working with stactools-osc-hazard"),
    )
    def oschazard() -> None:
        pass

    @oschazard.command(
        "cubify-zarr",
        short_help="Turn OS-Climate Hazard Zarr into data cube Zarr",
    )  
    @click.argument(
        "store_path", type=click.Path(exists=True, file_okay=False, dir_okay=True)
    )
    @click.argument(
        "output_dir",
        type=click.Path(file_okay=False, dir_okay=True),
    )
    @click.option(
        "--indicator-name", "-i",
        type=click.Choice(SUPPORTED_INDICATORS), required=True,
        help="Name of the indicator to convert"
    )
    def cubify_command(store_path, output_dir, indicator_name):
        generated_files = cubify(
            store_path=Path(store_path),
            output_dir=Path(output_dir),
            indicator_name=indicator_name,
        )
        file_list = "\n".join(map(str, generated_files.values()))
        click.echo(f"Generated the following data cube files:\n{file_list}")

    @oschazard.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    def create_collection_command(destination: str) -> None:
        """Creates a STAC Collection

        Args:
            destination: An HREF for the Collection JSON
        """
        collection = stac.create_collection()
        collection.set_self_href(destination)
        collection.save_object()

    @oschazard.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str) -> None:
        """Creates a STAC Item

        Args:
            source: HREF of the Asset associated with the Item
            destination: An HREF for the STAC Item
        """
        item = stac.create_item(source)
        item.save_object(dest_href=destination)

    return oschazard
