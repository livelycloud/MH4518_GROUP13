import pandas as pd
import numpy as np
import statsmodels.api as sm
from tqdm import tqdm
import matplotlib.pyplot as plt 
import datetime as dt
import matplotlib.dates as mdates

estimated_prices = []
estimated_prices_av = []
estimated_prices_ss = []
for cur_date in tqdm(pd.bdate_range( "2022-08-15", "2022-10-31")): # "2022-05-31", "2022-08-15", "2022-10-31"
    cur_date = cur_date + pd.Timedelta(days = 1)
    price_df = pd.read_csv(pricing_path + cur_date.strftime(time_format)+ "v_0"  + ".csv")
    estimate = price_df.mean(axis=0)[1]/5000
    estimated_prices .append(estimate)
    price_df_av = pd.read_csv(pricing_path_av + cur_date.strftime(time_format)+ "v_0"  + ".csv")
    estimate = price_df_av.mean(axis=0)[1]/5000
    estimated_prices_av .append(estimate)
    price_df = pd.read_csv(pricing_path_ss + cur_date.strftime(time_format)+ "v_0"  + ".csv")
    estimate = price_df_ss.mean(axis=0)[1]/5000
    estimated_prices_ss .append(estimate)
dates = []
for i in pd.bdate_range("2022-08-15", "2022-10-31"):
    date = i+ pd.Timedelta(days = 1)
    dates.append(date.strftime(time_format))
x = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
f = plt.figure()
f.set_figwidth(40)
f.set_figheight(10)
plt.plot(true_prices)
plt.plot(estimated_prices)
plt.plot(estimated_prices_av)
plt.plot(estimated_prices_ss)
plt.legend(['true price','GBM','av','ss'])
