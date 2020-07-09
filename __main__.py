import logging
import sys
import logging
import os


fld_name = os.path.dirname(os.path.abspath(__file__))
os.chdir(fld_name)
sys.path.append(fld_name)

from ipapi import __init__

from ipso_cli.ipso_cli import exec_cli

logger = logging.getLogger()
logger.info("Launching IPSO CLI as a module...")

if __name__ == "__main__":
    sys.exit(exec_cli())
