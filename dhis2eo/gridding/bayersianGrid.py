import os
# Force ABI mode for Windows stability
os.environ['RPY2_CFFI_MODE'] = 'ABI'

import numpy as np
import pandas as pd
import xarray as xr
from rpy2 import robjects
from rpy2.robjects import pandas2ri, default_converter
from rpy2.robjects.conversion import localconverter

def bayesian_grid(dataValues, reso=0.1, buff=0.1):
    # 1. Prepare Grid Coordinates
    lon_min, lon_max = dataValues.lon.min(), dataValues.lon.max()
    lat_min, lat_max = dataValues.lat.min(), dataValues.lat.max()

    lon_grid = np.arange(lon_min - buff, lon_max + buff, reso)
    lat_grid = np.arange(lat_min - buff, lat_max + buff, reso)

    # 2. Prepare Data
    dataValues = dataValues.copy()
    # Handle missing cases
    dataValues['cases'] = dataValues['cases'].fillna(0)
    
    dataValues["time"] = pd.PeriodIndex.from_fields(
        year=dataValues.year,
        month=dataValues.month,
        freq="M"
    ).astype(str)
    
    times = np.sort(dataValues["time"].unique())

    # 3. Transfer to R
    with localconverter(default_converter + pandas2ri.converter):
        robjects.globalenv["df"] = robjects.conversion.py2rpy(dataValues)

    robjects.globalenv["lon_grid"] = robjects.FloatVector(lon_grid)
    robjects.globalenv["lat_grid"] = robjects.FloatVector(lat_grid)

    # 4. Run R-INLA
    robjects.r("""
    library(INLA)

    run_spde <- function(df, lon_grid, lat_grid) {
      df$time <- as.factor(df$time)
      times <- levels(df$time)

      # Create Mesh from coordinates
      mesh <- inla.mesh.2d(
        loc = as.matrix(df[,c("lon","lat")]),
        max.edge = c(0.2, 0.6),
        cutoff = 0.05
      )

      # Define SPDE spatial model
      spde <- inla.spde2.pcmatern(
        mesh,
        prior.range = c(0.5, 0.5),
        prior.sigma = c(1, 0.01)
      )

      grid <- expand.grid(lon=lon_grid, lat=lat_grid)
      A_grid <- inla.spde.make.A(mesh, loc=as.matrix(grid))
      
      out <- array(NA, dim=c(length(times), length(lat_grid), length(lon_grid)))

      for (t in seq_along(times)) {
        dft <- df[df$time == times[t], ]
        if (nrow(dft) < 5) next

        A_obs <- inla.spde.make.A(mesh, loc=as.matrix(dft[,c("lon","lat")]))

        # No 'E' argument here because we aren't using population
        stk <- inla.stack(
          data=list(y=dft$cases), 
          A=list(A_obs, 1),
          effects=list(
            spatial=1:spde$n.spde,
            intercept=rep(1, nrow(dft))
          )
        )

        res <- inla(
          y ~ 0 + intercept + f(spatial, model=spde),
          family="poisson",
          data=inla.stack.data(stk),
          control.predictor=list(A=inla.stack.A(stk), compute=TRUE)
        )

        # Reconstruct the field (Intercept + Spatial)
        intercept_m <- res$summary.fixed["intercept", "mean"]
        spatial_m <- res$summary.random$spatial$mean
        
        # Projection
        field <- as.vector(intercept_m + (A_grid %*% spatial_m))
        
        # Convert from log-link to count scale
        out[t,,] <- matrix(exp(field), nrow=length(lat_grid), byrow=TRUE)
      }

      return(out)
    }

    result <- run_spde(df, lon_grid, lat_grid)
    """)

    # 5. Build Xarray Dataset
    data_3d = np.array(robjects.globalenv["result"])

    ds = xr.Dataset(
        data_vars={
            "cases": (("time", "lat", "lon"), data_3d)
        },
        coords={
            "time": times,
            "lat": lat_grid,
            "lon": lon_grid
        }
    )

    ds["cases"].attrs = {
        "long_name": "Bayesian posterior mean case density",
        "units": "estimated cases per cell",
        "description": "Spatial redistribution using R-INLA SPDE without population offset"
    }

    return ds