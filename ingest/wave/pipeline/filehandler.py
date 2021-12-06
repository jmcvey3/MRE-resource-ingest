import numpy as np
import pandas as pd
import xarray as xr

from tsdat import AbstractFileHandler


class SpotterFileHandler(AbstractFileHandler):
    """--------------------------------------------------------------------------------
    Custom file handler for reading <some data type> files from a <instrument name>.

    See https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/index.html for more
    examples of FileHandler implementations.

    --------------------------------------------------------------------------------"""

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """----------------------------------------------------------------------------
        Method to read data in a custom format and convert it into an xarray Dataset.

        Args:
            filename (str): The path to the file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        ----------------------------------------------------------------------------"""
        # Units are converted to m through config file
        df = pd.read_csv(filename, delimiter=",", index_col=False)
        ds = xr.Dataset(
            data_vars={
                "displacement": (
                    ["dir", "time"],
                    np.array(
                        [
                            df["outx(mm)"],
                            df["outy(mm)"],
                            df["outz(mm)"],
                        ]
                    ),
                )
            },
            coords={
                "dir": ("dir", ["x", "y", "z"]),
                "time": ("time", df["GPS_Epoch_Time(s)"] + df["millis"] * 1e-9),
            },
        )

        return ds
