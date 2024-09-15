import os

import pandas as pd
import matplotlib.pyplot as plt
import re


def normalize(values: list) -> list:
    max_value = max(values)
    return [value / float(max_value) for value in values]


# "flatten" the curve to get more visually appealing results
def get_running_mean(values: list, influence_range: int) -> list:
    res = [0] * len(values)

    # first and last part
    for i in range(influence_range):
        res[i] = sum([values[j] for j in range(i + influence_range + 1)]) / float(
            i + influence_range + 1
        )
        res[len(values) - i - 1] = sum(
            [
                values[j]
                for j in range(len(values) - influence_range - i - 1, len(values))
            ]
        ) / float(i + influence_range + 1)

    for i in range(influence_range, len(values) - influence_range):
        res[i] = sum(
            [values[j] for j in range(i - influence_range, i + influence_range + 1)]
        ) / float(2 * influence_range + 1)

    return res


# extract the four digits at the end of the filename
def extract_four_digits( filename):
    # Define the regex pattern to match exactly four digits before ".json"
    pattern = r"(\d{4})"

    # Use re.search to find the pattern in the filename
    match = re.search( pattern, filename)

    # Check if a match was found
    if match:
        # Extract and return the four-digit number
        return match.group( 1)
    else:
        return None


def read_file( path: str):
    df = pd.read_json( path)
    df.set_index( 'Timestamp', inplace=True)
    df.index = pd.to_datetime( df.index)

    # time selection
    df[ 'hour'] = df.index.hour
    df[ 'day'] = df.index.day
    df[ 'month'] = df.index.month
    df[ 'year'] = df.index.year
    df[ 'week_of_year'] = df.index.isocalendar().week
    df[ 'day_of_week'] = df.index.day_of_week

    # calculations
    # use diff values because other values store the absolute values
    # multiply by 0.012 to get kW (units are 0.1Wh/30 sec)
    df[ 'total_active_energy'] = (df[ 'L1_active_energy_diff'] + df[ 'L2_active_energy_diff'] + df[ 'L3_active_energy_diff']) * 0.012
    df[ 'L1_avg_power'] = ((df[ 'L1_avg_power_factor'] * df[ 'L1_avg_voltage'] * df[ 'L1_avg_current']) / 1000000000000).apply( abs)
    df[ 'L2_avg_power'] = ((df[ 'L2_avg_power_factor'] * df[ 'L2_avg_voltage'] * df[ 'L2_avg_current']) / 1000000000000).apply( abs)
    df[ 'L3_avg_power'] = ((df[ 'L3_avg_power_factor'] * df[ 'L3_avg_voltage'] * df[ 'L3_avg_current']) / 1000000000000).apply( abs)
    df[ 'total_avg_power'] = df[ 'L1_avg_power'] + df[ 'L2_avg_power'] + df[ 'L3_avg_power']

    '''
    print( df.columns)
    print( df.head())
    '''

    '''
    with open(path) as f:
        data = json.load(f)

    # use diff values because other values store the absolute values
    # multiply by 0.012 to get kW (units are 0.1Wh/30 sec)
    active_energy_values = [
        (
            data["L1_active_energy_diff"][idx]
            + data["L2_active_energy_diff"][idx]
            + data["L3_active_energy_diff"][idx]
        )
        * 0.012
        for idx in data["L1_active_energy_diff"].keys()
    ]

    # if influence_range=0, no running mean is calculated
    active_energy_values_running_mean = get_running_mean(
        active_energy_values, influence_range=0
    )
    max_value = max(active_energy_values_running_mean)

    # convert strings of timestamps to datetime objects for plotting
    x_values = np.array(list(data["Timestamp"].values()))
    x_values_dates = [
        dt.datetime.strptime(x_value, "%Y-%m-%d %H:%M:%S") for x_value in x_values
    ]

    data_relay = [
        max_value * relay_state for relay_state in data["relay_state"].values()
    ]
    '''

    return df

def plot_data( site_number, df):
    # plt.figure( figsize=(8, 4))

    plt.plot( df.index, df[ 'relay_state'] * 100, color='blue', label='Relay state 0/1')
    plt.plot( df.index, df[ 'total_active_energy'], color='red', label='Total active power from diff (kW)')
    plt.plot( df.index, df[ 'total_avg_power'], color='green', label='Total active power (kW)')

    '''
    plt.plot(
        x_values_dates,
        data_relay,
        marker=".",
        color="0.8",
        label="relay state",
        markersize=1.0,
    )
    '''

    '''
    plt.fill_between(x_values_dates, 0.0, data_relay, color="grey", label="relay on")
    plt.plot(
        x_values_dates,
        active_energy_values_running_mean,
        marker=".",
        color="r",
        label="sum of active energy",
        markersize=1.0,
    )
    plt.fill_between(x_values_dates, 0.0, active_energy_values_running_mean, color="r")

    plt.title("Active Energy vs. relay state site " + str(site_number))
    plt.ylabel("power [kW]")
    plt.xlabel("Date")
    plt.legend(markerscale=10.0)

    plt.margins(y=0)
    '''

    '''
    plt.savefig(
        "../plots/active_energy_vs_relay_site_" + str(site_number) + ".png",
        dpi=500,
        transparent=True,
    )
    '''

    plt.legend()

    plt.show()

