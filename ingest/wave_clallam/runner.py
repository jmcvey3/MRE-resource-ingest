import os
from glob import glob

from ingest.wave_clallam import Pipeline
from utils import expand, set_env


if __name__ == "__main__":
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_clallam.yml", __file__),
        expand("config/storage_config_clallam.yml", __file__),
    )

    os.chdir("ingest/wave")
    files = glob(os.path.join("data", "xyz", "*_FLT.CSV"))
    for fname in files:
        pipeline.run(expand(fname, __file__))
