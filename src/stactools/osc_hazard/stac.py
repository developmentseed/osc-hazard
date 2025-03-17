
import shapely
import xarray as xr
import xstac
from pystac import (
    Asset,
    Collection,
    Extent,
    Item,
    Link,
    MediaType,
    Provider,
    ProviderRole,
    RelType,
    SpatialExtent,
    TemporalExtent,
)

try:
    from pystac import Render, RenderExtension
    render_available = True
except ImportError:
    render_available = False


from stactools.osc_hazard.constants import (
    DESCRIPTIONS,
    KEYWORDS,
    TITLES,
    XARRAY_OPEN_KWARGS,
)


def _get_bbox(da: list[float]):
    return list(
        map(
            float,
            [
                da["longitude"].min(),
                da["latitude"].min(),
                da["longitude"].max(),
                da["latitude"].max(),
            ],
        )
    )


def create_collection(ds: xr.Dataset) -> Collection:
    """Creates a STAC Collection.

    This function should create a collection for this dataset. See `the STAC
    specification
    <https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md>`_
    for information about collection fields, and
    `Collection<https://pystac.readthedocs.io/en/latest/api.html#collection>`_
    for information about the PySTAC class.

    Returns:
        Collection: STAC Collection object
    """
    if len(ds.data_vars) != 1:
        raise ValueError(
            f"Only datasets with a single data variable are supported. Found {list(ds.data_vars)}."
        )
    da = next(iter(ds.data_vars.values()))
    indicator_name = da.name

    start_date, end_date = ds.indexes["time"][[0, -1]].to_pydatetime()

    extent = Extent(
        SpatialExtent([_get_bbox(ds)]),
        TemporalExtent(
            [
                [
                    start_date,
                    end_date,
                ]
            ]
        ),
    )

    collection = Collection(
        id=indicator_name,
        title=TITLES[indicator_name],
        description=DESCRIPTIONS[indicator_name],
        keywords=KEYWORDS,
        extent=extent,
        license="Apache-2.0",
        providers=[
            Provider(
                name="UK EO Data Hub",
                url="https://eodatahub.org.uk/",
                roles=[
                    ProviderRole.HOST,
                    ProviderRole.PRODUCER,
                    ProviderRole.LICENSOR,
                ],
            ),
            Provider(
                name="OS Climate",
                url="http://os-climate.org/",
                roles=[
                    ProviderRole.PRODUCER,
                ],
            ),
        ],
    )

    collection.add_link(
        Link(
            rel=RelType.LICENSE,
            target="http://www.apache.org/licenses/LICENSE-2.0",
            media_type=MediaType.HTML,
            title="Apache-2.0 license",
        ),
    )

    # add render extension - if pystac has it
    if render_available:
        collection.ext.add("render")
        renders = {
            indicator_name: Render.create(
                assets=[indicator_name],
                rescale=[[0, 100]],
                nodata=0,
                colormap_name="coolwarm",
            )
        }
        RenderExtension.ext(collection).apply(renders)

    # add data cube extension
    collection = xstac.xarray_to_stac(
        ds,
        collection,
        reference_system="epsg:4326",
        temporal_dimension="time",
        x_dimension="longitude",
        y_dimension="latitude",
    )

    return collection


def create_item(ds: xr.Dataset, href: str) -> Item:
    """Creates a STAC item from a raster asset.

    This example function uses :py:func:`stactools.core.utils.create_item` to
    generate an example item.  Datasets should customize the item with
    dataset-specific information, e.g.  extracted from metadata files.

    See `the STAC specification
    <https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md>`_
    for information about an item's fields, and
    `Item<https://pystac.readthedocs.io/en/latest/api/pystac.html#pystac.Item>`_ for
    information on the PySTAC class.

    This function should be updated to take all hrefs needed to build the item.
    It is an anti-pattern to assume that related files (e.g. metadata) are in
    the same directory as the primary file.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item

    Returns:
        Item: STAC Item object
    """
    if len(ds.data_vars) != 1:
        raise ValueError(
            f"Only datasets with a single data variable are supported. Found {list(ds.data_vars)}."
        )
    da = next(iter(ds.data_vars.values()))

    # generate item ID
    start_date = ds.indexes["time"][0].to_pydatetime()
    item_id = f"{da.name}_{start_date.year}"

    bbox = _get_bbox(ds)

    # create item
    item = Item(
        id=item_id,
        bbox=bbox,
        geometry=shapely.geometry.mapping(shapely.geometry.box(*bbox)),
        datetime=start_date,
        properties={},
    )

    # add asset
    item.assets[da.name] = Asset(
        href=href,
        title=f"{da.name} Zarr",
        description=da.attrs["long_name"],
        media_type="application/vnd+zarr",
        roles=["data", "zarr"],
        extra_fields={"xarray:open_kwargs": XARRAY_OPEN_KWARGS},
    )

    # add data cube extension
    item = xstac.xarray_to_stac(
        ds,
        item,
        reference_system="epsg:4326",
        temporal_dimension="time",
        x_dimension="longitude",
        y_dimension="latitude",
    )

    # additional dimensions not implemented in xstac
    for name in ["temperature", "gcm", "scenario"]:
        item.properties["cube:dimensions"][name] = {
            "type": "other",
            "description": ds[name].attrs["long_name"],
            "values": list(map(str, ds[name].values)),
        }

    return item
