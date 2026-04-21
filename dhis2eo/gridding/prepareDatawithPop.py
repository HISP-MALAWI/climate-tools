import xarray as xr
import numpy as np
from scipy.interpolate import NearestNDInterpolator

def prepare_data_with_pop(disease_df, pop_ds):
    sampled_pop = []
    
    pop_raster = pop_ds.total_pop.isel(band=0)

    # Create interpolator for faster nearest neighbor lookup
    xx, yy = np.meshgrid(pop_raster.x.values, pop_raster.y.values)
    points = np.column_stack((xx.ravel(), yy.ravel()))
    values = pop_raster.values.ravel()
    interp = NearestNDInterpolator(points, values)

    # Interpolate population values at disease data points
    pop_values = interp(disease_df.lon.values, disease_df.lat.values)

    disease_df = disease_df.copy()
    disease_df['population'] = pop_values
    
    # Replace NaN and non-positive values with 1
    disease_df['population'] = disease_df['population'].where(disease_df['population'] > 0, 1)
    
    return disease_df

