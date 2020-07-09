import sys
import argparse
import logging

from ipapi.base.pipeline_launcher import launch


def exec_cli():

    parser = argparse.ArgumentParser(description="Run a pipeline on target")
    parser.add_argument(
        "-s",
        "--stored_state",
        default=None,
        required=False,
        help="Path to the stored state built with IPSO Phen",
    )
    parser.add_argument(
        "-p",
        "--script",
        required=False,
        help="File containing an IPSO Phen pipeline",
        default=None,
    )
    parser.add_argument(
        "-i", "--image", required=False, help="Image to be processed", default=None
    )
    parser.add_argument(
        "-l",
        "--image_list",
        required=False,
        help="File containing a list of images to be processed",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--thread_count",
        required=False,
        help="Override number of concurrent processes",
        default=None,
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        required=False,
        help="CSV and data output folder",
        default=None,
    )
    parser.add_argument(
        "-f", "--csv_file_name", required=False, help="Merged CSV file name", default=None
    )

    args = vars(parser.parse_args())
    logger = logging.getLogger(__name__)
    for k, v in args.items():
        logger.info(f"{k}: {v}")

    return launch(**args)


if __name__ == "__main__":
    sys.exit(exec_cli())