def is_operating( energy):
    if energy > 0.05:
        return 1
    else:
        return 0

def is_starting( operating_diff):
    if operating_diff == 1:
        return 1
    else:
        return 0

def statistics( site_number, period, df):
    device = df.at[ df.index[0], 'Device']
    # col_power = 'total_active_energy'
    col_power = 'total_avg_power'

    # pre-calculation
    df[ 'operating'] = df[ col_power].apply( is_operating)

    # shift
    df_shifted = df.copy( True).shift( 1)

    # print( df.head( 20))
    # print( df_shifted.head( 20))
    # print( (df[ 'operating'] - df_shifted[ 'operating']).head( 20))

    # post-calculation
    df[ 'cycle_start'] = (df[ 'operating'] - df_shifted[ 'operating']).apply( is_starting)

    # statistics
    daily_energy = float( df[ col_power].mean( axis=0)) * 24
    daily_energy_on = float( (df[ col_power] * df[ 'relay_state']).mean( axis=0)) * 24
    daily_energy_off = -1 * float( (df[ col_power] * (df[ 'relay_state'] - 1)).mean( axis=0)) * 24
    daily_operating_hours = float( df[ 'operating'].mean( axis=0)) * 24
    daily_cycles = float( df[ 'cycle_start'].sum()) / 7
    hourly_energy = df[[ 'hour', col_power]].groupby([ 'hour']).mean().to_dict().get( col_power)

    return {
        'index': site_number + '_' + device + '_' + period,
        'site_number': site_number,
        'period': period,
        'device': device,
        'daily_energy': daily_energy,
        'daily_operating_hours': daily_operating_hours,
        'daily_energy_on': daily_energy_on,
        'daily_energy_off': daily_energy_off,
        'daily_cycles': daily_cycles
    } | hourly_energy

def get_filelist( folder_to_read) -> list:
    """
    Function to get a list of all json files one wants to include in an analysis.
    You have to have already created a directory and included all necessary json files before calling this function.
    """

    filenames = os.listdir( folder_to_read)
    filenames = [file for file in filenames if file.endswith(".json")]

    return [ folder_to_read + filename for filename in filenames]

if __name__ == "__main__":
    folder_to_read = 'data_enflate_cleaned/'

    week_unblocked = 30
    week_blocked = 36

    #''' comment to enable/ uncomment to disable
    # process a single file
    # filename_to_read = 'site_1106.json'
    # filename_to_read = 'site_2365.json'
    # filename_to_read = 'site_6037.json'
    filename_to_read = 'site_7083.json'

    path_enflate_data = folder_to_read + filename_to_read

    site_number = extract_four_digits( path_enflate_data)

    df = read_file( path_enflate_data)

    df_unblocked = df.loc[df.week_of_year == week_unblocked]

    plot_data( site_number, df_unblocked)

    stats = statistics( site_number, 'unblocked', df_unblocked)

    print( stats)

    # df_blocked = df.loc[(df.month >= 9) & (df.day <= 7)]
    df_blocked = df.loc[df.week_of_year == week_blocked]

    plot_data( site_number, df_blocked)

    stats = statistics( site_number, 'blocked', df_blocked)

    print( stats)
    #'''

    ''' comment to enable/ uncomment to disable
    # process all files
    files = get_filelist( folder_to_read)

    stats_list = []

    for path_enflate_data in files:
        site_number = extract_four_digits( path_enflate_data)

        print( site_number)

        df = read_file( path_enflate_data)

        df_unblocked = df.loc[df.week_of_year == week_unblocked]

        if df_unblocked.size > 0:
            stats = statistics( site_number, 'unblocked', df_unblocked)

            # print( stats)

            stats_list.append( stats)

        # df_blocked = df.loc[(df.month >= 9) & (df.day <= 7)]
        df_blocked = df.loc[df.week_of_year == week_blocked]

        if df_blocked.size > 0:
            stats = statistics( site_number, 'blocked', df_blocked)

            # print( stats)

            stats_list.append( stats)

    stats_df = pd.DataFrame( stats_list)
    stats_df.set_index( 'index', inplace=True)

    # print( stats_df.head())

    stats_df.to_csv( 'data_results/stats.csv')
    #'''
