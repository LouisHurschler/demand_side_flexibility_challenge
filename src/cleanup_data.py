import json
import os
import tkinter as tk
from tkinter import filedialog as fd
import datetime as dt


def sort_dict_according_to_timestamps(data: dict) -> dict:
    """
    Sorts all values of the data dictionary according to the date stored in the 'Timestamp'-dictionary.
    Note that afterwards the keys will not be sorted. Example:
    before: {
        data1 : {
            "1": 32,
            "2": 12,
            "3": -3,
        },
        Timestamp: {
            "1": "2023-06-05 12:23:06",
            "2": "2023-06-07 12:23:06",
            "3": "2023-06-05 12:23:05",
        }
    }

    afterwards: {
        data1 : {
            "3": -3,
            "1": 32,
            "2": 12,
        },
        Timestamp: {
            "3": "2023-06-05 12:23:05",
            "1": "2023-06-05 12:23:06",
            "2": "2023-06-07 12:23:06",
        },
    }
    """
    idx_list_sorted = sorted(
        data["Timestamp"].items(),
        key=lambda item: dt.datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S"),
    )
    data_new = {}
    for key in data.keys():
        data_new[key] = {}
        for idx, _val in idx_list_sorted:
            data_new[key][idx] = data[key][idx]
    return data_new


def sort_and_rename_keys(data: dict) -> dict:
    """
    reorder data sucht that they are sorted according to their timestamts
    and the keys are ints in ascending orders
    """

    new_dict = dict()
    data = sort_dict_according_to_timestamps(data)
    for key in data.keys():
        values = list(data[key].values())
        new_dict[key] = {str(i + 1): value for i, value in enumerate(values)}
    return new_dict


def add_difference(data: dict, difference_list: list) -> dict:
    """
    Adds the difference of all members in difference_list to a new dictionary.
    The value of posiiton 0 will be 0.0, otherwise the value of position i will
    be the original value of position i minus the original value of position i-1
    """
    data = sort_and_rename_keys(data)
    for name_difference in difference_list:
        values = list(data[name_difference].values())
        size = len(values)
        diff = [0.0] + [
            abs(value2 - value1)
            for value1, value2 in zip(values[0 : size - 1], values[1:size])
        ]
        data[name_difference + "_diff"] = {}
        for i, val in enumerate(diff):
            data[name_difference + "_diff"][str(i + 1)] = val
    return data


def cleanup_json(
    original_path: str,
    cleaned_path: str,
    last_date: dt.datetime,
    delete_30_sec: bool = True,
    delete_15_min: bool = False,
):
    """
    This function cleans all json files stated in original path.
    This means that it will remove all entries which are stated in the keys list,
    For the remaining entries, it will delete all datapoints which are older than last_date,
    sorts them with respect to the Timestamp date and adds the differences of all members stated in
    list_difference.
    if delete_30_sec is set to True, it will also delete all datapoints of type 30_seconds
    """
    assert not delete_30_sec or not delete_15_min

    # delete unused data to speedup generation of plots
    keys_to_delete = [
        # "L1_avg_power_factor",
        # "L1_min_power_factor",
        # "L1_max_power_factor",
        # "L2_avg_power_factor",
        # "L2_min_power_factor",
        # "L2_max_power_factor",
        # "L3_avg_power_factor",
        # "L3_min_power_factor",
        # "L3_max_power_factor",
        # "Total measurement count",
        # "L1_avg_voltage",
        # "L1_max_voltage",
        # "L1_min_voltage",
        # "L1_avg_current",
        # "L1_max_current",
        # "L1_min_current",
        # "L2_avg_voltage",
        # "L2_max_voltage",
        # "L2_min_voltage",
        # "L2_avg_current",
        # "L2_max_current",
        # "L2_min_current",
        # "L3_avg_voltage",
        # "L3_max_voltage",
        # "L3_min_voltage",
        # "Timestamp of first measurement",
        # "L3_avg_current",
        # "L3_max_current",
        # "L3_min_current",
        # "Sensor ID",
        # "iso_day",
        # "iso_month",
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

    for key in keys_to_delete:
        data.pop(key, None)

    # Delete the datapoints of old data to get a overview of the most recent data
    keys_to_delete_too_old_date = [
        key
        for key, date in data["Timestamp"].items()
        if dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S") < last_date
    ]

    # split the data in two datasets of 15 min and 30 secs
    if delete_30_sec:
        keys_to_delete_30_sec = [
            key
            for key, duration in data["Frequency"].items()
            if duration == "type_30_second"
        ]
        keys_to_delete = keys_to_delete_too_old_date + keys_to_delete_30_sec
    elif delete_15_min:
        keys_to_delete_15_min = [
            key
            for key, duration in data["Frequency"].items()
            if duration == "type_15_minutes"
        ]
        keys_to_delete = keys_to_delete_too_old_date + keys_to_delete_15_min
    else:
        keys_to_delete = keys_to_delete_too_old_date

    if keys_to_delete:
        for key in data.keys():
            for key_to_delete in keys_to_delete:
                data[key].pop(key_to_delete, None)

    difference_list = ["L1_active_energy", "L2_active_energy", "L3_active_energy"]

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

        data_heatpump = add_difference(data_heatpump, difference_list)
        data = add_difference(data, difference_list)
        name, ending = cleaned_path.split(".", 1)
        filename_heatpump = name + "_heatpump.json"
        filename_add_heat = name + "_add_heat.json"
        # make shure it is not empty
        if "Device" in data_heatpump.keys() and data_heatpump["Device"]:
            with open(filename_heatpump, "w") as f:
                json_str = json.dumps(sort_and_rename_keys(data_heatpump), indent=4)
                f.write(json_str)

        # make shure it is not empty
        if "Device" in data.keys() and data["Device"]:
            with open(filename_add_heat, "w") as f:
                json_str = json.dumps(sort_and_rename_keys(data), indent=4)
                f.write(json_str)
        return
    data = add_difference(data, difference_list)

    # make shure it is not empty
    if "Device" in data.keys() and data["Device"]:
        with open(cleaned_path, "w") as f:
            json_str = json.dumps(sort_and_rename_keys(data), indent=4)
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
    last_date = dt.datetime(year=2024, month=8, day=31)
    for i, (original_file, cleaned_file) in enumerate(filelist_to_get_and_store):
        cleanup_json(
            original_file,
            cleaned_file,
            last_date,
            delete_30_sec=False,
            delete_15_min=True,
        )
        print(
            f"{int(float(i * 100) / len(filelist_to_get_and_store))}% done: {cleaned_file}"
        )
