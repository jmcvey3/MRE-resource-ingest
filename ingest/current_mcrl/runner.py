from ingest.current_mcrl import Pipeline
from utils import expand, set_env
from glob import glob
import os


if __name__ == "__main__":
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_mcrl.yml", __file__),
        expand("config/storage_config_mcrl.yml", __file__),
    )

    os.chdir("ingest/current_mcrl")
    files = glob(os.path.join("data", "*.ad2cp"))
    for fname in files:
        pipeline.run(expand(fname, __file__))
