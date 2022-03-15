import os
from glob import glob

from ingest.wave_clallam import Pipeline
from utils import expand, set_env


if __name__ == "__main__":
    # Run wave data
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_clallam_wave.yml", __file__),
        expand("config/storage_config_clallam.yml", __file__),
    )
    files = glob(os.path.join("ingest", "wave_clallam", "data", "Aug2021", "*_FLT.CSV"))
    for fname in files:
        fname = os.path.join(*fname.rsplit("/")[2:])
        pipeline.run(expand(fname, __file__))

    # Run GPS data
    pipeline = Pipeline(
        expand("config/pipeline_config_clallam_gps.yml", __file__),
        expand("config/storage_config_clallam.yml", __file__),
    )
    files = glob(os.path.join("ingest", "wave_clallam", "data", "Aug2021", "*_LOC.CSV"))
    for fname in files:
        fname = os.path.join(*fname.rsplit("/")[2:])
        pipeline.run(expand(fname, __file__))
