import os
import cmocean
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

from typing import Dict
from tsdat import DSUtil
from utils import IngestPipeline, format_time_xticks


# TODO – Developer: Use hooks to add custom functionality to the pipeline including
# plots, as applicable. Remove any unused code.


class Pipeline(IngestPipeline):
    """--------------------------------------------------------------------------------
    SPOTTER_BUOY INGESTION PIPELINE

    Wave data taken in Clallam Bay over a month-long deployment in Aug-Sep 2021

    --------------------------------------------------------------------------------"""

    def hook_customize_raw_datasets(
        self, raw_dataset_mapping: Dict[str, xr.Dataset]
    ) -> Dict[str, xr.Dataset]:
        """-------------------------------------------------------------------
        Hook to allow for user customizations to one or more raw xarray Datasets
        before they merged and used to create the standardized dataset.  The
        raw_dataset_mapping will contain one entry for each file being used
        as input to the pipeline.  The keys are the standardized raw file name,
        and the values are the datasets.

        This method would typically only be used if the user is combining
        multiple files into a single dataset.  In this case, this method may
        be used to correct coordinates if they don't match for all the files,
        or to change variable (column) names if two files have the same
        name for a variable, but they are two distinct variables.

        This method can also be used to check for unique conditions in the raw
        data that should cause a pipeline failure if they are not met.

        This method is called before the inputs are merged and converted to
        standard format as specified by the config file.

        Args:
        ---
            raw_dataset_mapping (Dict[str, xr.Dataset])     The raw datasets to
                                                            customize.

        Returns:
        ---
            Dict[str, xr.Dataset]: The customized raw dataset.
        -------------------------------------------------------------------"""
        return raw_dataset_mapping

    def hook_customize_dataset(
        self, dataset: xr.Dataset, raw_mapping: Dict[str, xr.Dataset]
    ) -> xr.Dataset:
        """-------------------------------------------------------------------
        Hook to allow for user customizations to the standardized dataset such
        as inserting a derived variable based on other variables in the
        dataset.  This method is called immediately after the apply_corrections
        hook and before any QC tests are applied.

        Args:
        ---
            dataset (xr.Dataset): The dataset to customize.
            raw_mapping (Dict[str, xr.Dataset]):    The raw dataset mapping.

        Returns:
        ---
            xr.Dataset: The customized dataset.
        -------------------------------------------------------------------"""
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        """-------------------------------------------------------------------
        Hook to apply any final customizations to the dataset before it is
        saved. This hook is called after quality tests have been applied.

        Args:
            dataset (xr.Dataset): The dataset to finalize.

        Returns:
            xr.Dataset: The finalized dataset to save.
        -------------------------------------------------------------------"""
        return dataset

    def hook_generate_and_persist_plots(self, dataset: xr.Dataset):
        """-------------------------------------------------------------------
        Hook to allow users to create plots from the xarray dataset after
        processing and QC have been applied and just before the dataset is
        saved to disk.

        To save on filesystem space (which is limited when running on the
        cloud via a lambda function), this method should only
        write one plot to local storage at a time. An example of how this
        could be done is below:

        ```
        filename = DSUtil.get_plot_filename(dataset, "sea_level", "png")
        with self.storage._tmp.get_temp_filepath(filename) as tmp_path:
            fig, ax = plt.subplots(figsize=(10,5))
            ax.plot(dataset["time"].data, dataset["sea_level"].data)
            fig.save(tmp_path)
            storage.save(tmp_path)

        filename = DSUtil.get_plot_filename(dataset, "qc_sea_level", "png")
        with self.storage._tmp.get_temp_filepath(filename) as tmp_path:
            fig, ax = plt.subplots(figsize=(10,5))
            DSUtil.plot_qc(dataset, "sea_level", tmp_path)
            storage.save(tmp_path)
        ```

        Args:
        ---
            dataset (xr.Dataset):   The xarray dataset with customizations and
                                    QC applied.
        -------------------------------------------------------------------"""
        style_file = os.path.join(os.path.dirname(__file__), "styling.mplstyle")
        ds = dataset

        with plt.style.context(style_file):
            filename = DSUtil.get_plot_filename(dataset, "buoy_displacement", "png")
            with self.storage._tmp.get_temp_filepath(filename) as tmp_path:
                fig, ax = plt.subplots()

                ax.plot(ds.time, ds.displacement.sel(dir="x"), label="x-direction")
                ax.plot(ds.time, ds.displacement.sel(dir="y"), label="y-direction")
                ax.plot(ds.time, ds.displacement.sel(dir="z"), label="z-direction")

                ax.set_title("")  # Remove bogus title created by xarray
                ax.legend(ncol=2, bbox_to_anchor=(1, -0.05))
                ax.set_ylabel("Disp [m]")
                ax.set_xlabel("Time [UTC]")
                format_time_xticks(ax)
                plt.legend()

                fig.savefig(tmp_path)
                self.storage.save(tmp_path)
                plt.close(fig)
