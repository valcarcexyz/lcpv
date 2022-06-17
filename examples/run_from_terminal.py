"""
This script provides a simple example execution from the terminal args. Can be run when the package is installed
with pip or importing it from the src_old folder.
"""

import sys

# run once installed with pip
from src.lcpv.edge_process import LCPV

if __name__ == "__main__":
    from utils.args_parser import parse
    run_parameters = parse(sys.argv)

    capturer = LCPV()
    capturer.start(**run_parameters)

    # what to do with the results is a job for the end user, so for now we just print it
    print(capturer.median_results)
