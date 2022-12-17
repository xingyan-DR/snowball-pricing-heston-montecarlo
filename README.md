# snowball-pricing-heston-montecarlo

A snowball pricing model with Heston Monte Carlo simulation method, utilizing QuantLib.

Some concept clarification:

### Mathematical Representation of Heston model

In Heston model, the stock price follows the below stochastic process where the volatility is also stochasitic:

```math
dS_t = \mu_t S_t dt + \sqrt{\nu_t} S_t dW_{1,t}
```
```math
d\nu_t = -\lambda(\nu_t - \bar{\nu})dt + \eta\sqrt{\nu_t}dW_{2,t}
```
```math
dW_{1,t}, dW_{2,t} = \rho dt
```
Its discrete form formula will be used for model calibration and simulation, for details please refer to Euler and Milstein Discretization by F.D. Rouah.

### Snowball
"Snowball" covered by this model is one of the OTC equity derivatives with exotic structure. Its payoff, or redemption amount, is lineked to an index.

#### Knock out
Knock out barrier is usually higher than the initial index level and it influence both the redemption date and redemption amount.

Assumptions:
1. Knock out observation dates are specified.
2. Observation target is the closing price of each observation day.
3. Knock out barrier are specified for each observation date.

#### Knock in
Knock in barrier is usually lower than the initial index level and it will only influence the redemption amount.

Assumptions:
1. Knock in observation dates are all trading days during the life of the product.
2. Observation target is the closing price of each trading day.
3. Knock in barrier remains the same during the life of the product.

#### Scenarios
1. If knock out barrier is touched, the product will be terminated at redemption date (assumed to be the knock out date for simplicity) with redemption amount 1.
2. If knock out barrier is not touched and knock in barrier is touched, the product will be terminated at maturity with redemption amount 2.
3. If knock out barrier is not touched and knock in barrier is not touched, the product will be terminated at maturity with redemption amount 3.

### Comments
1. For simplicity, the market data and trade parameters are hard-coded. You may want to add a data processing module for practical use.
2. Pay attention that if you want to calculate greeks using this model, a seed should be specified in HestonPathGenerator.
3. Pay attention that if your interest rate curve is built using cubic interpolation method, this may result in the Heston calibrator not converging.

Reference: QuantLib-Python: Heston Monte Carlo Valuation for Autocallable Memory Coupon Note by Mikael Katajamäki,
available at http://mikejuniperhill.blogspot.com/2019/11/quantlib-python-heston-monte-carlo.html
