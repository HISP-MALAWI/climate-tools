import numpy as np
import pandas as pd
from io import StringIO
from scipy.interpolate import griddata
import xarray as xr

from preparedata import prepare_data

#You can pass multiple periods separated by a ;
# dataValues = pd.read_csv(StringIO(data))
#This function takes a pandas Dataframe type parameter
def linear_grid(dataValues):
    reso = 0.1
    buff = 0.1

    lon_min,lon_max = dataValues.lon.min(),dataValues.lon.max()
    lat_min,lat_max = dataValues.lat.min(),dataValues.lat.max()

    lon_grid = np.arange(lon_min - buff, lon_max + buff, reso)
    lat_grid = np.arange(lat_min - buff, lat_max + buff, reso)

    lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

    dataValues["time"] = pd.PeriodIndex.from_fields(year=dataValues.year,month=dataValues.month,freq="M")
    times = np.sort(dataValues["time"].unique())

    data_3d = np.full(
        (len(times), len(lat_grid), len(lon_grid)),
        np.nan
    )

    for t, time_val in enumerate(times):

        df_t = dataValues[dataValues["time"] == time_val]

        lats = df_t["lat"].values
        lons = df_t["lon"].values
        values = df_t["cases"].values

        mask = ~np.isnan(lats) & ~np.isnan(lons) & ~np.isnan(values)
        lats, lons, values = lats[mask], lons[mask], values[mask]

        if len(values) < 3:
            continue  # not enough points to interpolate

        grid_linear = griddata(
        (lons, lats),
        values,
        (lon_mesh, lat_mesh),
        method="linear"
        )

        grid_nearest = griddata(
            (lons, lats),
            values,
            (lon_mesh, lat_mesh),
            method="nearest"
        )

        grid_linear[np.isnan(grid_linear)] = grid_nearest[np.isnan(grid_linear)]

        data_3d[t, :, :] = grid_linear

    ds = xr.Dataset(
        data_vars={
            "cases": (("time", "lat", "lon"), data_3d)
        },
        coords={
            "time": times,
            "lat": lat_grid,
            "lon": lon_grid
        }
    )
    
    ds["cases"].attrs = {
    "long_name": "Monthly reported health facility cases",
    "units": "count",
    "cell_methods": "time: sum",
    "grid_mapping": "crs"
    }

    ds["lat"].attrs = {
    "standard_name": "latitude",
    "units": "degrees_north",
    "axis": "Y"
    }

    ds["lon"].attrs = {
        "standard_name": "longitude",
        "units": "degrees_east",
        "axis": "X"
    }

    ds["time"].attrs = {
        "standard_name": "time"
    }

    ds["crs"] = xr.DataArray(
    0,
    attrs={
        "grid_mapping_name": "latitude_longitude",
        "epsg_code": "EPSG:4326",
        "semi_major_axis": 6378137.0,
        "inverse_flattening": 298.257223563
    }
    )

    return ds






