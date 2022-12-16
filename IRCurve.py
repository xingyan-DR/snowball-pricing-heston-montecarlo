import QuantLib as ql

class SOFR:
    def __init__(self, depositRates, swapRates, valuationDate):
        self.depositRates = depositRates.copy()
        self.swapRates = swapRates.copy()
        self.valuationDate = valuationDate
        self.curveHandle = self.build_curve()
    
    def build_curve(self):
        calendar = ql.UnitedStates()
        index = ql.Sofr()
        depo_helpers = [ql.DepositRateHelper(ql.QuoteHandle(ql.SimpleQuote(self.depositRates.loc[idx, "Rate"])),
                                        ql.Period(self.depositRates.loc[idx, "Tenor"]),
                                        2, calendar, ql.ModifiedFollowing, False, ql.Actual360())
                   for idx in self.depositRates.index]
        swap_helpers = [ql.OISRateHelper(2, ql.Period(self.swapRates.loc[idx, "Tenor"]),
                                              ql.QuoteHandle(ql.SimpleQuote(self.swapRates.loc[idx, "Rate"])), index)
                             for idx in self.swapRates.index]
        helpers = depo_helpers + swap_helpers
        curve = ql.PiecewiseLogLinearDiscount(self.valuationDate, helpers, ql.Actual360())
        curve.enableExtrapolation()
        # discounting curve
        curveHandle = ql.YieldTermStructureHandle(curve)
        index = ql.Sofr(curveHandle)
        
        # for idx in self.fixings.index:
        #     date = self.fixings.loc[idx, "Date"]
        #     if self.caldndar.isBusinessDay(date):
        #         index.addFixing(date, self.fixings.loc[idx, "Rate"], True)
        
        return curveHandle

