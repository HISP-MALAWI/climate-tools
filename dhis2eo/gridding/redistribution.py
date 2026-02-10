from io import StringIO
import pandas as pd
from plot import plotData
from rasterise import rasterize_population
from masking import mask
from gridding import linear_grid
from preparedata import prepare_data
import geopandas as gpd
import rioxarray as rxr
from bayersianGrid import bayesian_grid

data = prepare_data(base_url="https://dhis2.health.gov.mw",username="yambansokausiwa",password="Bscinf-07",dx='jPEcKbn7jmh',pe="202501",ou_level="4") #getting data valaue to interpolate
dataValues = pd.read_csv(StringIO(data))
print(dataValues)
lin = linear_grid(dataValues) # linear interpolation
grd = mask(lin,r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp") #  masking takes the dataset and the path to the map layer you want to mask with
pop = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\pop.gpkg")
pop = pop.to_crs(epsg=4326)

overlay = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp")
overlay = overlay.to_crs(epsg=4326)

rst = rasterize_population(pop,lin,pop_col="population") # rasterize the population dataset

rst = rst.reindex_like(lin,method=None)
spatial_mask = lin.isel(time=0).notnull()
rst_masked = rst.where(spatial_mask)

pop_total = rst_masked.sum(dim=("lat", "lon"))
weights = rst_masked / pop_total

pop_total = rst.sum(dim=("lat", "lon"))
weights = rst / pop_total

total_cases = lin.isel(time=0).sum(dim=("lat", "lon"))

cases = weights * total_cases

msk = mask(cases,r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp")
# print(msk)
# print(lin)
print(msk)
plotData(grd,overlay)
plotData(msk,overlay) # Plot data values