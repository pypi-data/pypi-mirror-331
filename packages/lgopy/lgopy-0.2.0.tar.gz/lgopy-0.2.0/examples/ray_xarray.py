import numpy as np
import xarray as xr

import ray

ray.init()

data = xr.DataArray(np.random.randn(2, 3), coords={'x': ['a', 'b']}, dims=('x', 'y'))
ray.put(data)

ds = xr.Dataset(
    {
        "a": ("x", [1, 2]),
        "b": ("y", np.random.randn(3)),
    },
    coords={"x": ["a", "b"], "y": np.arange(3)},
)
ray.put(ds)


#ray.data.from_xarray(data)