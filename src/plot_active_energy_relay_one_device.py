import tkinter as tk
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import json
import re
import os


def normalize(values: list) -> list:
    max_value = max(values)
    return [value / float(max_value) for value in values]


# "flatten" the curve to get more visually appealing results
def get_running_mean(values: list, influence_range: int) -> list:
    res = [0] * len(values)

    # first and last part
    for i in range(influence_range):
        res[i] = sum([values[j] for j in range(i + influence_range + 1)]) / float(
            i + influence_range + 1
        )
        res[len(values) - i - 1] = sum(
            [
                values[j]
                for j in range(len(values) - influence_range - i - 1, len(values))
            ]
        ) / float(i + influence_range + 1)

    for i in range(influence_range, len(values) - influence_range):
        res[i] = sum(
            [values[j] for j in range(i - influence_range, i + influence_range + 1)]
        ) / float(2 * influence_range + 1)

    return res


# extract the four digits at the end of the filename
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


def plot_data(path: str):

    with open(path) as f:
        data = json.load(f)

    site_number = extract_four_digits(path)

    plt.figure(figsize=(8, 4))
    # use diff values because other values store the absolute values
    # multiply by 0.012 to get kW (units are 0.1Wh/30 sec)
    active_energy_values = [
        (
            data["L1_active_energy_diff"][idx]
            + data["L2_active_energy_diff"][idx]
            + data["L3_active_energy_diff"][idx]
        )
        * 0.012
        for idx in data["L1_active_energy_diff"].keys()
    ]

    # if influence_range=0, no running mean is calculated
    active_energy_values_running_mean = get_running_mean(
        active_energy_values, influence_range=0
    )
    max_value = max(active_energy_values_running_mean)

    # convert strings of timestamps to datetime objects for plotting
    x_values = np.array(list(data["Timestamp"].values()))
    x_values_dates = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S") for x_value in x_values
    ]

    data_relay = [
        max_value * relay_state for relay_state in data["relay_state"].values()
    ]

    # plt.plot(
    #     x_values_dates,
    #     data_relay,
    #     marker=".",
    #     color="0.8",
    #     label="relay state",
    #     markersize=1.0,
    # )
    plt.fill_between(x_values_dates, 0.0, data_relay, color="grey", label="relay on")
    plt.plot(
        x_values_dates,
        active_energy_values_running_mean,
        marker=".",
        color="r",
        label="sum of active energy",
        markersize=1.0,
    )
    plt.fill_between(x_values_dates, 0.0, active_energy_values_running_mean, color="r")

    plt.title("Active Energy vs. relay state site " + str(site_number))
    plt.ylabel("power [kW]")
    plt.xlabel("Date")
    plt.legend(markerscale=10.0)

    plt.margins(y=0)
    plt.savefig(
        "../plots/active_energy_vs_relay_site_" + str(site_number) + ".png",
        dpi=500,
        transparent=True,
    )


def get_filelist() -> list:
    """
    Function to get a list of all json files one wants to include in an analysis.
    You have to have already created a directory and included all necessary json files before calling this function.
    """

    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    directory_path = fd.askdirectory()

    filenames = os.listdir(directory_path)
    filenames = [file for file in filenames if file.endswith(".json") and not file.endswith("heat.json")]

    return [directory_path + "/" + filename for filename in filenames]


if __name__ == "__main__":
    # plot one file
    root = tk.Tk()
    root.withdraw()
    print("select the path of the file where the json data is stored")
    path_enflate_data = fd.askopenfilename()

    plot_data(path_enflate_data)

    # # plot all files
    # files = get_filelist()
    # for file in files:
    #     plot_data(file)
