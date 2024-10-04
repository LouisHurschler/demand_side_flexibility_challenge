import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from meteodata.read_meteo import read_meteo


file_path = os.path.join(os.path.dirname(__file__),
                         "..", "data_enflate", "site_6013.json")
metering = pd.read_json(file_path)
metering.set_index('Timestamp', inplace=True)
metering = metering[metering.index > '2024-08-29']

metering['ActEnergy'] = (metering['L1_active_energy']
                         + metering['L2_active_energy']
                         + metering['L3_active_energy'])

metering['ActPower_kW'] = metering['ActEnergy'].diff() / 10.


plt.plot(metering.index, metering['ActPower_kW'])

meteo = read_meteo()
meteo = meteo[meteo.index > '2024-08-29']
plt.plot(meteo.index, meteo['GlobIrradiation_W/m²'] / 1000. * 3)

plt.show()

