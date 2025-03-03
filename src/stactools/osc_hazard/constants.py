ATTRS = {
    "days_tas_above": {
        "days_tas_above": {        
            "long_name": "Days per year for which the average near-surface temperature 'tas' is above a threshold",
            "units": "Days per year"
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
            "units": "Degrees Celsius"
        }
    },
    "degree_days": {
        "degree_days": {
            "long_name": "Time integral of absolute difference in temperature of the medium over a reference temperature",
            "units": "Days per year"
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
            "units": "Degrees Celsius"
        }
    }
}

SUPPORTED_INDICATORS = list(ATTRS)