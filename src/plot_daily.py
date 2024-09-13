# start at 12.08. to 09.08.
import tkinter as tk
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import numpy as np
import pandas as pd
import json
import re
import os


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


def plot_data(path: str, specific_dates: list, weekday: str):

    plt.figure(figsize=(8, 4))

    fig, axs = plt.subplots(len(specific_dates), 1, figsize=(10, 8), sharex=True)
    data = pd.read_json(path)

    # Helper function to convert time to seconds since midnight
    def time_to_seconds(time):
        return time.hour * 3600 + time.minute * 60 + time.second

    max_data = 0
    for i, specific_date in enumerate(specific_dates):
        data_tmp = data[
            data["Timestamp"].dt.date == pd.to_datetime(specific_date).date()
        ].copy()
        if data_tmp.empty:
            continue

        data_tmp["time_in_seconds"] = data_tmp["Timestamp"].dt.time.apply(
            time_to_seconds
        )
        energy_from_current_and_voltage = (
            abs(
                data_tmp["L1_avg_current"]
                * data_tmp["L1_avg_voltage"]
                * data_tmp["L1_avg_power_factor"]
            )
            + abs(
                data_tmp["L2_avg_current"]
                * data_tmp["L2_avg_voltage"]
                * data_tmp["L2_avg_power_factor"]
            )
            + abs(
                data_tmp["L3_avg_current"]
                * data_tmp["L3_avg_voltage"]
                * data_tmp["L3_avg_power_factor"]
            )
        )
        max_value_energy = max(energy_from_current_and_voltage)

        start_time = dt.datetime(1970, 1, 1)
        time_list = [
            start_time + dt.timedelta(seconds=time)
            for time in data_tmp["time_in_seconds"]
        ]

        scaling = 1e-12
        axs[i].fill_between(
            time_list,
            (1.0 - data_tmp["relay_state"]) * max_value_energy * scaling,
            color="red",
            label="relay off",
            alpha=0.2,
        )
        axs[i].plot(
            time_list,
            energy_from_current_and_voltage * scaling,
            color="blue",
            label="energy",
        )

    # Set x-axis to show time in hh:mm:ss
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

    plt.gcf().autofmt_xdate()
    four_digits = extract_four_digits(path)
    plt.legend()
    plt.savefig("../plots/plot_" + weekday + "_site_" + str(four_digits) + ".png")


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
    filenames = [
        file
        for file in filenames
        if file.endswith(".json") and not file.endswith("heat.json")
    ]

    return [directory_path + "/" + filename for filename in filenames]


if __name__ == "__main__":
    # "energyall files
    files = get_filelist()
    specific_dates_monday = [
        "2024-08-12",
        "2024-08-19",
        "2024-08-26",
        "2024-09-02",
        "2024-09-09",
    ]
    specific_dates_tuesday = [
        "2024-08-13",
        "2024-08-20",
        "2024-08-27",
        "2024-09-03",
        "2024-09-10",
    ]
    specific_dates_wednesday = [
        "2024-08-14",
        "2024-08-21",
        "2024-08-28",
        "2024-09-04",
        "2024-09-11",
    ]
    specific_dates_thursday = [
        "2024-08-15",
        "2024-08-22",
        "2024-08-29",
        "2024-09-05",
    ]
    specific_dates_friday = [
        "2024-08-16",
        "2024-08-23",
        "2024-08-30",
        "2024-09-06",
    ]
    specific_dates_saturday = [
        "2024-08-17",
        "2024-08-24",
        "2024-08-31",
        "2024-09-07",
    ]
    specific_dates_sunday = [
        "2024-08-18",
        "2024-08-25",
        "2024-09-01",
        "2024-09-08",
    ]

    for file in files:
        plot_data(file, specific_dates_monday, "monday")
        plot_data(file, specific_dates_tuesday, "tuesday")
        plot_data(file, specific_dates_wednesday, "wednesday")
        plot_data(file, specific_dates_thursday, "thursday")
        plot_data(file, specific_dates_friday, "friday")
        plot_data(file, specific_dates_saturday, "saturday")
        plot_data(file, specific_dates_sunday, "sunday")
        print(f"file {file} plotted!")
