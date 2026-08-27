from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import matplotlib.dates as mdates

start_date = "2025-08-25"
end_date = "2026-08-26"
windowsz = 20
low_percentile = 33
high_percentile = 67

figures_dir = Path("figures")
results_dir = Path("results")
figures_dir.mkdir(exist_ok=True)
results_dir.mkdir(exist_ok=True)

def analysestock(company_name, ticker, fx_ticker):
    stock = yf.Ticker(ticker)
    marketdata = stock.history(start = start_date, end = end_date)
    exchangedata = yf.Ticker(fx_ticker).history(start = start_date, end = end_date)
    if marketdata.empty:
        raise ValueError(f"No stock market data downloaded for {company_name}.")
    if exchangedata.empty:
        raise ValueError(f"No exchange-rate data downloaded for {company_name}.")
    stockclose = marketdata["Close"].copy()
    fxrate = exchangedata["Close"].copy()
    stockclose.index = stockclose.index.date
    fxrate.index = fxrate.index.date
    fxrate = fxrate.reindex(stockclose.index)
    fxrate = fxrate.ffill()
    stockclose_gbp = stockclose / fxrate
    stockclose_gbp = stockclose_gbp.dropna()
    
    returns_gbp = []
    for i in range(1, len(stockclose_gbp)):
        prev_price = stockclose_gbp.iloc[i-1]
        curr_price = stockclose_gbp.iloc[i]
        daily_return = (curr_price - prev_price) / prev_price
        returns_gbp.append(daily_return)
        
 
    dailyvolatility = np.std(returns_gbp, ddof=1)
    rlng_volatility = []

    for i in range(windowsz, len(returns_gbp)+1):
        windowreturns = returns_gbp[i-windowsz:i]
        volatility = np.std(windowreturns, ddof=1)
        rlng_volatility.append(volatility)
        
    rlng_volatility_pct = []
    for volatility in rlng_volatility:
        rlng_volatility_pct.append(volatility*100) 
    volatilitydates = stockclose_gbp.index[windowsz:]
    lowthreshold = np.percentile(rlng_volatility_pct, low_percentile)
    highthreshold = np.percentile(rlng_volatility_pct, high_percentile)
    

    volatilityregimes = [] 
    for volatility in rlng_volatility_pct:
        if volatility < lowthreshold:
            regime = "Low"
        elif volatility > highthreshold:
            regime = "High"
        else:
            regime = "Normal" 
            
        volatilityregimes.append(regime)
        
    worst_return = min(returns_gbp)
    worst_index = returns_gbp.index(worst_return)
    worst_return_date = stockclose_gbp.index[worst_index + 1]
    return {"company_name": company_name, "price_gbp": stockclose_gbp, "daily_volatility": dailyvolatility *100, 
            "rolling_volatility_pct": rlng_volatility_pct,"volatility_dates": volatilitydates,
            "low_threshold": lowthreshold, "high_threshold": highthreshold, "volatility_regimes": volatilityregimes,
            "worst_return": worst_return*100, "worst_return_date": worst_return_date}

ferrari_results = analysestock("Ferrari", "RACE", "GBPUSD=X")
schneider_results = analysestock("Schneider Electric", "SU.PA", "GBPEUR=X")
nvidia_results = analysestock("NVIDIA", "NVDA", "GBPUSD=X")
sp500_results = analysestock("S&P 500", "^GSPC", "GBPUSD=X")
commonprices = pd.concat({"Ferrari": ferrari_results["price_gbp"], "Schneider Electric": schneider_results["price_gbp"],
                          "NVIDIA": nvidia_results["price_gbp"], "S&P 500": sp500_results["price_gbp"]}, axis=1, join="inner")
