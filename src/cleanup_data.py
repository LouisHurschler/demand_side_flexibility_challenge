import json
import os
import tkinter as tk
from tkinter import filedialog as fd
import datetime as dt


def cleanup_json(original_path: str, cleaned_path: str, last_date: dt.datetime):
    keys = ['L1_avg_power_factor', 'L1_min_power_factor', 'L1_max_power_factor', 'L2_avg_power_factor',
            'L2_min_power_factor', 'L2_max_power_factor', 'L3_avg_power_factor', 'L3_min_power_factor',
            'L3_max_power_factor', 'Total measurement count', 'L1_avg_voltage', 'L1_max_voltage',
            'L1_min_voltage', 'L1_avg_current', 'L1_max_current', 'L1_min_current',
            'L2_avg_voltage', 'L2_max_voltage', 'L2_min_voltage', 'L2_avg_current', 'L2_max_current',
            'L2_min_current', 'L3_avg_voltage', 'L3_max_voltage', 'L3_min_voltage', 'Timestamp of first measurement',
            'L3_avg_current', 'L3_max_current', 'L3_min_current', 'Sensor ID', 'iso_day', 'iso_month']
    with open(original_path, "r") as f:
        data = json.load(f)
    for key in keys:
        data.pop(key, None)

    keys_to_delete = [key for key, date in data["Timestamp"].items() if
                      dt.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') < last_date]
    if keys_to_delete:
        for key in data.keys():
            for key_to_delete in keys_to_delete:
                data[key].pop(key_to_delete, None)
    with open(cleaned_path, "w") as f:
        json_str = json.dumps(data, indent=4)
        f.write(json_str)





def get_filelist() -> list:
    """
    Function to get a list of all json files one wants to include in an analysis.
    You have to have already created a directory and included all neccesairy json files before calling this function.
    """

    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    directory_path = fd.askdirectory()
    os.makedirs(directory_path + "_cleaned", exist_ok=True)

    filenames = os.listdir(directory_path)
    filenames = [file for file in filenames if file.endswith(".json")]

    return [(directory_path + "/" + filename, directory_path + "_cleaned/" + filename) for filename in filenames]


if __name__ == "__main__":
    filelist_to_get_and_store = get_filelist()
    last_date = dt.datetime(year=2024, month=7, day=22)
    for i, (original_file, cleaned_file) in enumerate(filelist_to_get_and_store):
        cleanup_json(original_file, cleaned_file, last_date)
        print(f'{int(i * 100 / len(filelist_to_get_and_store))}% done')
