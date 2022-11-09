import pandas as pd
import numpy as np
import statsmodels.api as sm
from tqdm import tqdm

rv_type = "ss"
Nsim = 5000 #if av, change to 2 * Nsim


inerest_rate_path = "../interest rate model/interest_rate_YC_wh.csv"
simulation_path = "../generated_data/final_" + str(Nsim) + "/" + rv_type + "/"


time_format = "%Y-%m-%d"

interest_rate_date = "2022-07-26" # TODO: hard code, need to change when used

denomination = 5000
barrier = 0.59
# being the date on which the Strike and the Barrier and the Ratio is fixed,
# and from which date the Complex Products may be traded
initial_fixing_date = "2022-04-25" 
final_fixing_date = "2023-07-26"
final_redemption_date = "2023-08-02"

issue_date = "2022-05-02"

coupon_rate = 0.11 / 4

coupon_payment_dates = [
    "2022-08-02",
    "2022-11-02",
    "2023-02-02",
    "2023-05-02",
    "2023-08-02"
]

exercise_dates = [
    "2022-10-26",
    "2023-01-26",
    "2023-04-25"
]

early_redemption_dates = [
    "2022-11-02",
    "2023-02-02",
    "2023-05-02"
]

stock_init_price = {
    "GOOGL":  2461.48 / 20,
    "AAPL": 162.88,
    "MSFT": 280.72
}

stock_ratio = {
    "GOOGL":  40.62596486666558,
    "AAPL": 30.6974,
    "MSFT": 17.8113
}

stock_names = ["GOOGL",	"MSFT",	"AAPL"]



def get_business_days_from_initial_date(cur_date, initial_date = issue_date):
    return np.busday_count(initial_date, cur_date)

def get_business_days_to_final_redemption(cur_date, final_date = final_redemption_date):
    return np.busday_count(cur_date, final_date)

## dummy intesest rate func 
# (should return the average interest rate from current date to final redemption date)
def get_interest_rate(cur_date, to_date = final_redemption_date):
    r = float(interest_rate_df.loc[interest_rate_date, "rate"]) / 100
    return r

def get_discounted_price(p: float, cur_date, to_date = final_redemption_date):
    r = get_interest_rate(cur_date)
    return p * np.exp(- r * np.busday_count(cur_date, to_date) / 250)

## p_mature should be the lowest total price of stocks
def get_product_price(p_mature, cur_date, next_date = final_redemption_date):
    coupon_remaining = 0.0
    for coupon_payment_date in coupon_payment_dates:
        if cur_date <= coupon_payment_date and coupon_payment_date < next_date:
            coupon_remaining += get_discounted_price(denomination * coupon_rate, cur_date, coupon_payment_date)
    d = get_discounted_price(p_mature, cur_date, final_redemption_date)
    return d + coupon_remaining

## input: 
stock_names = ["GOOGL", "AAPL", "MSFT"]

def get_redemption_amount(df: pd.DataFrame):
    lowest_prices = df[stock_names].min()
    barrier_trigger = (lowest_prices / df_init_price < barrier).sum() 

    # if log:
    #     print("barrier_trigger", barrier_trigger)

    if barrier_trigger > 0:
        tmpdf = df.reset_index().set_index("date")
        stock_min = (tmpdf.loc[tmpdf.index.max(), stock_names] * df_convert).min()
        # if log:
        #     print("stock_min", stock_min)
        return min(stock_min, denomination)
    else:
        return denomination

## y = a_0 + a_1 * x + a_2 * x ** 2
class Poly2DModel:
    
    mod: sm.OLS
    x_name: str
    
    def fit(self, df : pd.DataFrame, x_names: list, y_name: str):
        self.x_names = x_names.copy()
        self.df = df
        for x_name in self.x_names:
            self.df[x_name + "_sq"] = np.power(self.df[x_name], 2)
        
        self.x_names.extend([x_name + "_sq" for x_name in self.x_names])
            
        self.X = sm.add_constant(self.df[self.x_names])
        self.y = self.df[y_name]
        self.mod = sm.OLS(self.y, self.X).fit()

    def predict(self):
        self.df["pred"] = self.mod.predict()
        return self.mod.predict()

def get_sim_noncallable_price(df: pd.DataFrame):
    func_df = df.set_index(["index", "date"])
    l = []
    for i in  range(Nsim):
        tmp_df = func_df.loc[i]
        l.append(get_product_price(get_redemption_amount(tmp_df), cur_date = final_redemption_date))
        
    return pd.Series(l, index = pd.Series([x for x in range(Nsim)]))

# input df: to get prices of underlying assets to run the regression
def get_v_backward(df: pd.DataFrame, exercise_date: str, redemption_date: str, v: pd.Series, v_date: str) -> pd.Series:
    discounted_v = v.apply(lambda x: get_discounted_price(x, redemption_date, v_date))
    mod = Poly2DModel()
    regress_input_df = (
        df.set_index(["date", "index"])
        .loc[exercise_date, stock_names]
    ).assign(discounted_v = discounted_v)

    mod.fit(regress_input_df, stock_names, "discounted_v")
    pred_v = mod.predict()

    return discounted_v.where((pred_v < denomination), other = denomination) + denomination * coupon_rate

if __name__ == "__main__":
    interest_rate_df = pd.read_csv(inerest_rate_path, index_col = "Date")
    df_init_price = pd.Series(stock_init_price)
    df_convert = pd.Series(stock_ratio)

    if rv_type == "av":
        Nsim *= 2

    for cur_date in tqdm(pd.bdate_range( "2022-06-30", "2022-07-31")): # "2022-05-31", "2022-08-15", "2022-10-31"
        cur_date = cur_date + pd.Timedelta(days = 1)
        sim_df = pd.read_csv(simulation_path + cur_date.strftime(time_format) + ".csv")

        save_date = cur_date.strftime(time_format)

        v_date = final_redemption_date
        v_price = get_sim_noncallable_price(sim_df) + denomination * coupon_rate
        cur_date = sim_df.date.min()
        interest_rate_date = cur_date # TODO: hardcode (should be fine)
        for i in range(len(exercise_dates) - 1, -1, -1):
            exercise_date = exercise_dates[i]
            if cur_date < exercise_date:
                redemption_date = early_redemption_dates[i]
                v_price = get_v_backward(sim_df, exercise_date, redemption_date, v_price, v_date)
                v_date = redemption_date

        ## edge case: consider the first coupon paymeent
        if cur_date < coupon_payment_dates[0]:
            v_price = v_price.apply(lambda x: get_product_price(x, coupon_payment_dates[0], next_date= v_date))
            v_date = coupon_payment_dates[0]

        v_0_price = v_price.apply(lambda x: get_product_price(x, cur_date, next_date= v_date))
        v_0_price.to_csv(simulation_path + save_date + "v_0" + ".csv")

