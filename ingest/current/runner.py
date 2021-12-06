from ingest.current import Pipeline
from utils import expand, set_env


if __name__ == "__main__":
    set_env()
    pipeline = Pipeline(
        expand("config/pipeline_config_current.yml", __file__),
        expand("config/storage_config_current.yml", __file__),
    )
    pipeline.run(expand("data/Sig1000_tidal.ad2cp", __file__))
