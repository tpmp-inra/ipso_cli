import sys
import argparse

sys.path.append("./ipapi")


from ipapi.base.pipeline_launcher import launch


if __name__ == "__main__":
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

    sys.exit(launch(**vars(parser.parse_args())))
