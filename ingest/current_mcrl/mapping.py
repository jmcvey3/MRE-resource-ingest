import re

from typing import AnyStr, Dict
from utils import IngestSpec, expand
from . import Pipeline


# See https://regex101.com for information on setting up a regex pattern. Note that the
# full filepath will be passed to the compiled regex pattern, so you can optionally
# match the directory structure in addition to (or instead of) the file basename.
mapping: Dict["AnyStr@compile", IngestSpec] = {
    # Mapping for Raw Data -> Ingest
    re.compile(r".*.ad2cp"): IngestSpec(
        pipeline=Pipeline,
        pipeline_config=expand("config/pipeline_config_mcrl.yml", __file__),
        storage_config=expand("config/storage_config_mcrl.yml", __file__),
        name="current",
    ),
    # Mapping for Processed Data -> Ingest (so we can reprocess plots)
    re.compile(r".*.ad2cp"): IngestSpec(
        pipeline=Pipeline,
        pipeline_config=expand("config/pipeline_config_mcrl.yml", __file__),
        storage_config=expand("config/storage_config_mcrl.yml", __file__),
        name="plot_current",
    ),
    # You can add as many {regex: IngestSpec} entries as you would like. This is useful
    # if you would like to reuse this ingest at other locations or possibly for other
    # similar instruments
}
