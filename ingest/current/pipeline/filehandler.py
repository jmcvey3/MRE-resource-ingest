import xarray as xr

import dolfyn as dlfn
import dolfyn.adp.api as api
from tsdat import AbstractFileHandler


class AdcpUpHandler(AbstractFileHandler):
    """-------------------------------------------------------------------
    Custom file handler for reading *.wpr files.
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
        depth = self.parameters["depth"]
        ds = api.clean.set_range_offset(ds, depth)

        # Locate surface using pressure data and remove data above it
        s = self.parameters["salinity"]
        ds = api.clean.surface_from_P(ds, salinity=s)
        ds = api.clean.nan_beyond_surface(ds)

        # Rotate to Earth coordinates
        declin = self.parameters["magn_declination"]
        ds = dlfn.set_declination(ds, declin)  # 15.8 deg East
        ds = dlfn.rotate2(ds, "earth")

        thresh = self.parameters["corr_threshold"]
        ds = api.clean.correlation_filter(ds, thresh=thresh)

        # Velocity magnitude and direction in degrees from N
        ds["U_mag"] = ds.Veldata.U_mag
        ds["U_dir"] = ds.Veldata.U_dir
        ds.U_dir.values = dlfn.tools.misc.convert_degrees(ds.U_dir.values)

        # Dropping the detailed configuration stats because netcdf can't save it
        for key in list(ds.attrs.keys()):
            if "config" in key:
                ds.attrs.pop(key)

        return ds


class AdcpDownHandler(AbstractFileHandler):
    """-------------------------------------------------------------------
    Custom file handler for reading *.wpr files.
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
        ds = api.clean.set_range_offset(ds, d)

        # Locate surface using pressure data and remove data above it
        at = self.parameters["amp_threshold"]
        ds = api.clean.find_surface(ds, thresh=at)
        ds = api.clean.nan_beyond_surface(ds)

        # Rotate to Earth coordinates
        declin = self.parameters["magn_declination"]
        ds = dlfn.set_declination(ds, declin)
        ds = dlfn.rotate2(ds, "earth")

        ct = self.parameters["corr_threshold"]
        ds = api.clean.correlation_filter(ds, thresh=ct)

        # Velocity magnitude and direction in degrees from N
        ds["U_mag"] = ds.Veldata.U_mag
        ds["U_dir"] = ds.Veldata.U_dir
        ds.U_dir.values = dlfn.tools.misc.convert_degrees(ds.U_dir.values)

        # Dropping the detailed configuration stats because netcdf can't save it
        for key in list(ds.attrs.keys()):
            if "config" in key:
                ds.attrs.pop(key)

        return ds


class AdvHandler(AbstractFileHandler):
    """-------------------------------------------------------------------
    Custom file handler for reading *.wpr files.
    -------------------------------------------------------------------"""

    def read(self, filename: str, **kwargs) -> xr.Dataset:
        """-------------------------------------------------------------------
        Classes derived from the FileHandler class can implement this method.
        to read a custom file format into a xr.Dataset object.

        Args:
            filename (str): The path to the ADV file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        -------------------------------------------------------------------"""

        ds = dlfn.read(filename)

        # Clean the file using the Goring+Nikora method:
        npt = self.parameters["npt"]
        mask = api.clean.GN2002(ds.vel, npt=npt)
        # Replace bad datapoints via cubic spline interpolation
        ds["vel"] = api.clean.clean_fill(ds["vel"], mask, npt=12, method="cubic")

        # First set the magnetic declination
        declin = self.parameters["magn_declination"]
        ds = dlfn.set_declination(ds, declin)

        # Rotate that data from the instrument to earth frame (ENU):
        ds = dlfn.rotate2(ds, "earth")

        ds.attrs["principal_heading"] = dlfn.calc_principal_heading(ds.vel)
        ds = dlfn.rotate2(ds, "principal")

        # Dropping the detailed configuration stats because netcdf can't save it
        for key in list(ds.attrs.keys()):
            if "config" in key:
                ds.attrs.pop(key)

        return ds
