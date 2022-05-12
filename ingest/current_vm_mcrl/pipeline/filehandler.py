import xarray as xr
import dolfyn as dlfn
from dolfyn.adp import api
from tsdat import AbstractFileHandler


class AdcpDownHandler(AbstractFileHandler):
    """-------------------------------------------------------------------
    Custom file handler for reading ADCP binary files.
    -------------------------------------------------------------------"""

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """-------------------------------------------------------------------
        Classes derived from the FileHandler class can implement this method.
        to read a custom file format into a xr.Dataset object.

        Args:
            filename (str): The path to the ADCP file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        -------------------------------------------------------------------"""

        ds = dlfn.read(filename)

        # The ADCP transducers were measured to be 0.6 m from the feet of the lander
        d = self.parameters["depth"]
        api.clean.set_range_offset(ds, d)

        # Locate surface using pressure data and remove data above it
        at = self.parameters["amp_threshold"]
        api.clean.find_surface(ds, thresh=at)
        ds = api.clean.nan_beyond_surface(ds)

        # Rotate to Earth coordinates
        declin = self.parameters["magn_declination"]
        dlfn.set_declination(ds, declin)
        dlfn.rotate2(ds, "earth")

        ct = self.parameters["corr_threshold"]
        ds = api.clean.correlation_filter(ds, thresh=ct)

        # Velocity magnitude and direction in degrees from N
        ds["U_mag"] = ds.velds.U_mag
        ds["U_dir"] = ds.velds.U_dir
        ds.U_dir.values = dlfn.tools.misc.convert_degrees(ds.U_dir.values)

        # Dropping the detailed configuration stats because netcdf can't save it
        for key in list(ds.attrs.keys()):
            if "config" in key:
                ds.attrs.pop(key)

        # Fix x* coordinate
        ds.coords["inst*"] = ("x*", ["X", "Y", "Z1", "Z2"])
        return ds.swap_dims({"x*": "inst*"})
