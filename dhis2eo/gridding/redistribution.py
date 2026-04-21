import argparse
import os
from io import StringIO
from pathlib import Path
import pandas as pd
import xarray as xr
import geopandas as gpd
from dotenv import load_dotenv
from preparedata import prepare_data
from gridding import linear_grid
from plot import plotData
from dhis2eo.data.worldpop import pop_total

load_dotenv(Path(__file__).parent / ".env")


def redistribute_cases(data_values, pop_da, polygons):
    """Redistribute case counts onto a population-weighted grid, masked to polygons.

    Parameters
    ----------
    data_values : pd.DataFrame
        DHIS2-style case data to be gridded via linear interpolation.
    pop_da : xr.DataArray
        Population raster with ``lon``/``lat`` dims.
    polygons : geopandas.GeoDataFrame
        Polygons (EPSG:4326) used to clip the output grids.

    Returns
    -------
    tuple[xr.DataArray, xr.DataArray]
        ``(linear_masked, redistributed_masked)``.
    """
    lin = linear_grid(data_values)

    rst = pop_da.reindex_like(lin, method="nearest")
    weights = rst / rst.sum(dim=("lat", "lon"))

    total_cases_val = lin['cases'].isel(time=0).sum(dim=("lat", "lon"))
    cases_ds = (weights * total_cases_val).to_dataset(name="cases")

    def _clip(ds):
        da = ds["cases"].rio.write_crs("EPSG:4326")
        da = da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
        return da.rio.clip(polygons.geometry, polygons.crs, drop=True)

    return _clip(lin), _clip(cases_ds)


DEFAULT_DISTRICTS_PATH = r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--districts",
        default=DEFAULT_DISTRICTS_PATH,
        help="Path to districts shapefile (default: %(default)s)",
    )
    args = parser.parse_args()

    data_str = prepare_data(
        base_url="https://dhis2.health.gov.mw/",
        username="yambansokausiwa",
        password=os.environ["DHIS2_PASSWORD"],
        dx='jPEcKbn7jmh',
        pe="202501",
        ou_level="4"
    )
    data_values = pd.read_csv(StringIO(data_str))

    pop_ds = pop_total.get("2025", "MWI")
    pop_da = pop_ds['total_pop'].rename({'x': 'lon', 'y': 'lat'})

    overlay = gpd.read_file(args.districts).to_crs(epsg=4326)

    grd_masked, msk_redistributed = redistribute_cases(data_values, pop_da, overlay)

    plotData(grd_masked, overlay)
    plotData(msk_redistributed.squeeze(), overlay)