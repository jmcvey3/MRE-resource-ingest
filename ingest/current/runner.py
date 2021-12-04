from ingest.sequim_current_mcrl import Pipeline
from utils import expand, set_env


# TODO – Developer: Update path to data and/or configuration files as needed.
if __name__ == "__main__":
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_sequim_current_mcrl.yml", __file__),
        expand("config/storage_config_sequim_current_mcrl.yml", __file__),
    )
    pipeline.run(expand("data/Sig1000_tidal", __file__))
