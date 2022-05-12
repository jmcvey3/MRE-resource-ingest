import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

from typing import Dict
from tsdat import DSUtil
from utils import IngestPipeline


class Pipeline(IngestPipeline):
    """--------------------------------------------------------------------------------
    SEQUIM_CURRENT INGESTION PIPELINE

    Velocity data from ADCP deployed on a lander in the inlet to Sequim Bay

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

        def add_colorbar(ax, plot, label):
            cb = plt.colorbar(plot, ax=ax, pad=0.01)
            cb.ax.set_ylabel(label, fontsize=12)
            cb.outline.set_linewidth(1)
            cb.ax.tick_params(size=0)
            cb.ax.minorticks_off()
            return cb

        ds = dataset
        date = pd.to_datetime(ds.time.values)

        filename = DSUtil.get_plot_filename(dataset, "h_vel", "png")
        with self.storage._tmp.get_temp_filepath(filename) as tmp_path:

            # Create the figure and axes objects
            fig, ax = plt.subplots(
                nrows=2, ncols=1, figsize=(14, 8), constrained_layout=True
            )

            magn = ax[0].pcolormesh(
                date, -ds["range"], ds["current_speed"], cmap="Blues", shading="nearest"
            )
            ax[0].set_xlabel("Time (UTC)")
            ax[0].set_ylabel(r"Range [m]")
            ax[0].set_ylim([-10, 0])
            add_colorbar(ax[0], magn, r"Speed [m/s]")
            magn.set_clim(0, 2.5)

            dirc = ax[1].pcolormesh(
                date,
                -ds["range"],
                ds["current_direction"],
                cmap="twilight",
                shading="nearest",
            )
            ax[1].set_xlabel("Time (UTC)")
            ax[1].set_ylabel(r"Range [m]")
            ax[1].set_ylim([-10, 0])
            add_colorbar(ax[1], dirc, r"Direction [deg from N]")

            # Save the figure
            fig.savefig(tmp_path, dpi=100)
            self.storage.save(tmp_path)
            plt.close()

        # filename = DSUtil.get_plot_filename(dataset, "amplitude", "png")
        # with self.storage._tmp.get_temp_filepath(filename) as tmp_path:

        #     # Create the figure and axes objects
        #     fig, ax = plt.subplots(
        #         nrows=ds.n_beams, ncols=1, figsize=(14, 8), constrained_layout=True
        #     )

        #     for beam in range(ds.n_beams):
        #         amp = ax[beam].pcolormesh(
        #             date, ds.range, ds.amplitude[beam], shading="nearest"
        #         )
        #         ax[beam].set_title("Beam " + str(beam + 1))
        #         ax[beam].set_xlabel("Time (UTC)")
        #         ax[beam].set_ylabel(r"Range [m]")
        #         ax[beam].set_ylim([0, 11])
        #         add_colorbar(ax[beam], amp, "Ampliude [dB]")

        #     # Save the figure
        #     fig.savefig(tmp_path, dpi=100)
        #     self.storage.save(tmp_path)
        #     plt.close()

        # filename = DSUtil.get_plot_filename(dataset, "correlation", "png")
        # with self.storage._tmp.get_temp_filepath(filename) as tmp_path:

        #     # Create the figure and axes objects
        #     fig, ax = plt.subplots(
        #         nrows=ds.n_beams, ncols=1, figsize=(14, 8), constrained_layout=True
        #     )

        #     for beam in range(ds.n_beams):
        #         amp = ax[beam].pcolormesh(
        #             date,
        #             ds.range,
        #             ds.correlation[beam],
        #             cmap="copper",
        #             shading="nearest",
        #         )
        #         ax[beam].set_title("Beam " + str(beam + 1))
        #         ax[beam].set_xlabel("Time (UTC)")
        #         ax[beam].set_ylabel(r"Range [m]")
        #         ax[beam].set_ylim([0, 11])
        #         add_colorbar(ax[beam], amp, "Correlation [%]")

        #     # Save the figure
        #     fig.savefig(tmp_path, dpi=100)
        #     self.storage.save(tmp_path)
        #     plt.close()
