## Data and Back Test Results 

// TODO: (2~3 pages, including graphs)

### Data Used

// TODO: describe the data used

The following data were downloaded from Bloomberg Terminal 4 in Business Library NTU:

1. The daily last price of the underlying assets, Alphabet Inc. -A (GOOGL UW), Apple Inc. (AAPL UW), and Microsoft Corp (MSFT UW), from 1 Oct 2017 to 31 Oct 2022;
2. The daily last price of the product, from 2 May 2022 to 31 Oct 2022;
3. The daily mid yield of the US Government Treasury bills with maturity dates range from 30 April 2023 to 15 Nov 2029. The data start on 1 Oct 2020 and end on 1 Nov 2022.

The following data were collected online from the US department of the treasury:

1. Historical yield curve from 2020 to 2022.



### Back Test Method

// TODO: how the back tests are conducted (To be completed after the first three chapters are done)

```
For cur_date := business day range (01-06-2022, 31-10-2022):

	1. Generate interest rate for cur_date:
		a. Use one-year historical yield curve data until cur_date - 1 to calibrate short rate model.
		b. Generate Random Variables (TODO: Set 1 Z....)
		c. Use Short Rate Model mentioned in (TODO: ) to simulate interest rate paths
		d. Take the average interest rate as r
	2. Simulate future price paths:
		a. Use one-year historical price paths of the three underlying assets to calibrate Multidimentional Geometric Brownian Motion(GBM) mas entioned in (TODO: ) 
		b. Use r from Step 1.d as the mu in GBM for risk neutral valuation.
		c. Generate random variables {W_m_i_j}~N(0, 1) where 0<= m < 999, 0<=i<3, 0<=j<final_fixing_date - cur_date. 
			ci. Apply Inverse cdf to {W_m_i_j} to get MC rvs;
			cii. Apply Inverse cdf to {W_m_i_j} and {- W_m_i_j} to get AV rvs;
			ciii. Apply Stratified Sampling Method in (TODO: ) to get SS rvs.
		d. For each set of rvs obtained in step 2c, generate future price paths using GBM Model.
	3. Use Least Square Regression and dynamic programming as mentioned in (TODO: ) to price the product.
		a. For each simulated price paths, calculate the final day payoff P (including demonination and coupon), denote the final_redemption_date as v_date
		b. For each not passed early_exercise_day:
			calculate P = discounted (P + coupon between early_exercise_day and v_date)
			run Least Sqaure regression (degree 2 polynomial) of P~S
			compared f(S) with the current payoff P_c(5000 + discounted future coupon on the corresponding coupon payment date)
			if f(S) is smaller, set keep P; else set P = P_c
			set v_date = early_exercise_day
		c. For each not passed coupon_payment_date between cur_date and v_date:
			calculate P = discounted (P + coupon)
	4. Take the mean as the final pricing.
```



### Results and Analysis

// TODO: Interpret the results/comparisons 

#### Simulation of Interest Rate Model

#### Simulation of The underlying Assets

![image-20221112164750085](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\google-2022-08-02)

The graph above shows an example of simulated price paths. The colorful lines are 1000 simulated price paths by GBM for Google on 2 Aug 2022. The black line is the true price path of google in the date range 1 Aug 2021 to 31 Oct 2023, where a decreasing trend can be observed. However, as we use risk-neutral valuation, where the average log return of a stock is assumed to be equal to the risk-free rate, the average of all simulated price paths has a small increasing trend which corresponds to the predicted interest rate of  2.498%. 



![image-20221112165641707](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20221112165641707.png)

Covariance Matrix based on historical data on 2 Aug 2022

|       | GOOGL | APPL | MSFT |
| ----- | ----- | ---- | ---- |
| GOOGL |       |      |      |
| APPL  |       |      |      |
| MSFT  |       |      |      |

From the covariance matrix table, we can observe that the covariance of the three assets are very high, which means they are highly correlated with each other, which can also been observed from simulated price paths, e.g. in Fig (TODO: ). In addition, the variance of google is the highest, which mean it has the highest volatility. 

#### Pricing Results

//TODO: attempt to explain the deviations from the benchmark (true) prices.

![image-20221112165840257](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\mc)

|               | Standard Monte Carlo | Antithetic Variate | Stratified Sampling |
| ------------- | -------------------- | ------------------ | ------------------- |
| SE (mean) (%) | 0.63107              | 0.44694            | 0.63469             |
| RMSE (%)      | 2.065                | 2.353              | 2.389               |

$p_{t,m}$ is the $m^{th}$ simulated price on day t in the percentage of 5000.
$$
\begin{aligned}
\hat{p}_t & = \frac{1}{N}{\sum_{m=1}^{N} }p_{t, m}
\\
\sigma_t & = \sqrt{\frac{1}{N - 1}{\sum_{m=1}^{N} (p_{t, m} -\hat{p}_t )^2}}
\\
SE_t & = \frac{\sigma_t}{\sqrt{N}}
\\
\overline{SE} &= \frac{1}{T}\sum_{t = 1}^{T}SE_t
\\
RMSE &= \sqrt{\frac{1}{T} \sum_{t = 1}^{T} (\hat{p}_t  - p_t)^2}
\end{aligned}
$$
Our estimation of the price path has the same trend (including rise and fall) as the true price path of the product, which validates our method to some extent. However, it is noteworthy that our price path is almost always lower than the true path. This could probably due to the following reasons:

1. Our estimation of the interest rate is higher than the market participants
2. Our estimation of the risk involved is probably higher than the market participants. (TODO: using different rolling window size, TODO: use Heston model)

#### Results of Greek Values

![image-20221113134255666](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\delta)

The estimation of delta shows the sensitivity of the price of the product to the price change of the three underlying assets. In June to mid-July, the red line which represents the delta of APPL is the highest among the three, showing that the product price was very sensitive to the price change in APPL. From mid-July to 1 September, the green line which represents the delta of GOOGL is the highest among the three, shows that the product price was very sensitive to the price change in GOOGL. A similar result can be observed from the gamma graph in (TODO: Appendix D, and explain gamma?). The reason behind this sensitivity is probably that as the product is barrier reverse convertible, the asset with the lowest price would have a higher chance to hit the barrier thus bringing larger risk to the product, thus having the largest influence on the product price.

##  Conclusion and Reflection

// TODO: (0.5 page): 

//TODO: concludes the study and share your insights into the problems encountered 

be cautious of buying such products (return may be dependent on the interest rate which is influenced by government economic policies.)
Remember to do risk neutral valuation, as there are too many noises in the stock's past returns

(not sure about the stock's future performance (difficult to predict return), but volatility is generally more stable)

//TODO: potential improvements.

Use more complicated models, e.g. Heston to capture local volatility. (We try to use heston Model, but due to human and resource constraints, we are not able to carry out the experiments).



### Appendix 1: Examples of Simulated Price Path

![image-20221112164750085](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\google-2022-08-02)

![image-20221112164625023](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\apple-2022-08-02)

![image-20221112164722029](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\msft-2022-08-02)



### Appendix 2: Simulated Price Paths with Variance Reduction Techniques

![image-20221112165947384](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\av)

![image-20221112170009812](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\ss)

### Appendix C: Estimation of Gamma

![image-20221113134320770](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\gamma)

### Appendix D: Historical Price Paths of the three underlying assets

![img](D:\ntu\y3s1\MH4518\project\MH4518_GROUP13\data_and_backtest_results\graphs\true_price_paths_three_underlying)