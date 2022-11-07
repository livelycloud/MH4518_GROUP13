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
