import tkinter as tk
from tkinter import filedialog as fd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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


def plot_distribution_from_results():
    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    path_json_data = fd.askopenfilename()
    with open(path_json_data) as f:
        data = json.load(f)

    plt.figure(figsize=(10, 6))
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    for datapoint in data.keys():
        # do not plot if empty
        days = -np.linspace(0, len(data[datapoint]), len(data[datapoint]))
        data_to_plot = list(data[datapoint].values())
        # do not plot empty data
        if sum(data_to_plot) == 0:
            continue
        plt.plot(days, data_to_plot, label=datapoint)

    # plt.gcf().autofmt_xdate()
    plt.title("Plot amount of data gathered at each day")
    plt.ylabel("#Datapoints")
    plt.xlabel("Days")
    plt.legend()
    plt.grid(True)
    plt.savefig("plots/data_distribution.pdf")


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
        x_values = np.array(list(data["Timestamp"].values()))

        # mean_app_energy = (
        #     sum(data["L1_app_energy"].values())
        #     + sum(data["L2_app_energy"].values())
        #     + sum(data["L3_app_energy"].values())
        # ) / len(data["L1_app_energy"])
        threshold_on = 1

        mask_energy = [
            data["relay_state"][idx] == threshold_on
            for idx in data["relay_state"].keys()
        ]

        type = list(data["Device"].values())[0]
        if type == "Boiler":
            color_on = "darkblue"
            color_off = "lightblue"
            label = "Boiler"

        elif type == "Heatpump":
            color_on = "darkred"
            color_off = "orange"
            label = "Heatpump"

        elif type == "Add.Heating":
            color_on = "purple"
            color_off = "pink"
            label = "Additional Heating"

        else:
            color_on = "k"
            color_off = "k"
            label = type

        x_values_on = [
            dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S")
            for x_value in x_values[mask_energy]
        ]
        x_values_off = [
            dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S")
            for x_value in x_values[np.invert(mask_energy)]
        ]

        # choose following y_value to group values together which started arount the same time
        # y_values = np.ones(len(x_values)) * int(min(x_values).strftime('%M%d'))
        y_values_on = np.ones(len(x_values[mask_energy])) * i
        y_values_off = np.ones(len(x_values[np.invert(mask_energy)])) * i
        IDs[i] = extract_four_digits(file)
        plt.plot(
            x_values_on,
            y_values_on,
            linestyle="None",
            marker=".",
            color=color_on,
            label=label + " on",
            markersize=1,
        )
        plt.plot(
            x_values_off,
            y_values_off,
            linestyle="None",
            marker=".",
            color=color_off,
            label=label + " off",
            markersize=1,
        )
        print(f"file {file} read successfully! {int(i * 100 / len(filelist))}% done")
    plt.title("Amount of data gathered at each day")
    plt.xlabel("Date")
    # plt.grid(True)

    # plot additional information
    x_lim = plt.gca().get_xlim()[1]

    for height, value in IDs.items():
        plt.text(
            x_lim - 0.5,
            height,
            str(value),
            fontsize=6,
            ha="right",
            va="center",
            color="red",
        )

    # This trick removes multiple same labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), markerscale=5.0)

    # plt.show()
    plt.savefig(
        "../plots/data_distribution_from_data_conditional_relay_on.png", dpi=300
    )


if __name__ == "__main__":
    # plot_distribution_from_results()
    plot_directly_from_data()
