from asset_model import AssetModel, calculate_return
import pandas as pd
import numpy as np



## Assumption: data is on daily frequence
## delta_t = 1
class SingleAssetGBM(AssetModel):

    asset_name: str
    r: float
    v: float
    sigma: float

    def __init__(self, df: pd.DataFrame, fixing_date: str, asset_name):
        super().__init__(df, fixing_date)
        self.asset_name = asset_name
        # self.df = self.df[["date", asset_name]]
        calculate_return(self.df, asset_name)


    def fit_model(self, data: pd.DataFrame):
        self.r = data[self.asset_name + "_return"].mean()
        self.v = self.r
        self.sigma = np.sqrt(1 / (len(data) - 1) * np.sum((data[self.asset_name + "_return"] - self.r) ** 2) )


    def get_predict_price(self, cur_date: str):
        self.set_cur_date(cur_date)
        self.fit_date(self.start_date, self.cur_date)
        # print(datetime.strptime(self.cur_date, time_format), datetime.strptime(self.fixing_date, time_format))
        days = np.busday_count( self.cur_date, self.fixing_date)
        
        w = np.random.normal(0, 1)
        print(w)
        return self.df.loc[cur_date, self.asset_name] * np.exp(self.v * days + self.sigma * days * w)


    def get_path(self, cur_date: str):
        self.set_cur_date(cur_date)
        self.fit_date(self.start_date, self.cur_date)
        days = np.busday_count( self.cur_date, self.fixing_date)
        
        w = np.random.normal(0, 1, days)
        price_path = pd.Series(np.exp(self.v + self.sigma * w)).cumprod() * self.df.loc[cur_date, self.asset_name]
        return price_path