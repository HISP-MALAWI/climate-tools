import os
from io import StringIO
from pathlib import Path
import pandas as pd
import xarray as xr
import geopandas as gpd
from dotenv import load_dotenv
from preparedata import prepare_data
from gridding import linear_grid
from masking import mask
from plot import plotData
from dhis2eo.data.worldpop import pop_total

load_dotenv(Path(__file__).parent / ".env")

# 1. DATA PREPARATION
# Fetch disease data from DHIS2
data_str = prepare_data(
    base_url="https://dhis2.health.gov.mw/",
    username="yambansokausiwa",
    password=os.environ["DHIS2_PASSWORD"],
    dx='jPEcKbn7jmh',
    pe="202501",
    ou_level="4"
)
dataValues = pd.read_csv(StringIO(data_str))

lin = linear_grid(dataValues)

country_code = 'MWI'
pop_ds = pop_total.get("2025", country_code)

pop_da = pop_ds['total_pop'].rename({'x': 'lon', 'y': 'lat'})

rst = pop_da.reindex_like(lin, method="nearest")

total_pop_sum = rst.sum(dim=("lat", "lon"))
weights = rst / total_pop_sum

total_cases_val = lin['cases'].isel(time=0).sum(dim=("lat", "lon"))

redistributed_da = weights * total_cases_val

cases_ds = redistributed_da.to_dataset(name="cases")

districts_path = r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp"  # Path to district shapefile
overlay = gpd.read_file(districts_path).to_crs(epsg=4326)
print(cases_ds)
grd_masked = mask(lin, districts_path)
msk_redistributed = mask(cases_ds, districts_path)

print("Masked Redistributed Data:")
print(msk_redistributed)

plotData(grd_masked, overlay)          # Original Linear Interpolation
plotData(msk_redistributed.squeeze(), overlay)    # Population-Weighted Redistribution