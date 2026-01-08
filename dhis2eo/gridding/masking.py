
from io import StringIO
import pandas as pd
import rioxarray
import geopandas as gpd

from preparedata import prepare_data
from gridding import linear_grid
from plot import plotData

data = prepare_data(base_url="SomeURL",username="someUsername",password="pwd",dx='jPEcKbn7jmh',pe="202501",ou_level="4")
dataValues = pd.read_csv(StringIO(data))
lin = linear_grid(dataValues)

def mask(lin):

    lin = lin["cases"]  # extract DataArray from Dataset

    lin = lin.rio.write_crs("EPSG:4326")  # assign CRS
    lin = lin.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    lin.rio.write_crs("EPSG:4326", inplace=True)

    overlay = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp")
    overlay = overlay.to_crs(epsg=4326)

    clip = lin.rio.clip(
        overlay.geometry,
        overlay.crs,
        drop=True
    )
    return clip


plotData(clip,overlay)




