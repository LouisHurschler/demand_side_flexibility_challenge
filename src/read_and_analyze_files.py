import json
import os
import tkinter as tk
from tkinter import filedialog as fd
from datetime import date, datetime
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import math


def add_trace(
    fig: go.Figure,
    df: pd.DataFrame,
    size: int,
    information_to_plot: list,
    name_plot: str,
    mask: list = None,
):
    """
    Function to add traces to the plots. If you include a mask (list of binary values),
    it will only plot the datapoints where this mask is set to True.
    This enables to plot data dependent of other data.
    """
    if df.empty or "Timestamp" not in df.keys():
        return

    if mask is None:
        mask = [True] * size
    else:
        mask = mask[0:size]

    for name in information_to_plot:
        # only plot numeric data
        if type(df[name].iloc[0]) is not str:
            fig.add_trace(
                go.Scattergl(
                    x=df["Timestamp"][0:size][mask],
                    y=df[name][0:size][mask],
                    name=name + name_plot,
                    mode="markers",
                    line=dict(width=1),
                    marker=dict(size=6, opacity=0.15),
                )
            )


def get_last_timestamp(members: list) -> int:
    """
    Funciton to get the last timestep of all members in members.
    All member DataFrames have to be sorted in descending order with respect to the
    "Timestamp of last measurement" entry beforehand.
    """
    last_timestamp = 0
    for member in members:
        if not member.empty:
            last_timestamp = max(
                last_timestamp, member["Timestamp of last measurement"].iloc[0]
            )
    return last_timestamp


def get_first_timestamp(members: list) -> int:
    """
    Funciton to get the last timestep of all members in members.
    All member DataFrames have to be sorted in descending order with respect to the
    "Timestamp of last measurement" entry beforehand.
    """
    # Timestamp in the future (2038)
    last_timestamp = 2147483647
    for member in members:
        if not member.empty:
            last_timestamp = min(
                last_timestamp,
                member["Timestamp of last measurement"].iloc[len(member) - 1],
            )
    assert (
        last_timestamp != 2147483647
    ), "default value did not change! check get_first_timestamp"
    return last_timestamp


