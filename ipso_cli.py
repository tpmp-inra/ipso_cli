import sys
import argparse
import logging
import os
import logging

if not os.path.exists("logs"):
    os.mkdir("logs")
logging.basicConfig(
    filename=os.path.join("logs", "log.log"),
    filemode="a",
    level=logging.INFO,
    format="[%(asctime)s - %(name)s - %(levelname)s] - %(message)s",
)
logger = logging.getLogger("IPSO CLI")
logger.info("_________________________________________________________________________")
logger.info("_________________________________________________________________________")
logger.info("Launching IPSO CLI")

from ipapi.base.pipeline_launcher import launch


class StoreTrueOnly(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super(StoreTrueOnly, self).__init__(
            option_strings=option_strings, nargs=nargs, dest=dest, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)


def exec_cli():

    parser = argparse.ArgumentParser(
        description="Command line interface for pipelines built with IPSO Phen",
        epilog="""
        Even if all arguments are optional, some must be present.
        Stored state can be used alone. If not present there must 
        be a source a script an output_folder and a csv_file_name at least.
        """,
        allow_abbrev=False,
    )
    parser.add_argument(
        "--stored-state",
        default=None,
        required=False,
        help="Path to the stored state built with IPSO Phen",
        dest="stored_state",
    )
    parser.add_argument(
        "--script",
        required=False,
        help="File containing an IPSO Phen pipeline",
        default=None,
        dest="script",
    )
    parser.add_argument(
        "--image", required=False, help="Image to be processed", default=None, dest="image"
    )
    parser.add_argument(
        "--image-list",
        required=False,
        help="File containing a list of images to be processed",
        default=None,
        dest="image_list",
    )
    parser.add_argument(
        "--thread-count",
        required=False,
        help="Override number of concurrent processes",
        default=None,
        type=int,
        dest="thread_count",
    )
    parser.add_argument(
        "--output-folder",
        required=False,
        help="CSV and data output folder",
        default=None,
        dest="output_folder",
    )
    parser.add_argument(
        "--csv-file-name",
        required=False,
        help="Merged CSV file name",
        default=None,
        dest="csv_file_name",
    )
    parser.add_argument(
        "--overwrite",
        required=False,
        help="Overwrite existing partial files",
        action=StoreTrueOnly,
        dest="overwrite",
    )
    parser.add_argument(
        "--build-annotation-csv",
        required=False,
        help="Build annotation ready CSV",
        action=StoreTrueOnly,
        dest="build_annotation_csv",
        nargs=0,
    )
    parser.add_argument(
        "--generate-series-id",
        required=False,
        help="Generate series id, group plants by close timestamp",
        action=StoreTrueOnly,
        dest="generate_series_id",
    )
    parser.add_argument(
        "--series-id-delta",
        required=False,
        help="Images of an item taken within minutes of time delta will have the same series id",
        default=None,
        type=int,
        dest="series_id_time_delta",
    )

    args = vars(parser.parse_args())
    logger.info("Retrieved parameters")
    for k, v in args.items():
        logger.info(f"  * {k}: {v}")

    return launch(**args)


if __name__ == "__main__":
    res = exec_cli()
    if res == 0:
        logger.info("Closing IPSO CLI")
    else:
        logger.error("Closing IPSO CLI")
    logger.info("_________________________________________________________________________")
    sys.exit(res)
