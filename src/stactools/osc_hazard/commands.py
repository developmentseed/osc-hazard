import logging
from pathlib import Path
from os import PathLike

import click
from click import Command, Group
import xarray as xr

from stactools.osc_hazard.constants import SUPPORTED_INDICATORS, XARRAY_OPEN_KWARGS
from stactools.osc_hazard import cubify, stac

logger = logging.getLogger(__name__)


def cubify_invocation(
    store_path: PathLike,
    output_dir: PathLike,
    indicator_name: str,
    split_years: bool = True,
):
    generated_files = cubify(
        store_path=Path(store_path),
        output_dir=Path(output_dir),
        indicator_name=indicator_name,
        split_years=split_years,
    )
    file_list = "\n".join(map(str, generated_files.values()))
    click.echo(f"Generated the following data cube files:\n{file_list}")


def collection_invocation(sources: str, destination: PathLike):
    with xr.open_mfdataset(sources, **XARRAY_OPEN_KWARGS) as ds:
        collection = stac.create_collection(ds)
    collection.save_object(dest_href=destination)


def item_invocation(source: str, destination: PathLike):
    with xr.open_dataset(source, **XARRAY_OPEN_KWARGS) as ds:
        item = stac.create_item(ds, href=source)
    item.save_object(dest_href=destination)


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
        "--indicator-name",
        "-i",
        type=click.Choice(SUPPORTED_INDICATORS),
        required=True,
        help="Name of the indicator to convert",
    )
    @click.option(
        "--split-years/--no-split-years",
        default=True,
        show_default=True,
        help="Split output zarr cubes by year",
    )
    def cubify_command(
        store_path: PathLike,
        output_dir: PathLike,
        indicator_name: str,
        split_years: bool,
    ):
        cubify_invocation(
            store_path,
            output_dir,
            indicator_name=indicator_name,
            split_years=split_years,
        )

    @oschazard.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("sources", nargs=-1)
    @click.argument("destination")
    def create_collection_command(sources: str, destination: str) -> None:
        """Creates a STAC Collection

        Args:
            sources: A list or pattern of HREF for the Xarray-readable input data cube
            destination: An HREF for the Collection JSON
        """
        collection_invocation(sources, destination)

    @oschazard.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str) -> None:
        """Creates a STAC Item

        Args:
            source: HREF of the Asset associated with the Item
            destination: An HREF for the STAC Item
        """
        item_invocation(source, destination)

    return oschazard
