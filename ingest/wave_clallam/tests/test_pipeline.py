import os
import xarray as xr
from utils import expand, set_env
from ingest.wave_clallam import Pipeline

parent = os.path.dirname(__file__)


def test_wave_pipeline():
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_clallam.yml", parent),
        expand("config/storage_config_clallam.yml", parent),
    )
    output = pipeline.run(expand("tests/data/input/data.csv", parent))
    expected = xr.open_dataset(expand("tests/data/expected/data.csv", parent))
    xr.testing.assert_allclose(output, expected)
