import pandas as pd
from matplotlib import pyplot as plt


def read_meteo():
    # Reads meteo data from .txt file as panda dataframe

    # File path to the .txt file
    file_path = 'order_124794_data.txt'  # Replace with the actual path to your file

    # Read the .txt file into a pandas DataFrame
    meteo = pd.read_csv(file_path, sep=';')

    # All data is from the same meteo station "STG"
    meteo.drop('stn', axis=1, inplace=True)
    # Convert the 'time' column to pandas datetime format
    meteo['time'] = pd.to_datetime(meteo['time'], format='%Y%m%d%H%M').dt.tz_localize('UTC')
    meteo['time'] = meteo['time'].dt.tz_convert('Etc/GMT-2')
    meteo = meteo.rename(columns={'gre000z0': 'GlobIrradiation_W/m²',
                                  'tre200s0': 'Temp_C',
                                  'sre000z0': 'sunshine_min'})
    meteo.drop('sunshine_min', axis=1, inplace=True)
    meteo.set_index("time", inplace=True)
    return meteo


if __name__ == "__main__":

    meteo_df = read_meteo()

    # Display the first few rows of the dataframe
    print(meteo_df.head())
    meteo_df.plot()
    plt.show()