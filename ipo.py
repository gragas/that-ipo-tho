import os
import re
import sys
import time

import nltk
import requests
import sklearn

URL = "URL"
CACHED = "CACHED"

def main():
    # get the time (this will be used to eventually calculate total run time)
    start_time = time.time()

    # get the command line arguments
    args = sys.argv
    # get the current working directory
    cwd = os.getcwd()
    # set the mode to URL by default
    mode = URL
    # set the output location to "results.txt" by default
    output_location = "results.txt"

    # strip the first argument (it's always "some/path/ipo.py")
    if len(args) > 1:
        args = args[1:]
    else:
        args = []

    # process the args
    for arg in args:
        if arg.startswith("-mode="):
            target = arg[len("-mode="):]
            if target.lower() == "url":
                mode = URL
            elif target.lower() == "cached":
                mode = CACHED
            else:
                print("Invalid mode \"{}\"".format(target))
                sys.exit(1)
        elif arg.startswith("-output="):
            raw_target = arg[len("-output="):]
            target = "".join(raw_target.strip().split())
            if not target == raw_target:
                print("WARNING: " + \
                      "Invalid output location \"{}\"".format(raw_target) + \
                      ". Using \"{}\" instead.".format(target))
            if not target:
                print("Output location is an empty string.")
                sys.exit(1)
            output_location = target
        else:
            print("Invalid argument \"{}\"".format(arg))
            sys.exit(1)

    # print out what is going to happen
    print("Running IPO in {} mode...".format(mode))
    print("Output location: {}".format(output_location))

    # do stuff based on the mode
    if mode == URL:
        if not os.path.isfile(os.path.join(cwd, "urls.txt")):
            print("There is no \"urls.txt\" file in the path \"{}\"".format(
                cwd))
            sys.exit(1)
        file_path = os.path.join(cwd, "urls.txt")
        # finish this
    elif mode == CACHED:
        if not os.path.isdir(os.path.join(cwd, "data")):
            print("There is no \"data\" directory in the path \"{}\"".format(
                cwd))
            sys.exit(1)
        data_path = os.path.join(cwd, "data")
        # finish this
    else:
        print("Invalid mode. Please contact the developers: tdfisch2 " \
              "at illinois dot edu")
        sys.exit(1)

    # print out the run time
    time_delta = time.time() - start_time
    print("SUCCESS! Run time: {:.1f} seconds".format(time_delta))

if __name__ == "__main__":
    main()
