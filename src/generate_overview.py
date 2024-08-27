import tkinter as tk
from tkinter import filedialog as fd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import numpy as np
import json
import os

def plot_distribution_from_results():
    root = tk.Tk()
    root.withdraw()
    print("select the path of the directory where the json data is stored")
    path_json_data = fd.askopenfilename()
    with open(path_json_data) as f:
        data = json.load(f)


    plt.figure(figsize=(10, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    for datapoint in data.keys():
        days = -np.linspace(0, len(data[datapoint]), len(data[datapoint]))
        data_to_plot = list(data[datapoint].values())
        plt.plot(days, data_to_plot)

    plt.gcf().autofmt_xdate()
    plt.title('Plot amount of Data')
    plt.xlabel('Days')
    plt.ylabel('#Datapoints')
    plt.grid(True)
    plt.savefig("../results/data_distribution.pdf")

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
        x_values = data['Timestamp'].values()

        if type == "Boiler":
            color = "b"
        elif type == "Heatpump" or type == "Add.Heating":
            color = "r"
        else:
            color = "w"
        x_values = [dt.datetime.strptime(x_value, '%Y-%m-%d %H:%M:%S') for x_value in x_values]
        # choose following y_value to group values together which started arount the same time
        # y_values = np.ones(len(x_values)) * int(min(x_values).strftime('%M%d'))
        y_values = np.ones(len(x_values)) * i
        plt.plot(x_values, y_values, linestyle='None', marker=".", color=color)
        print(f'file {file} read successfully! {int(i * 100 / len(filelist))}% done')
    plt.title('Plot amount of Data')
    plt.xlabel('Days')
    plt.ylabel('#Datapoints')
    plt.grid(True)
    # plt.show()
    plt.savefig("../results/data_distribution_from_data_cleanup_twice.png")

if __name__ == "__main__":
    plot_directly_from_data()

