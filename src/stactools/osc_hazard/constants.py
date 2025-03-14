ATTRS = {
    "days_tas_above": {
        "days_tas_above": {
            "long_name": "Days per year for which the average near-surface temperature 'tas' is above a threshold",  # noqa: E501
            "units": "Days per year",
        },
        "gcm": {
            "long_name": "Name of general circulation model",
        },
        "scenario": {
            "long_name": "Name of climate scenario",
        },
        "time": {
            "long_name": "Central predicted year",
        },
        "temperature": {
            "long_name": "Threshold temperature",
            "units": "Degrees Celsius",
        },
        "longitude": {"long_name": "Longitude", "units": "Degrees East"},
        "latitude": {"long_name": "Latitude", "units": "Degrees North"},
    },
    "degree_days": {
        "degree_days": {
            "long_name": "Time integral of absolute difference in temperature of the medium over a reference temperature",  # noqa: E501
            "units": "Days per year",
        },
        "gcm": {
            "long_name": "Name of general circulation model",
        },
        "scenario": {
            "long_name": "Name of climate scenario",
        },
        "time": {
            "long_name": "Central predicted year",
        },
        "temperature": {
            "long_name": "Threshold temperature",
            "units": "Degrees Celsius",
        },
    },
}

TITLES = {"days_tas_above": "Days TAS Above", "degree_days": "Degree Days"}


DESCRIPTIONS = {
    "days_tas_above": (
        "Days per year for which the average near-surface temperature 'tas' is above a threshold specified in °C."
    ),
    "degree_days": (
        "Degree days indicators are calculated by integrating over time the absolute difference in temperature "
        "of the medium over a reference temperature. The exact method of calculation may vary; "
        "here the daily maximum near-surface temperature 'tasmax' is used to calculate an annual indicator."
    ),
}

KEYWORDS = ["OS-Climate", "Climate Hazards"]

SUPPORTED_INDICATORS = list(ATTRS)

XARRAY_OPEN_KWARGS = dict(engine="zarr", consolidated=True)
