import numpy as np
import pandas as pd
import xarray as xr
import warnings
from tsdat import AbstractFileHandler


class SpotterFltFileHandler(AbstractFileHandler):
    """--------------------------------------------------------------------------------
    Custom file handler for reading flt.csv files (motion data) from a Sofar Spotter
    wave buoy.
    --------------------------------------------------------------------------------"""

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """----------------------------------------------------------------------------
        Method to read data in a custom format and convert it into an xarray Dataset.

        Args:
            filename (str): The path to the file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        ----------------------------------------------------------------------------"""
        # Reads "FLT" filetype from spotter: wave displacement data
        # Units are converted to m through config file

        # Ignore pandas ParserWarning:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
                ),
                "t_elapsed": (["time"], df["millis"]),
            },
            coords={
                "dir": ("dir", ["x", "y", "z"]),
                "time": ("time", df["GPS_Epoch_Time(s)"]),
            },
        )
        return ds


class SpotterLocFileHandler(AbstractFileHandler):
    """--------------------------------------------------------------------------------
    Custom file handler for reading loc.csv files (gps data) from a Sofar Spotter
    wave buoy.
    --------------------------------------------------------------------------------"""

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """----------------------------------------------------------------------------
        Method to read data in a custom format and convert it into an xarray Dataset.

        Args:
            filename (str): The path to the file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        ----------------------------------------------------------------------------"""

        # Reads "LOC" filetype from spotter: GPS data
        df = pd.read_csv(filename, delimiter=",", index_col=False)
        ds = xr.Dataset(
            data_vars={
                "lat": (
                    ["time"],
                    np.array(df["lat(deg)"] + df["lat(min*1e5)"] * 1e-5 / 60),
                ),
                "lon": (
                    ["time"],
                    np.array(df["long(deg)"] + df["long(min*1e5)"] * 1e-5 / 60),
                ),
            },
            coords={"time": ("time", df["GPS_Epoch_Time(s)"])},
        )
        return ds
