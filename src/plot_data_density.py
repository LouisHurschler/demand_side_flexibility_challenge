import math
import tkinter as tk
from tkinter import filedialog as fd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import datetime as dt
import numpy as np
import json
import os
from collections import OrderedDict
import re


def extract_four_digits(filename):
    # Define the regex pattern to match exactly four digits before ".json"
    pattern = r"(\d{4})"

    # Use re.search to find the pattern in the filename
    match = re.search(pattern, filename)

    # Check if a match was found
    if match:
        # Extract and return the four-digit number
        return int(match.group(1))
    else:
        return None


def get_filelist() -> list:
    """
    Function to get a list of all json files one wants to include in an analysis.
    You have to have already created a directory and included all neccesairy json files before calling this function.
    """

    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    path_enflate_data = fd.askdirectory()

    filenames = os.listdir(path_enflate_data)
    filenames = [file for file in filenames if file.endswith(".json")]

    return [path_enflate_data + "/" + filename for filename in filenames]


def plot_directly_from_data():
    filelist = get_filelist()
    plt.figure(figsize=(20, 8))
    IDs = dict()

    for i, file in enumerate(filelist):
        with open(file) as f:
            data = json.load(f)

        # do not look at this data if it is empty
        if not data:
            continue

        times = list(data["Timestamp"].values())
        times = sorted(times)
        dt_times = [dt.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") for time in times]
        begin = dt_times[0]
        end = dt_times[-1]
        duration = end - begin
        total_hours = math.ceil(duration.total_seconds() / 3600.0)

        amount_of_data = [0] * total_hours

        for date in dt_times:
            data_idx = int((date - begin).total_seconds() / 3600.0)
            amount_of_data[data_idx] += 1

        dates = begin + dt.timedelta(hours=1) * np.linspace(
            0, len(amount_of_data) - 1, num=len(amount_of_data)
        )
        IDs[i] = extract_four_digits(file)

        y_values = np.ones(len(dates)) * i

        points = plt.scatter(
            x=dates,
            y=y_values,
            c=amount_of_data,
            s=1,
            cmap="Blues",
            marker="s",
        )

        print(f"file {file} read successfully! {int(i * 100 / len(filelist))}% done")

    plt.title("overview of data density")

    # plot additional information
    x_lim = plt.gca().get_xlim()[1]

    for height, value in IDs.items():
        plt.text(
            x_lim - 1,
            height,
            str(value),
            fontsize=6,
            ha="right",
            va="center",
            color="red",
        )
    plt.colorbar(points, label="#points per hour")

    plt.yticks([])

    plt.xlabel("Date")
    # plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
    # This trick removes multiple same labels
    # handles, labels = plt.gca().get_legend_handles_labels()
    # by_label = OrderedDict(zip(labels, handles))
    # plt.legend(by_label.values(), by_label.keys(), markerscale=10.0)

    # plt.show()
    plt.savefig("../plots/data_density.png", dpi=600)


if __name__ == "__main__":
    # plot_distribution_from_results()
    plot_directly_from_data()
