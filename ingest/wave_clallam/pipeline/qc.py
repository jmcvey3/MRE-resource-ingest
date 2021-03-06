import numpy as np
from typing import Optional

from dolfyn.adv.clean import GN2002, clean_fill
from tsdat import DSUtil, QualityChecker, QualityHandler


class CustomQualityChecker(QualityChecker):
    def run(self, variable_name: str) -> Optional[np.ndarray]:

        # False values in the results array mean the check passed, True values indicate
        # the check failed. Here we initialize the array to be full of False values as
        # an example. Note the shape of the results array must match the variable data.
        results_array = np.full_like(
            self.ds[variable_name].data,
            fill_value=False,
            dtype=bool,
        )

        return results_array


class CustomQualityHandler(QualityHandler):
    def run(self, variable_name: str, results_array: np.ndarray):

        # Some QualityHandlers only want to run if at least one value failed the check.
        # In this case, we replace all values that failed the check with the variable's
        # _FillValue and (possibly) add an attribute to the variable indicating the
        # correction applied.
        if results_array.any():

            fill_value = DSUtil.get_fill_value(self.ds, variable_name)
            keep_array = np.logical_not(results_array)

            var_values = self.ds[variable_name].data
            replaced_values = np.where(keep_array, var_values, fill_value)
            self.ds[variable_name].data = replaced_values

            self.record_correction(variable_name)


class GoringNikora2002(QualityChecker):
    def run(self, variable_name: str) -> Optional[np.ndarray]:
        """----------------------------------------------------------------------------
        The Goring & Nikora 2002 'despiking' method, with Wahl2003 correction.
        Returns a logical vector that is true where spikes are identified.

        Args:
            variable_name (str): array (1D or 3D) to clean.
            n_points (int) : The number of points over which to perform the method.

        Returns:
            mask [np.ndarray]: Logical vector with spikes labeled as 'True'

        ----------------------------------------------------------------------------"""

        return GN2002(self.ds[variable_name], npt=self.params["n_points"])


class CubicSplineInterp(QualityHandler):
    def run(self, variable_name: str, results_array: np.ndarray):
        """
        Interpolate over mask values in timeseries data using the specified method

        Parameters
        ----------
        variable_name : xarray.DataArray
            The dataArray to clean.
        mask : bool
            Logical tensor of elements to "nan" out and replace
        npt : int
            The number of points on either side of the bad values that
        interpolation occurs over
        method : string
            Interpolation scheme to use (linear, cubic, pchip, etc)
        max_gap : int
            Max number of consective nan's to interpolate across, must be <= npt/2

        Returns
        -------
        da : xarray.DataArray
            The dataArray with nan's filled in

        """
        if results_array.any():

            self.ds[variable_name] = clean_fill(
                self.ds[variable_name], mask=results_array, npt=12, method="cubic"
            )
            self.record_correction(variable_name)