commonprices = commonprices.dropna()
commonnormalised = (commonprices / commonprices.iloc[0])*100
commontotalreturns = (commonnormalised.iloc[-1]-commonnormalised.iloc[0])
commondailyreturns = (commonprices.pct_change().dropna())
commonvolatility = (commondailyreturns.std()*100)
running_pk = commonnormalised.cummax()
drawdown_pct = ((commonnormalised - running_pk) / running_pk)*100
maxdrawdowns = drawdown_pct.min()

comparison_table = pd.DataFrame({"Total Return (%)": commontotalreturns, "Daily Volatility (%)": commonvolatility,
                                 "Maximum Drawdown (%)": pd.Series(maxdrawdowns)})
comparison_table = comparison_table.round(2)


#volatility regime table
regime_table = pd.DataFrame({"Low/Normal Threshold (%)": [ferrari_results["low_threshold"],
                                                          schneider_results["low_threshold"],
                                                          nvidia_results["low_threshold"],
                                                          sp500_results["low_threshold"]],
                             "Normal/High Threshold (%)": [ferrari_results["high_threshold"],
                                                           schneider_results["high_threshold"],
                                                           nvidia_results["high_threshold"],
                                                           sp500_results["high_threshold"]]},
                            index=["Ferrari", "Schneider Electric", "NVIDIA", "S&P 500"])
regime_table = (regime_table.round(2))
print("\n==================")
print("Common Comparison Period")
print("==================")
print("Start Date:", commonprices.index[0].strftime("%d-%m-%Y"))
print("End Date:", commonprices.index[-1].strftime("%d-%m-%Y"))
print("Number of Common Trading Days:", len(commonprices))
print("\n==================")
print("Final Performance Comparison")
print("==================")
print(comparison_table.to_string())
print("\n==================")
print("Volatility Regime Thresholds")
print("==================")
print(regime_table.to_string())
print("\n==================")
print("Ferrari Outlier Check")
print("==================")
print("Worst Observed GBP-Adjusted Return:", round(ferrari_results["worst_return"], 2), "%")
print("Date:", ferrari_results["worst_return_date"].strftime("%d-%m-%Y"))

#saving
comparison_table.to_csv(results_dir / "performance_comparison.csv")
regime_table.to_csv(results_dir / "volatility_regime_thresholds.csv")
commonprices.to_csv(results_dir / "common_gbp_prices.csv")

#figure 1
plt.figure(figsize=(10, 6))
for company in commonnormalised.columns:
    plt.plot(commonnormalised.index, commonnormalised[company], label=company)
plt.axhline(100, linestyle="--")
plt.title("One-Year GBP-Adjusted Relative Performance")
plt.xlabel("Date")
plt.ylabel("Normalised Value (Initial Value = 100)")
plt.grid(True)
plt.legend()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(figures_dir / "relative_performance.png", dpi=300, bbox_inches="tight")
plt.show()

#figure 2
ferrari_volatility = (ferrari_results["rolling_volatility_pct"])
ferrari_dates = (ferrari_results["volatility_dates"])
ferrari_lowthreshold = (ferrari_results["low_threshold"])
ferrari_highthreshold = (ferrari_results["high_threshold"])
ymax = max(ferrari_volatility)*1.1
plt.figure(figsize=(10, 5))
plt.axhspan(0, ferrari_lowthreshold, alpha=0.2, color="green", label="Low Volatility")
plt.axhspan(ferrari_lowthreshold, ferrari_highthreshold, alpha=0.2, color="orange", label="Normal Volatility")
plt.axhspan(ferrari_highthreshold, ymax, alpha=0.2, color="red", label="High Volatility")
plt.plot(ferrari_dates, ferrari_volatility, color="black", label="20-Day Rolling Volatility")
plt.title("Ferrari (RACE) Rolling Volatility Regimes")
plt.xlabel("Date")
plt.ylabel("20-Day Rolling Volatility (%)")
plt.ylim(0, ymax)
plt.grid(True)
plt.legend()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%Y"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(figures_dir / "ferrari_volatility_regimes.png", dpi=300, bbox_inches="tight")
plt.show()