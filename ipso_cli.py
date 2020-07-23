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
logger = logging.getLogger("IPSO CLI entry unit")
logger.info("_________________________________________________________________________")
logger.info("Launching IPSO CLI as a module...")

from ipapi.base.pipeline_launcher import launch


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
        action="store_true",
        dest="overwrite",
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
