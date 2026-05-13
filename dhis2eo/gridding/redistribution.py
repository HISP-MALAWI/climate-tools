import os
from io import StringIO
<<<<<<< HEAD
import os
=======
from pathlib import Path
>>>>>>> b522fcf67ac369dce5c40b15ae6e4c974515a29f
import pandas as pd
import xarray as xr
import geopandas as gpd
from dotenv import load_dotenv
from preparedata import prepare_data
from gridding import linear_grid
from masking import mask
from plot import plotData
from dhis2eo.data.worldpop import pop_total
from prepareDatawithPop import prepare_data_with_pop
from bayersianGrid import bayesian_grid

<<<<<<< HEAD
# Load environment variables from .env file
load_dotenv()

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get configuration from environment variables
DHIS2_BASE_URL = os.getenv('DHIS2_BASE_URL')
DHIS2_USERNAME = os.getenv('DHIS2_USERNAME')
DHIS2_PASSWORD = os.getenv('DHIS2_PASSWORD')
DHIS2_DX = os.getenv('DHIS2_DX')
DHIS2_PERIOD = os.getenv('DHIS2_PERIOD')
DHIS2_OU_LEVEL = os.getenv('DHIS2_OU_LEVEL')
WORLDPOP_YEAR = os.getenv('WORLDPOP_YEAR')
WORLDPOP_COUNTRY_CODE = os.getenv('WORLDPOP_COUNTRY_CODE')
SHAPEFILE_PATH = os.path.join(PROJECT_ROOT, os.getenv('SHAPEFILE_PATH', 'docs/data/Districts.shp'))
# 1. DATA PREPARATION
# Fetch disease data from DHIS2
data_str = prepare_data(
    base_url=DHIS2_BASE_URL,
    username=DHIS2_USERNAME,
    password=DHIS2_PASSWORD,
    dx=DHIS2_DX,
    pe=DHIS2_PERIOD,
    ou_level=DHIS2_OU_LEVEL
=======
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
>>>>>>> b522fcf67ac369dce5c40b15ae6e4c974515a29f
)
dataValues = pd.read_csv(StringIO(data_str))

# Get population data
pop_ds = pop_total.get(WORLDPOP_YEAR, WORLDPOP_COUNTRY_CODE)

# Prepare data with population
dataValues = prepare_data_with_pop(dataValues, pop_ds)

# Run Bayesian gridding
lin = bayesian_grid(dataValues)

pop_da = pop_ds['total_pop'].rename({'x': 'lon', 'y': 'lat'})

rst = pop_da.reindex_like(lin, method="nearest")

total_pop_sum = rst.sum(dim=("lat", "lon"))
weights = rst / total_pop_sum

total_cases_val = lin['cases'].isel(time=0).sum(dim=("lat", "lon"))

redistributed_da = weights * total_cases_val

cases_ds = redistributed_da.to_dataset(name="cases")

# Load district shapefile
overlay = gpd.read_file(SHAPEFILE_PATH).to_crs(epsg=4326)
print(cases_ds)
grd_masked = mask(lin, SHAPEFILE_PATH)
msk_redistributed = mask(cases_ds, SHAPEFILE_PATH)

print("Masked Redistributed Data:")
print(msk_redistributed)

plotData(grd_masked, overlay)          # Original Linear Interpolation
plotData(msk_redistributed.squeeze(), overlay)    # Population-Weighted Redistribution