# snowball-pricing-heston-montecarlo

A snowball pricing model with Heston Monte Carlo simulation method, utilizing QuantLib.

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
