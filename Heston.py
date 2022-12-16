import numpy as np
import QuantLib as ql

def HestonPathGenerator(dates, dayCounter, process, nPaths):
    '''
    Parameters
    ----------
    dates : QuantLib date
        Dates on the path.
    dayCounter : QuantLib dayCounter
    process : ql.HestonProcess
    nPaths : FLOAT
        The number of simulations.
    '''
    t = np.array([dayCounter.yearFraction(dates[0], d) for d in dates])
    nGridSteps = (t.shape[0] - 1) * 2
    sequenceGenerator = ql.UniformRandomSequenceGenerator(nGridSteps, ql.UniformRandomGenerator())
    gaussianSequenceGenerator = ql.GaussianRandomSequenceGenerator(sequenceGenerator)
    pathGenerator = ql.GaussianMultiPathGenerator(process, t, gaussianSequenceGenerator, False)
    paths = np.zeros(shape = (nPaths, t.shape[0]))
    
    for i in range(nPaths):
        multiPath = pathGenerator.next().value()
        paths[i,:] = np.array(list(multiPath[0]))
        
    # return array dimensions: [number of paths, number of items in t array]
    return paths


def HestonModelCalibrator(valuationDate, calendar, spot, curveHandle, dividendHandle,
                          v0, kappa, theta, sigma, rho, expiration_dates, 
                          strikes, data, optimizer, bounds):
    '''

    Parameters
    ----------
    valuationDate : QuantLib date
    calendar : QuantLib calendar
    spot : FLOAT
        Spot price of the index at valuation date.
    curveHandle : ql YieldTermStructureHandle
        The yield curve.
    dividendHandle : YieldTermStructureHandle
        The dividend curve.
    v0, kappa, theta, sigma, rho : FLOAT
        Initial parameters of the Heston process.
    expiration_dates : QuantLib date
        Expiration dates on the market volatility surface.
    strikes : FLOAT
        Strikes on the market volatility surface.
    data : LIST of LIST
        Volatility surface data.
    optimizer : FUNCTION
        Scipy optimizer.
    bounds : LIST of TUPLES
        Parameter bounds.

    Returns
    -------
    ql.HestonProcess
        The calibrated Heston process.
    ql.HestonModel
        The calibrated Heston model.

    '''
    
    # container for heston calibration helpers
    helpers = []
    
    # create Heston process, model and pricing engine
    # use given initial parameters for model
    process = ql.HestonProcess(curveHandle, dividendHandle,
                               ql.QuoteHandle(ql.SimpleQuote(spot)), 
                               v0, kappa, theta, sigma, rho)
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model)
    
    # nested cost function for model optimization
    def CostFunction(x):
        parameters = ql.Array(list(x))        
        model.setParams(parameters)
        error = [helper.calibrationError() for helper in helpers]
        return np.sqrt(np.sum(np.abs(error)))

    # create Heston calibration helpers, set pricing engines
    for i in range(len(expiration_dates)):
        for j in range(len(strikes)):
            expiration = expiration_dates[i]
            days = expiration - valuationDate
            period = ql.Period(days, ql.Days)
            vol = data[i][j]
            strike = strikes[j]
            helper = ql.HestonModelHelper(period, calendar, spot, strike,
                ql.QuoteHandle(ql.SimpleQuote(vol)), curveHandle, dividendHandle)
            helper.setPricingEngine(engine)
            helpers.append(helper)
    
    # run optimization, return calibrated model and process
    optimizer(CostFunction, bounds)
    return process, model