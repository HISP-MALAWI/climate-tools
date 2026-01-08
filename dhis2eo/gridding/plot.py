import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd

def plotData(data, overlay, cmap="Reds"):
    """
    Plot a single-time-step xarray DataArray on a map.
    """

    overlay = gpd.read_file(r"C:\Users\ShnkMn\Documents\CMS\climate-tools\docs\data\Districts.shp")
    overlay = overlay.to_crs(epsg=4326)
    # Ensure we have a 2D array for plotting
    if "time" in data.dims:
        data2d = data.isel(time=0)
    else:
        data2d = data

    fig, ax = plt.subplots(
        figsize=(10, 8),
        subplot_kw={"projection": ccrs.PlateCarree()}
    )

    # Plot raster
    pcm = ax.pcolormesh(
        data2d["lon"],
        data2d["lat"],
        data2d.values,
        cmap=cmap,
        shading="auto",
        transform=ccrs.PlateCarree()
    )

    # Plot boundaries
    overlay.boundary.plot(
        ax=ax,
        linewidth=0.8,
        edgecolor="black"
    )

    ax.coastlines(resolution="10m")
    ax.set_title(data2d.attrs.get("long_name", data2d.name))

    cbar = plt.colorbar(pcm, ax=ax, shrink=0.8)
    cbar.set_label(data2d.attrs.get("units", ""))

    plt.tight_layout()
    plt.show()
