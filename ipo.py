import os
import sys
import time

from bs4 import BeautifulSoup
import nltk.sentiment
import requests
import sklearn

URL = "URL"
CACHED = "CACHED"

scores = dict()

def analyze(url, data):
    # extract the text from the html data
    soup = BeautifulSoup(data, "html.parser")
    for unwanted in soup(["script", "style"]):
        unwanted.extract()
    text = soup.get_text()
    if not text:
        print("Could not extract information from \"{}\"".format(url))
        return
    # analyze the text
    sid = nltk.sentiment.vader.SentimentIntensityAnalyzer()
    polarity_scores = sid.polarity_scores(text)
    score = (polarity_scores['neg'], polarity_scores['pos'], 1.0)
    # add the polarity score to the scores dict, with a weight of 1 (for now)
    scores[url] = score
    print("Successfully analyzed \"{}\"".format(url))

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
        # Create the file path
        if not os.path.isfile(os.path.join(cwd, "urls.txt")):
            print("There is no \"urls.txt\" file in the path \"{}\"".format(
                cwd))
            sys.exit(1)
        file_path = os.path.join(cwd, "urls.txt")
        # read the file and store the apparent urls
        urls = list()
        with open(file_path, "r") as urls_file:
            for line in urls_file:
                line = line.strip()
                if not line:
                    continue
                urls.append(line)
        # request each url and analyze it
        for url in urls:
            # download each webpage
            r = requests.get(url)
            if not r.status_code == 200:
                print("Could not access \"{}\"".format(url))
                continue
            else:
                print("Successfully accessed \"{}\"".format(url))
            # analyze the data
            analyze(url, r.text)
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

    # check to see if scores were collected
    if not scores:
        print("No polarity scores were collected.")
        sys.exit(1)

    # print out the weighted polarity scores
    total_pos = sum([pos * weight for (neg, pos, weight) in scores.values()])
    total_neg = sum([neg * weight for (neg, pos, weight) in scores.values()])
    total_weight = sum([weight for (neg, pos, weight) in scores.values()])
    average_pos = total_pos / total_weight
    average_neg = total_neg / total_weight
    print("Weighted negativity score: {:.3f}".format(average_neg))
    print("Weighted positivity score: {:.3f}".format(average_pos))

    # write the values to the output file
    with open(output_location, "w") as output_file:
        output_file.write("{} {}\n".format(average_neg, average_pos))
    print("Successfully wrote results to \"{}\"".format(output_location))

    # print out the total run time
    time_delta = time.time() - start_time
    print("SUCCESS! Run time: {:.1f} seconds".format(time_delta))

if __name__ == "__main__":
    main()
