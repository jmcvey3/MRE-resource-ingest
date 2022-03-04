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
    os.chdir("ingest/wave_clallam")
    files = glob(os.path.join("data", "Aug2021", "*_FLT.CSV"))
    for fname in files:
        pipeline.run(expand(fname, __file__))

    # Run GPS data
    pipeline = Pipeline(
        expand("config/pipeline_config_clallam_gps.yml", __file__),
        expand("config/storage_config_clallam.yml", __file__),
    )
    files = glob(os.path.join("data", "Aug2021", "*_LOC.CSV"))
    for fname in files:
        pipeline.run(expand(fname, __file__))
