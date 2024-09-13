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


def add_overview_of_signs(data: dict, i: int):

    # currents under 1000 milliampere are just fluctuations
    threshold_active = 1000

    mask_energy_active = [
        data["L1_avg_current"][idx]
        + data["L2_avg_current"][idx]
        + data["L3_avg_current"][idx]
        > threshold_active
        for idx in data["relay_state"].keys()
    ]
    is_active = any(mask_energy_active)

    first_key = list(data["L1_active_energy"].keys())[0]
    last_key = list(data["L1_active_energy"].keys())[-1]
    active_energy_difference = [
        data["L1_active_energy"][last_key] - data["L1_active_energy"][first_key],
        data["L2_active_energy"][last_key] - data["L2_active_energy"][first_key],
        data["L3_active_energy"][last_key] - data["L3_active_energy"][first_key],
    ]
    linewidth = "5"
    if is_active:
        if active_energy_difference[0] * data["L1_min_power_factor"]["0"] > 0:
            color = "green"
        else:
            color = "red"
        plt.plot([1, 2], [i, i], color=color, linewidth=linewidth)
        if active_energy_difference[1] * data["L2_min_power_factor"]["0"] > 0:
            color = "green"
        else:
            color = "red"
        plt.plot([2, 3], [i, i], color=color, linewidth=linewidth)
        if active_energy_difference[2] * data["L3_min_power_factor"]["0"] > 0:
            color = "green"
        else:
            color = "red"
        plt.plot([3, 4], [i, i], color=color, linewidth=linewidth)
    else:
        plt.plot([1, 4], [i, i], label="not running", color="grey", linewidth=linewidth)


def add_energy_values_comparison(data: dict, i: int):
    x_values = np.array(list(data["Timestamp"].values()))

    threshold_active = (
        np.mean(list(data["L1_active_energy_diff"].values()))
        + np.mean(list(data["L2_active_energy_diff"].values()))
        + np.mean(list(data["L3_active_energy_diff"].values()))
    ) / 3.0 + 1.0

    mask_energy_active = [
        data["L1_active_energy_diff"][idx]
        + data["L2_active_energy_diff"][idx]
        + data["L3_active_energy_diff"][idx]
        > threshold_active
        for idx in data["relay_state"].keys()
    ]

    energy_values = [
        data["L1_active_energy_diff"][idx]
        + data["L2_active_energy_diff"][idx]
        + data["L3_active_energy_diff"][idx]
        for idx in data["L1_active_energy_diff"].keys()
    ]

    x_values_dates = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S") for x_value in x_values[:]
    ]
    y_values = np.ones(len(x_values_dates)) * i

    mask_relay = [data["relay_state"][idx] == 1 for idx in data["relay_state"].keys()]

    devie_type = list(data["Device"].values())[0]
    if devie_type == "Boiler":
        color_on_energy = "blue"
        color_off_energy = "lightblue"
        label = "Boiler"

    elif devie_type == "Heatpump":
        color_on_energy = "darkred"
        color_off_energy = "orange"
        label = "Heatpump"

    elif devie_type == "Add.Heating":
        color_on_energy = "purple"
        color_off_energy = "pink"
        label = "Additional Heating"

    else:
        color_on_energy = "k"
        color_off_energy = "k"
        label = devie_type

    color_on_relay = "green"
    color_off_relay = "red"

    x_values_on_energy = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S")
        for x_value in x_values[mask_energy_active]
    ]
    x_values_off_energy = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S")
        for x_value in x_values[np.invert(mask_energy_active)]
    ]

    x_values_on_relay = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S")
        for x_value in x_values[mask_relay]
    ]
    x_values_off_relay = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S")
        for x_value in x_values[np.invert(mask_relay)]
    ]

    # choose following y_value to group values together which started arount the same time
    y_values_on_energy = np.ones(len(x_values[mask_energy_active])) * (2 * i + 1)
    y_values_off_energy = np.ones(len(x_values[np.invert(mask_energy_active)])) * (
        2 * i + 1
    )
    y_values_on_relay = np.ones(len(x_values[mask_relay])) * 2 * i
    y_values_off_relay = np.ones(len(x_values[np.invert(mask_relay)])) * 2 * i

    plt.plot(
        x_values_off_relay,
        y_values_off_relay,
        linestyle="None",
        marker=".",
        color=color_off_relay,
        label=label + " relay off",
        markersize=1,
    )
    plt.plot(
        x_values_on_relay,
        y_values_on_relay,
        linestyle="None",
        marker=".",
        color=color_on_relay,
        label=label + " relay on",
        markersize=1,
    )
    # plt.plot(
    #     x_values_off_energy,
    #     y_values_off_energy,
    #     linestyle="None",
    #     marker=".",
    #     color=color_off_energy,
    #     label="active energy low",
    #     markersize=1,
    # )
    # plt.plot(
    #     x_values_on_energy,
    #     y_values_on_energy,
    #     linestyle="None",
    #     marker=".",
    #     color=color_on_energy,
    #     label="active energy high",
    #     markersize=1,
    # )


def plot_distribution_from_results():
    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    path_json_data = fd.askopenfilename()
    with open(path_json_data) as f:
        data = json.load(f)

    plt.figure(figsize=(20, 8))
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))

    for datapoint in data.keys():
        # do not plot if empty
        end_date = dt.datetime(2024, 9, 2)
        start_date = end_date - dt.timedelta(days=len(data[datapoint]))
        days = np.flip(mdates.drange(start_date, end_date, dt.timedelta(days=1)))
        data_to_plot = list(data[datapoint].values())
        # do not plot empty data
        if sum(data_to_plot) == 0:
            continue
        match datapoint:
            case "boilers":
                label = "Boilers"
            case "heatpumps":
                label = "Heatpumps"
            case "Add.heatings":
                label = "Additional Heatings"
            case _:
                label = datapoint

        plt.plot(days, data_to_plot, label=label)

    plt.gcf().autofmt_xdate()

    # plt.gcf().autofmt_xdate()
    plt.title("Amount of data gathered at each day")
    plt.ylabel("#Datapoints")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True)
    plt.savefig("../plots/data_distribution.png", dpi=500, transparent=True)


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

        add_overview_of_signs(data, i)
        # add_energy_values_comparison(data, i)

        IDs[i] = extract_four_digits(file)
        print(f"file {file} read successfully! {int(i * 100 / len(filelist))}% done")

    plt.title("overviews of sign of energy")

    # plot additional information
    x_lim = plt.gca().get_xlim()[1]

    for height, value in IDs.items():
        plt.text(
            x_lim - 0.05,
            height,
            str(value),
            fontsize=6,
            ha="right",
            va="center",
            color="red",
        )

    x = [1.5, 2.5, 3.5]
    x_labels = ["L1", "L2", "L3"]
    plt.xticks(x, x_labels)
    plt.yticks([])
    handles = [
        mpatches.Patch(color="red", label="negative sign"),
        mpatches.Patch(color="green", label="positive sign"),
        mpatches.Patch(color="grey", label="no current"),
    ]
    plt.legend(handles=handles)

    # plt.xlabel("Date")
    # plt.grid(True)
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
    # # This trick removes multiple same labels
    # handles, labels = plt.gca().get_legend_handles_labels()
    # by_label = OrderedDict(zip(labels, handles))
    # plt.legend(by_label.values(), by_label.keys(), markerscale=10.0)

    # plt.show()
    plt.savefig("../plots/data_distribution_signs.png", dpi=300)


if __name__ == "__main__":
    # plot_distribution_from_results()
    plot_directly_from_data()
