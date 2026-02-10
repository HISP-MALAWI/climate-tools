from io import StringIO

import pandas as pd
from masking import mask
from dhis2eo.data.worldpop import pop_total
from prepareDatawithPop import prepare_data_with_pop
from preparedata import prepare_data
from bayersianGrid import bayesian_grid
import geopandas as gpd
from plot import plotData


pe="202501"
data = prepare_data(base_url="https://dhis2.health.gov.mw",username="yambansokausiwa",password="Bscinf-07",dx='jPEcKbn7jmh',pe=pe,ou_level="4") #getting data valaue to interpolate
dataValues = pd.read_csv(StringIO(data))
print(dataValues)
country_code = 'MWI'

file = pop_total.get("2025",country_code)

dataValues_ready = prepare_data_with_pop(dataValues, file)

grd = bayesian_grid(dataValues_ready)

msk = mask(grd,r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp")
overlay = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp")
overlay = overlay.to_crs(epsg=4326)
data_to_plot = msk.isel(time=0)
plotData(data_to_plot,overlay)


