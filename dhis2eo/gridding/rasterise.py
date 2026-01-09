import numpy as np
import rasterio.features
import xarray as xr

def rasterize_population(pop_gdf, cases_da, pop_col="population"):
    if not cases_da.rio.crs:
        cases_da = cases_da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
        cases_da = cases_da.rio.write_crs("EPSG:4326")

    if pop_gdf.crs != cases_da.rio.crs:
        pop_gdf = pop_gdf.to_crs(cases_da.rio.crs)

    transform = cases_da.rio.transform()
    out_shape = (cases_da.sizes["lat"], cases_da.sizes["lon"])

    shapes = ((geom, value) for geom, value in zip(pop_gdf.geometry, pop_gdf[pop_col]))

    raster = rasterio.features.rasterize(
        shapes=shapes,
        out_shape=out_shape,
        transform=transform,
        fill=0,
        dtype="float32"
    )

    pop_da = xr.DataArray(
        raster,
        coords={"lat": cases_da["lat"], "lon": cases_da["lon"]},
        dims=("lat", "lon"),
        name="population"
    )

    # 5️⃣ Register spatial dims and CRS
    pop_da = pop_da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    pop_da = pop_da.rio.write_crs(cases_da.rio.crs)

    return pop_da
