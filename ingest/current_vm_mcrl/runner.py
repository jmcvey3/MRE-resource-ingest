from ingest.current_vm_mcrl import Pipeline
from utils import expand, set_env
from glob import glob
import os


if __name__ == "__main__":
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_vm.yml", __file__),
        expand("config/storage_config_vm.yml", __file__),
    )

    files = glob(os.path.join("ingest", "current_vm_mcrl", "data", "*.ad2cp"))
    for fname in files:
        fname = os.path.join(*fname.rsplit("/")[2:])
        pipeline.run(expand(fname, __file__))
