from multi_asset_GBM import MultiAssetGBM
import pandas as pd
import numpy as np
from tqdm import tqdm
import os


if __name__ == "__main__":

    print(os.getcwd())

    Nsim = 10000
    np.random.seed(4518)
    save_path = "../generated_data/multiGBM_simple/" 
    time_format = "%Y-%m-%d"
    
    sample_cols = ["GOOGL", "MSFT", "AAPL"]
    fixing_date = "2023-07-26"
    asset_names = ["GOOGL UW Equity", "MSFT UW Equity", "AAPL UW Equity"]
    df = pd.read_csv("stock_historical_prices.csv")

    historical_data_start_date = "2021-07-01"
    
    multassetGBM = MultiAssetGBM(df, fixing_date, asset_names)
    multassetGBM.set_start_date(historical_data_start_date)

    for cur_date in tqdm(pd.bdate_range("2022-08-15", "2022-10-31")): # "2022-05-31", "2022-08-15", "2022-10-31"
        sample_start_date = cur_date + pd.Timedelta(days = 1)
        samples = [pd.DataFrame(multassetGBM.get_path(cur_date.strftime(time_format)).transpose(), 
                    columns = sample_cols, 
                    index = pd.bdate_range(sample_start_date, fixing_date, name = "date")) for i in range(Nsim)]
        for i in range(Nsim):
            samples[i]["index"] = i
        samples_df = pd.concat(samples)

        cur_path = save_path + sample_start_date.strftime(time_format) + ".csv"
        print(cur_path)
        samples_df.to_csv(cur_path)