class EnflateData:
    """
    Main class to store and analyze the enflate data
    """

    def __init__(self, list_files: list):
        """
        Function to read all data, sort them according to the timestamps,
        and calculate the amount of datapoints of each day
        """
        print("starting with reading and sorting data")
        boilers_list = []
        heatpumps_list = []
        emob_list = []
        other_list = []

        for file in list_files:
            with open(file) as f:
                data = pd.DataFrame(json.load(f))
                device_type = data["Device"]["0"]

                match device_type:
                    case "Boiler":
                        boilers_list.append(data)

                    case "Heatpump" | "Add.Heating":
                        heatpumps_list.append(data)

                    case "eMob":
                        emob_list.append(data)

                    case _:
                        print(f"ERROR: device detected of type {device_type}")
                        other_list.append(data)
                print(f"file {file} read")

        print("data read")

        # preprocess data to be stored in a sorted pd.DataFrame per frequency
        if len(boilers_list) != 0:
            self.boilers = pd.concat(boilers_list)
            print("start sorting boilers")
            self.boilers.sort_values(
                by="Timestamp of last measurement", ascending=False, inplace=True
            )
            print("boilers sorted")
        else:
            self.boilers = pd.DataFrame()

        if len(heatpumps_list) != 0:
            self.heatpumps = pd.concat(heatpumps_list)
            print("start sorting heatpumps")
            self.heatpumps.sort_values(
                by="Timestamp of last measurement", ascending=False, inplace=True
            )
            print("heatpumps sorted")
        else:
            self.heatpumps = pd.DataFrame()

        if len(emob_list) != 0:
            self.emob = pd.concat(emob_list)
            print("start sorting emob")
            self.emob.sort_values(
                by="Timestamp of last measurement", ascending=False, inplace=True
            )
            print("emob sorted")
        else:
            self.emob = pd.DataFrame()

        if len(other_list) != 0:
            self.other = pd.concat(other_list)
            print("start sorting others")
            self.other.sort_values(
                by="Timestamp of last measurement", ascending=False, inplace=True
            )
            print("others sorted")
        else:
            self.other = pd.DataFrame()

        print("data read and sorted")
        print("count number of datapoints per day")

        last_timestamp = get_last_timestamp(
            [self.boilers, self.heatpumps, self.emob, self.other]
        )
        first_timestamp = get_first_timestamp(
            [self.boilers, self.heatpumps, self.emob, self.other]
        )
        day = 60 * 60 * 24
        max_days = math.ceil((last_timestamp - first_timestamp) / day)

        # Precompute the `curr_last_timestamp` values for each day
        timestamps = last_timestamp - np.arange(1, max_days + 1) * day

        # Initialize the result DataFrame
        self.datapoints_per_day = pd.DataFrame(
            {
                "boilers": np.zeros(max_days, dtype=int),
                "heatpumps": np.zeros(max_days, dtype=int),
                "emob": np.zeros(max_days, dtype=int),
                "other": np.zeros(max_days, dtype=int),
            }
        )

        # this function counts the datapoints in a timeframe by calculating the indexes of each days
        # and returning it's defferences
        def count_datapoints(data, timestamps):
            # use the minus sign because searchsorted is only implemented for ascending datasets
            idxs = np.searchsorted(
                -data["Timestamp of last measurement"].values, -timestamps, side="left"
            )
            return np.diff(np.append(0, idxs))

        if not self.boilers.empty:
            self.datapoints_per_day["boilers"] = count_datapoints(
                self.boilers, timestamps
            )
        if not self.heatpumps.empty:
            self.datapoints_per_day["heatpumps"] = count_datapoints(
                self.heatpumps, timestamps
            )
        if not self.emob.empty:
            self.datapoints_per_day["emob"] = count_datapoints(self.emob, timestamps)
        if not self.other.empty:
            self.datapoints_per_day["other"] = count_datapoints(self.other, timestamps)

    def print_info(self):
        """
        Function to print information of current dataset
        """
        print(f"amount of boiler datapoints: {len(self.boilers)}")
        print(f"amount of heatpump datapoints: {len(self.heatpumps)}")
        print(f"amount of emob datapoints: {len(self.emob)}")
        print(f"amount of other datapoints: {len(self.other)}")

        print("Boilers data: ")
        print(self.boilers)
        print("Heatpumps data: ")
        print(self.heatpumps)
        print("Emob data: ")
        print(self.emob)
        print("other data: ")
        print(self.other)

    def plot_data(self, days=1):
        """
        This function aims to plot interesting data in the range [most_current_data - days, most_current_data]
        """
        print("start plotting now")
        members_dict = {
            "boilers": self.boilers,
            "heatpumps": self.heatpumps,
            "emob": self.emob,
            "other": self.other,
        }

        fig = go.Figure()
        information_to_plot = [
            # "L1_avg_power_factor",
            # "L2_avg_power_factor",
            # "L3_avg_power_factor",
            # "L1_avg_voltage",
            # "L2_avg_voltage",
            # "L3_avg_voltage",
            # "L1_avg_current",
            # "L2_avg_current",
            # "L3_avg_current",
            # "relay_state"
            "L1_app_energy",
            "L2_app_energy",
            "L3_app_energy",
        ]
        # information_to_plot = self.boilers.keys()
        # print(information_to_plot)

        # Add interesting traces to the plot
        for member in members_dict.keys():
            if len(members_dict[member]) != 0:
                add_trace(
                    fig=fig,
                    df=members_dict[member],
                    size=sum(self.datapoints_per_day[member][0:days]),
                    information_to_plot=information_to_plot,
                    name_plot="_" + member,
                )
                add_trace(
                    fig=fig,
                    df=members_dict[member],
                    size=sum(self.datapoints_per_day[member][0:days]),
                    information_to_plot=information_to_plot,
                    name_plot="_plot_only_relay_1" + member,
                    mask=[id == 1 for id in members_dict[member]["relay_state"]],
                )
                add_trace(
                    fig=fig,
                    df=members_dict[member],
                    size=sum(self.datapoints_per_day[member][0:days]),
                    information_to_plot=information_to_plot,
                    name_plot="_plot_only_relay_0" + member,
                    mask=[id == 0 for id in members_dict[member]["relay_state"]],
                )

                # add_trace(
                #     fig=fig,
                #     df=members_dict[member],
                #     len=sum(self.datapoints_per_day[member][0:days]),
                #     information_to_plot=information_to_plot,
                #     name_plot="_plot_only_30_sec_data_" + member,
                #     mask=[
                #         freq == "type_30_second"
                #         for freq in members_dict[member]["Frequency"]
                #     ],
                # )

                # add_trace(
                #     fig=fig,
                #     df=members_dict[member],
                #     len=sum(self.datapoints_per_day[member][0:days]),
                #     information_to_plot=information_to_plot,
                #     name_plot="_plot_only_15_min_data_" + member,
                #     mask=[
                #         freq == "type_15_min"
                #         for freq in members_dict[member]["Frequency"]
                #     ],
                # )

                # add_trace(
                #     fig=fig,
                #     df=members_dict[member],
                #     len=sum(self.datapoints_per_day[member][0:days]),
                #     information_to_plot=information_to_plot,
                #     name_plot="_plot_only_type_1_" + member,
                #     mask=[
                #         type == 1 for type in members_dict[member]["Measurement type"]
                #     ],
                # )
                # add_trace(
                #     fig=fig,
                #     df=members_dict[member],
                #     len=sum(self.datapoints_per_day[member][0:days]),
                #     information_to_plot=information_to_plot,
                #     name_plot="_plot_only_type_2_" + member,
                #     mask=[
                #         type == 2 for type in members_dict[member]["Measurement type"]
                #     ],
                # )

        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(count=1, label="1D", step="day", stepmode="backward"),
                            dict(count=7, label="1W", step="day", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(step="all", label="ALL"),
                        ]
                    )
                ),
                rangeslider=dict(visible=True),
                type="date",
            ),
            showlegend=True,
        )

        fig.show()

    def store_datapoints_per_day(self, filename):
        """
        Stores datapoints as json in the directory of filename.
        Make shure that the right relative path is used
        """
        with open(filename, "w") as f:
            f.write(self.datapoints_per_day.to_json(indent=4))


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


if __name__ == "__main__":

    list_files = get_filelist()
    data = EnflateData(
        list_files,
    )
    # data.print_info()
    data.plot_data(days=3)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # Make shure that the right relative path is used.
    # This works if you are calling this python script outside the python folder,
    # e.g. with python3 src/read_and_analyze_files.py
    data.store_datapoints_per_day(filename="../results/" + timestamp + ".json")
