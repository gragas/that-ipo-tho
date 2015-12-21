import os
import sys
import time

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

collected_percent_deltas = dict()
collected_negative_scores = dict()
collected_positive_scores = dict()
collected_folder_names = list()

def plot(x, y, x_label, y_label):
    # set the title and label the x and y axes
    plt.title("{} vs {}".format(y_label, x_label))
    plt.xlabel(x_label.lower())
    plt.ylabel(y_label.lower())
    # do a linear regression
    slope, intercept, r_value, ___, std_err = stats.linregress(x, y)
    # calculate the best fit values
    best_fit_values = [slope * _ + intercept for _ in x]
    # create the labels for the legend
    first_legend_label = "Data point"
    second_legend_label = "Prediction of {} given {}".format(
        y_label.lower()[:-1], x_label.lower()[:-1])
    third_legend_label = "Positive return line"
    # plot the data points as a scatter plot
    plt.plot(x, y, "ro", label=first_legend_label)
    # plot the best fit values as a line
    plt.plot(x, best_fit_values, "b", label=second_legend_label)
    # calculate the x and y position of the r^2 value text
    y_min, y_max = plt.gca().get_ylim()
    x_min, x_max = plt.gca().get_xlim()
    y_range = y_max - y_min
    x_range = x_max - x_min
    # create the positive return line
    N = 31
    positive_return_line_x = [x_min + (_ / (N - 1)) * x_range for _ in range(N)]
    positive_return_line_y = [0.0 for _ in range(N)]
    # plot the positive return line
    plt.plot(positive_return_line_x, positive_return_line_y,
             "r_", label=third_legend_label)
    text_x_pos, text_y_pos = (x_min + 1.005 * x_range, y_min + 0.5 * y_range)
    r_squared = r_value * r_value
    # display the r^2 value text
    plt.text(text_x_pos, text_y_pos, r"$r^{2}=$" + "{:.2f}".format(r_squared))
    # display the legend in the upper left
    plt.legend(
        [first_legend_label, second_legend_label, third_legend_label],
        loc=2)
    # annotate the data points
    for label, _x, _y in zip(collected_folder_names, x, y):
        plt.annotate(
            label,
            xy = (_x, _y),
            xytext = (-15, 0),
            textcoords = "offset points",
            ha = "right",
            va = "bottom",
            bbox = dict(boxstyle = "round,pad=0.5", fc = "yellow", alpha = 0.5),
            #arrowprops = dict(arrowstyle = "->", connectionstyle = "arc3,rad=0")
        )
    # and finally, show the whole thing
    plt.show()

def main():
    # get the time (this will be used to eventually calculate total run time)
    start_time = time.time()

    # get the current working directory
    cwd = os.getcwd()

    # determine if a folder exists called "training_data"
    if not os.path.isdir(os.path.join(cwd, "training_data")):
        print("There is no folder \"{}\"".format(
            os.path.join(cwd, "training_data")))
        sys.exit(1)
    training_path = os.path.join(cwd, "training_data")

    # get the folders
    folders = next(os.walk(training_path))[1]

    # go through each folder and get the results
    for folder_name in folders:
        # determine if delta.txt exists
        if not os.path.isfile(
                os.path.join(training_path, folder_name, "delta.txt")):
            print("Could not find delta.txt file in " + \
                  "\"training_data/{}\"".format(folder_name))
            continue
        delta_path = os.path.join(training_path, folder_name, "delta.txt")
        # get the closing prices from delta.txt
        with open(delta_path, "r") as delta_file:
            delta_lines = [line for line in delta_file]
            if not delta_lines:
                print("\"{}\" is not a valid delta file.".format(delta_path))
                continue
            delta_line = delta_lines[0]
            delta_data = delta_line.strip().split()
            if len(delta_data) != 2:
                print("\"{}\" is not a valid delta file.".format(delta_path))
                continue
            try:
                first_price = float(delta_data[0])
                second_price = float(delta_data[1])
            except ValueError:
                print("\"{}\" is not a valid delta file.".format(delta_path))
                continue
            percent_delta = (second_price - first_price) / first_price

            # but before we store the percent delta, make sure we can gather
            # information from results.txt

            # so determine if results.txt exists
            if not os.path.isfile(
                    os.path.join(training_path, folder_name, "results.txt")):
                print("Could not find results.txt file in " + \
                      "\"training_data/{}\"".format(folder_name))
                continue
            results_path = os.path.join(
                training_path, folder_name, "results.txt")
            # get the negative and positive scores from results.txt
            with open(results_path, "r") as results_file:
                results_lines = [line for line in results_file]
                if not results_lines:
                    print("\"{}\" is not a valid results file.".format(
                        results_path))
                    continue
                results_line = results_lines[0]
                results_data = results_line.strip().split()
                if len(results_data) != 2:
                    print("\"{}\" is not a valid results file.".format(
                        results_path))
                    continue
                try:
                    negative_score = float(results_data[0])
                    positive_score = float(results_data[1])
                except ValueError:
                    print("\"{}\" is not a valid results file.".format(
                        results_path))
                    continue

            # Now that we have everything we want
            collected_percent_deltas[folder_name] = percent_delta
            collected_negative_scores[folder_name] = negative_score
            collected_positive_scores[folder_name] = positive_score

        # We did it!
        collected_folder_names.append(folder_name)
        print("Successfully gathered data from \"training_path/{}\"".format(
            folder_name))
    
    # put our data into numpy arrays
    percent_deltas = np.array(list(collected_percent_deltas.values()))
    negative_scores = np.array(list(collected_negative_scores.values()))
    positive_scores = np.array(list(collected_positive_scores.values()))
    diff_scores = np.subtract(positive_scores, negative_scores)
    
    # print out the total run time
    time_delta = time.time() - start_time
    print("SUCCESS! Total run time: {:.2f} seconds".format(time_delta))

    # plot our data
    plot(negative_scores, percent_deltas, "Negative Scores", "Percent Deltas")
    plot(positive_scores, percent_deltas, "Positive Scores", "Percent Deltas")
    plot(diff_scores, percent_deltas, "Difference Scores", "Percent Deltas")
    
if __name__ == "__main__":
    main()
