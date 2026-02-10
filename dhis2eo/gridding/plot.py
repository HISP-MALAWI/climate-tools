import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd
import numpy as np
from matplotlib.colors import LogNorm  # Essential for showing detail

def plotData(data, overlay=None, cmap="YlOrRd"):
    """
    Plot a single-time-step xarray DataArray on a map with a Logarithmic scale.
    """
    # Load overlay if path is provided
    if isinstance(overlay, str):
        overlay = gpd.read_file(overlay)
        overlay = overlay.to_crs(epsg=4326)

    # 1. Handle Dimensions
    if "time" in data.dims:
        data2d = data.isel(time=0)
    else:
        data2d = data

    fig, ax = plt.subplots(
        figsize=(10, 10),
        subplot_kw={"projection": ccrs.PlateCarree()}
    )

    # 2. Set dynamic min/max based on data (ignoring zeros/NaNs)
    # This ensures the scale fits your specific data perfectly
    valid_data = data2d.values[data2d.values > 0]
    data_min = np.percentile(valid_data, 5) if valid_data.size > 0 else 1
    data_max = np.percentile(valid_data, 95) if valid_data.size > 0 else 1000

    # 3. Use LogNorm for the "Detail" boost
    pcm = ax.pcolormesh(
        data2d["lon"],
        data2d["lat"],
        data2d.values,
        norm=LogNorm(vmin=data_min, vmax=data_max), # Logarithmic scaling
        cmap=cmap,
        shading="auto",
        transform=ccrs.PlateCarree()
    )

    # Plot boundaries
    if overlay is not None:
        overlay.boundary.plot(
            ax=ax,
            linewidth=0.6,
            edgecolor="black",
            alpha=0.7
        )

    # Zoom into the data extent (adds more detail by removing empty space)
    ax.set_extent([data2d.lon.min(), data2d.lon.max(), 
                   data2d.lat.min(), data2d.lat.max()])

    ax.coastlines(resolution="10m")
    title = data2d.attrs.get("long_name", "Spatial Distribution")
    ax.set_title(f"{title}\n(Logarithmic Scale)", fontsize=14)

    # Colorbar with log formatting
    cbar = plt.colorbar(pcm, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label(data2d.attrs.get("units", "Value"))

    plt.tight_layout()
    plt.show()