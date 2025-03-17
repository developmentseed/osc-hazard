import datetime
import re
import fnmatch
import shutil
import os.path
from os import PathLike

import numpy as np
import xarray as xr
import zarr
from hazard.sources.osc_zarr import OscZarr

from .constants import ATTRS

INDICATOR_NAME = "indicator"


def _parse_index_name(key: str, prefix: str = ".*"):
    match = re.match(
        rf"{prefix}_([0-9]+\.?[0-9]+)c_([a-zA-Z0-9-]+)_([a-zA-Z0-9]+)_(\d+)*.*", key
    )
    if match is None:
        raise ValueError(f"Unable to match string '{key}'")
    temperature, gcm, scenario, year = match.groups()
    index = dict(
        temperature=float(temperature),
        gcm=gcm,
        scenario=scenario,
        time=datetime.datetime(int(year), 1, 1),
    )
    return index


def _index_arrays(store: OscZarr):
    all_keys = list(store.keys())
    array_keys = fnmatch.filter(all_keys, f"*_????/{INDICATOR_NAME}/.zarray")
    if not array_keys:
        # try again assuming flat array structure
        array_keys = fnmatch.filter(all_keys, "*_????/.zarray")
    if not array_keys:
        raise RuntimeError(
            f"Store at {store.dir_path()} does not contain any matching keys. Found only {all_keys}."
        )
    keys = [key.removesuffix("/.zarray") for key in array_keys]
    return {key: _parse_index_name(key, prefix=".*") for key in keys}


def _indexes_to_coords(indexes: dict):
    coords = None
    for index in indexes:
        if coords is None:
            coords = {key: set() for key in index}

        for key, value in index.items():
            coords[key].add(value)

    for key in coords:
        coords[key] = sorted(coords[key])

    return coords


def _create_empty_array(coords: dict, sample_array: xr.DataArray, indicator_name: str):
    shape = [len(values) for values in coords.values()]

    attrs = sample_array.attrs.copy()
    attrs.update(ATTRS[indicator_name][indicator_name])
    da = xr.DataArray(
        np.zeros(shape, dtype=sample_array.dtype),
        coords=coords,
        attrs=attrs,
        name=indicator_name,
    )

    # set coordinate variable attributes
    for name in da.coords:
        if name in sample_array.coords:
            da[name].attrs = sample_array.coords[name].attrs.copy()
        if name in ATTRS[indicator_name]:
            da[name].attrs = ATTRS[indicator_name][name]

    return da


def build_yearly_zarr_cubes(
    store: OscZarr, indexes_grouped: dict, indicator_name: str, output_dir: PathLike
):
    target = OscZarr(store=store)

    def _read_source_array(target: OscZarr, key: str):
        da = target.read(key)
        return da.isel(index=0)

    output_paths = {}
    for year, indexes in indexes_grouped.items():
        # generate one file per year
        output_paths[year] = output_path = (
            output_dir / f"{indicator_name}_{year:04d}.zarr"
        )

        # since we are using append mode for writing zarr, we need to make sure
        # the store does not yet exist
        if output_path.is_dir():
            shutil.rmtree(output_path)

        # create Xarray coords
        coords = _indexes_to_coords(indexes.values())

        # augment coords with those present in sample array
        sample_key = next(iter(indexes))
        sample_array = _read_source_array(target, key=sample_key)
        for key in sample_array.dims:
            coords[key] = sample_array.coords[key].values

        # create empty array with attributes and all
        da = _create_empty_array(
            coords=coords, sample_array=sample_array, indicator_name=indicator_name
        )

        # fill array with data from group
        for key, index in indexes.items():
            source_data = _read_source_array(target, key=key)
            da.loc[index] = source_data

        # write to zarr, appending to yearly file
        ds = da.to_dataset()
        ds.to_zarr(output_path, mode="a", consolidated=True)

    return output_paths


def cubify(
    store_path: PathLike,
    indicator_name: str,
    output_dir: PathLike,
    split_years: bool = True,
):
    # open OS-Climate Zarr in the directory that contains the arrays
    store = zarr.DirectoryStore(store_path)

    # index the contents
    indexes = _index_arrays(store)

    # group by year
    if split_years:
        indexes_grouped = {}
        for name, index in indexes.items():
            year = index["time"].year
            if year not in indexes_grouped:
                indexes_grouped[year] = {}
            indexes_grouped[year][name] = index
    else:
        first_year = next(iter(indexes.values()))["time"].year
        indexes_grouped = {first_year: {}}
        for name, index in indexes.items():
            indexes_grouped[first_year][name] = index

    # copy source data into multidimensional zarr in yearly files
    output_paths = build_yearly_zarr_cubes(
        store=store,
        indexes_grouped=indexes_grouped,
        indicator_name=indicator_name,
        output_dir=output_dir,
    )

    return output_paths
