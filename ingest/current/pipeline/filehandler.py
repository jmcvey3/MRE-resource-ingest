import xarray as xr

import dolfyn as dlfn
import dolfyn.adp.api as api
from tsdat import AbstractFileHandler


# TODO – Developer: Write your FileHandler and add documentation
class CustomFileHandler(AbstractFileHandler):
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
        return xr.Dataset()


class DolfynFileHandler(AbstractFileHandler):
    """-------------------------------------------------------------------
    Custom file handler for reading *.wpr files.
    -------------------------------------------------------------------"""

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """-------------------------------------------------------------------
        Classes derived from the FileHandler class can implement this method.
        to read a custom file format into a xr.Dataset object.

        Args:
            filename (str): The path to the ADCP/ADV file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        -------------------------------------------------------------------"""

        ds = dlfn.read(filename)

        # The ADCP transducers were measured to be 0.6 m from the feet of the lander
        ds = api.clean.set_range_offset(ds, 0.6)

        # Locate surface using pressure data and remove data above it
        ds = api.clean.surface_from_P(ds, salinity=31)
        ds = api.clean.nan_beyond_surface(ds)

        # Rotate to Earth coordinates
        ds = dlfn.set_declination(ds, 15.8)  # 15.8 deg East
        ds = dlfn.rotate2(ds, "earth")
        ds = api.clean.correlation_filter(ds, thresh=50)

        # Velocity magnitude and direction in degrees from N
        ds["U_mag"] = ds.Veldata.U_mag
        ds["U_dir"] = ds.Veldata.U_dir
        ds.U_dir.values = dlfn.tools.misc.convert_degrees(ds.U_dir.values)

        # Dropping the detailed configuration stats because netcdf can't save it
        for key in list(ds.attrs.keys()):
            if "config" in key:
                ds.attrs.pop(key)

        return ds
