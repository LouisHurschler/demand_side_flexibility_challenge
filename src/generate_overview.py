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
    for i, file in enumerate(filelist):
        with open(file) as f:
            data = json.load(f)

        # do not look at this data if it is empty
        if not data:
            continue
        x_values = data["Timestamp"].values()

        type = list(data["Device"].values())[0]
        if type == "Boiler":
            color = "b"
            label = "Boiler"
        elif type == "Heatpump" or type == "Add.Heating":
            color = "r"
            label = "Heatpump"
        else:
            color = "k"
            label = type
        x_values = [
            dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S") for x_value in x_values
        ]
        # choose following y_value to group values together which started arount the same time
        # y_values = np.ones(len(x_values)) * int(min(x_values).strftime('%M%d'))
        y_values = np.ones(len(x_values)) * i
        plt.plot(
            x_values, y_values, linestyle="None", marker=".", color=color, label=label
        )
        print(f"file {file} read successfully! {int(i * 100 / len(filelist))}% done")
    plt.title("Plot amount of data gathered at each day")
    plt.xlabel("Days")
    plt.grid(True)

    # This trick removes multiple same labels
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    # plt.show()
    plt.savefig("plots/data_distribution_from_data_original.png")


if __name__ == "__main__":
    plot_distribution_from_results()
    # plot_directly_from_data()
