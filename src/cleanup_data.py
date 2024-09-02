import json
import os
import tkinter as tk
from tkinter import filedialog as fd
import datetime as dt


def rename_keys(data: dict) -> dict:
    new_dict = dict()
    for key in data.keys():
        values = list(data[key].values())
        new_dict[key] = {str(i + 1): value for i, value in enumerate(values)}
    return new_dict


def cleanup_json(original_path: str, cleaned_path: str, last_date: dt.datetime):
    keys = [
        "L1_avg_power_factor",
        "L1_min_power_factor",
        "L1_max_power_factor",
        "L2_avg_power_factor",
        "L2_min_power_factor",
        "L2_max_power_factor",
        "L3_avg_power_factor",
        "L3_min_power_factor",
        "L3_max_power_factor",
        "Total measurement count",
        "L1_avg_voltage",
        "L1_max_voltage",
        "L1_min_voltage",
        "L1_avg_current",
        "L1_max_current",
        "L1_min_current",
        "L2_avg_voltage",
        "L2_max_voltage",
        "L2_min_voltage",
        "L2_avg_current",
        "L2_max_current",
        "L2_min_current",
        "L3_avg_voltage",
        "L3_max_voltage",
        "L3_min_voltage",
        "Timestamp of first measurement",
        "L3_avg_current",
        "L3_max_current",
        "L3_min_current",
        "Sensor ID",
        "iso_day",
        "iso_month",
    ]
    with open(original_path, "r") as f:
        data = json.load(f)

    # don't store an empty dataframe again
    if not data:
        return

    type = list(data["Device"].values())[0]
    # do not use emobility
    if type == "eMob":
        return

    for key in keys:
        data.pop(key, None)

    keys_to_delete = [
        key
        for key, date in data["Timestamp"].items()
        if dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S") < last_date
    ]
    if keys_to_delete:
        for key in data.keys():
            for key_to_delete in keys_to_delete:
                data[key].pop(key_to_delete, None)

    if type == "Heatpump" or type == "Add.Heating":
        keys_heatpump = [
            key for key, device in data["Device"].items() if device == "Heatpump"
        ]
        data_heatpump = dict()
        for key in data.keys():
            data_heatpump[key] = dict()

        for key in data.keys():
            for key_heatpump in keys_heatpump:
                data_heatpump[key][key_heatpump] = data[key][key_heatpump]
                data[key].pop(key_heatpump, None)

        name, ending = cleaned_path.split(".", 1)
        filename_heatpump = name + "_heatpump.json"
        filename_add_heat = name + "_add_heat.json"
        # make shure it is not empty
        if "Device" in data_heatpump.keys() and data_heatpump["Device"]:
            with open(filename_heatpump, "w") as f:
                json_str = json.dumps(rename_keys(data_heatpump), indent=4)
                f.write(json_str)

        # make shure it is not empty
        if "Device" in data.keys() and data["Device"]:
            with open(filename_add_heat, "w") as f:
                json_str = json.dumps(rename_keys(data), indent=4)
                f.write(json_str)
        return

    # make shure it is not empty
    if "Device" in data.keys() and data["Device"]:
        with open(cleaned_path, "w") as f:
            json_str = json.dumps(rename_keys(data), indent=4)
            f.write(json_str)


def get_filelist() -> list:
    """
    Function to get a list of all json files one wants to include in an analysis.
    You have to have already created a directory and included all necessary json files before calling this function.
    """

    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    directory_path = fd.askdirectory()
    os.makedirs(directory_path + "_cleaned", exist_ok=True)

    filenames = os.listdir(directory_path)
    filenames = [file for file in filenames if file.endswith(".json")]

    return [
        (directory_path + "/" + filename, directory_path + "_cleaned/" + filename)
        for filename in filenames
    ]


if __name__ == "__main__":
    filelist_to_get_and_store = get_filelist()
    last_date = dt.datetime(year=2024, month=8, day=28)
    for i, (original_file, cleaned_file) in enumerate(filelist_to_get_and_store):
        cleanup_json(original_file, cleaned_file, last_date)
        print(f"{int(float(i * 100) / len(filelist_to_get_and_store))}% done")
