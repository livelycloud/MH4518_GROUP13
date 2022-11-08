from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

def calculate_return(df, asset_name: str):
   df[asset_name + "_return"] = np.log(df[asset_name] / df[asset_name].shift(1))

def calculate_returns(df, asset_names):
   for asset_name in asset_names:
      calculate_return(df, asset_name)

def preprocess_date(df):
   df["date"] = pd.to_datetime(df["Dates"], format = "%d/%m/%Y")
   
   
class AssetModel(ABC):

    start_date: str
    cur_date: str

    def __init__(self, df: pd.DataFrame, fixing_date: str):
        preprocess_date(df)
        self.start_date = df["date"].min()
        self.end_date = df["date"].max()
        self.df = df.set_index("date")
        self.fixing_date = fixing_date

    
    def set_start_date(self, start_date: str):
        self.start_date = start_date

    def set_cur_date(self, cur_date: str):
        self.cur_date = cur_date
    
    def fit_date(self, start_date: str, cur_date: str):
        data = self.df.loc[start_date:cur_date]
        self.fit_model(data)
    
    @abstractmethod
    def fit_model(self, data: pd.DataFrame):
        return NotImplemented

    @abstractmethod   
    def get_predict_price(self, cur_date: str):
        return NotImplemented

    @abstractmethod
    def get_path(self, cur_date: str):
        return NotImplemented


## Assumption: data is on daily frequence
## delta_t = 1
class  MultiAssetGBM(AssetModel):

    asset_names: list
    r: float
    v: float
    sigma: float

    def __init__(self, df: pd.DataFrame, fixing_date: str, asset_names: list):
        super().__init__(df, fixing_date)
        self.asset_names = asset_names
        calculate_returns(self.df, asset_names)
        self.return_names = [x + "_return" for x in self.asset_names]
        self.no_of_assets = len(self.asset_names)

    def fit_model(self, data: pd.DataFrame):
        returns = data[self.return_names]
        self.r = returns.mean()
        self.v = self.r
        self.sigma = np.sqrt(returns.cov())


    def get_predict_price(self, cur_date: str):
        self.set_cur_date(cur_date)
        self.fit_date(self.start_date, self.cur_date)
        # print(datetime.strptime(self.cur_date, time_format), datetime.strptime(self.fixing_date, time_format))
        days = np.busday_count( self.cur_date, self.fixing_date)
        
        w = np.random.normal(0, 1, self.no_of_assets)
        print(w)

        self.s_0 = self.df.loc[cur_date, self.asset_names]

        return self.s_0.values * np.exp(self.v * days + self.sigma.transpose() @ w)
        

    def get_path(self, cur_date: str):
        self.set_cur_date(cur_date)
        self.fit_date(self.start_date, self.cur_date)
        days = np.busday_count( self.cur_date, self.fixing_date)
        
        w = np.random.normal(0, 1, (self.no_of_assets, days))
        self.s_0 = self.df.loc[cur_date, self.asset_names]
        return_path =np.exp(np.repeat([self.v.values], [days], axis = 0).transpose() + self.sigma.transpose().values @  w).cumprod(axis = 1)
        price_path = np.diag(self.s_0) @ return_path
        return price_path