from io import StringIO
import pandas as pd
from plot import plotData
from rasterise import rasterize_population
from masking import mask
from gridding import linear_grid
from preparedata import prepare_data
import geopandas as gpd
import rioxarray as rxr

data = prepare_data(base_url="someURL",username="url",password="password",dx='jPEcKbn7jmh',pe="202501",ou_level="4")
dataValues = pd.read_csv(StringIO(data))
lin = linear_grid(dataValues)
grd = mask(lin)

pop = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\pop.gpkg")
pop = pop.to_crs(epsg=4326)

rst = rasterize_population(pop,lin,pop_col="population")

rst = rst.reindex_like(lin,method=None)
spatial_mask = lin.isel(time=0).notnull()
rst_masked = rst.where(spatial_mask)from io import StringIO
import pandas as pd
from plot import plotData
from rasterise import rasterize_population
from masking import mask
from gridding import linear_grid
from preparedata import prepare_data
import geopandas as gpd
import rioxarray as rxr

data = prepare_data(base_url="someURL",username="url",password="password",dx='jPEcKbn7jmh',pe="202501",ou_level="4")
dataValues = pd.read_csv(StringIO(data))
lin = linear_grid(dataValues)
grd = mask(lin)

pop = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\pop.gpkg")
pop = pop.to_crs(epsg=4326)

rst = rasterize_population(pop,lin,pop_col="population")

rst = rst.reindex_like(lin,method=None)
spatial_mask = lin.isel(time=0).notnull()
rst_masked = rst.where(spatial_mask)

pop_total = rst_masked.sum(dim=("lat", "lon"))
weights = rst_masked / pop_total

pop_total = rst.sum(dim=("lat", "lon"))
weights = rst / pop_total

total_cases = lin.isel(time=0).sum(dim=("lat", "lon"))

cases = weights * total_cases

msk = mask(cases)
# print(msk)
# print(lin)
print(msk)

plotData(msk)

pop_total = rst_masked.sum(dim=("lat", "lon"))
weights = rst_masked / pop_total

pop_total = rst.sum(dim=("lat", "lon"))
weights = rst / pop_total

total_cases = lin.isel(time=0).sum(dim=("lat", "lon"))

cases = weights * total_cases

msk = mask(cases)
# print(msk)
# print(lin)
print(msk)

plotData(msk)