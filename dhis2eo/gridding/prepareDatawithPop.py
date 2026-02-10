import xarray as xr

def prepare_data_with_pop(disease_df, pop_ds):
    sampled_pop = []
    
    pop_raster = pop_ds.total_pop.isel(band=0)

    target_lon = xr.DataArray(disease_df.lon.values, dims="points")
    target_lat = xr.DataArray(disease_df.lat.values, dims="points")

    pop_values = pop_raster.sel(x=target_lon, y=target_lat, method="nearest").values

    disease_df = disease_df.copy()
    disease_df['population'] = pop_values
    
    disease_df['population'] = disease_df['population'].fillna(1).replace(0, 1)
    
    return disease_df

