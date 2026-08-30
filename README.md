# Engineering Market Performance Project
## Performance, Volatility and Drawdown Across Equities.

The reusable workflow developed in this project serves to analyse and compare the behaviour of several engineering-related equities against a broad-market benchmark (**S&P 500**). This pipeline was validated against event-driven outliers and tested across automotive, semi-conductor and industrial engineering equities. In detecting changing volatility regimes in noisy market data, the objective of this project was to conduct preprocessing, statistical characterisation, validation and comprarative interpretation. 

Each dataset is treated as a noisy time-series signal and, in addition to extreme observations and behaviour relative to the benchmark, investigates:
- relative performance
- daily return variability
- rolling volatility
- max drawdown

The three engineering-related datasets analysed in this project are:
- **Ferrari (RACE)** - automotive and motorsport engineering
- **Schneider Electric (SU.PA)** - industrial automation, electrification and energy management
- **NVIDIA (NVDA)** - high-performance computing and semiconductor tech

#

A deliberate focus was made on transparent and interpretable methods, rather than predictive machine-learning or trading models. All returns were GBP-adjusted and the analysis time period was fixed (**25 August 2025 - 25 August 2026**), before synchronisation reduced this to **249 common trading days**. As a result, the final comparison concerns these 249 common trading days.

Extreme observations were individually investigated, to ensure legitimacy, before analysis. Ferrari's notably large negative return, on October 9th 2025, was retained after validation against Ferrari's Capital Markets Day and concurring market reports. Investors grew concerned over the release of Ferrari's long-term growth proposal, therefore, the -14.86% GBP return resulted from a genuine market event.

#

Volatility-regime analysis showed absolute volatility levels differed materially between assets, while the percentile classifier provided an asset relative condition-monitoring framework. Ferrari's severe single-day shock is distinctly greater than it's negative annual return, demonstrating the importance of path-dependent downside risk over simple end-to-end returns. The strongest observed return was produced by Schneider, whilst NVIDIA exhibited a similar return to the benchmark (S&P 500) and produced the greatest overall day-to-day volatility.

During this specific observation window:
- Schneider Electric delivered a GBP-adjusted performance of +39.33%, with a maximum drawdown of 18.37%.
- NVIDIA returned +16.88% but exhibited a substantially deeper maximum drawdown of -20.78%.
- Ferrari returned -9.50% and experienced the greatest drawdown of -37.33%.
- S&P 500 returned +17.88%, with a maximum drawdown of -8.50%.
