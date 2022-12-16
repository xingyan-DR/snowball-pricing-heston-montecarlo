import numpy as np
import QuantLib as ql

class Snowball():
    def __init__(self, effectiveDate, maturityDate, initialLevel,
                 notional, inBarrier, outBarrier, 
                 RedemptionFormula1, RedemptionFormula2, RedemptionFormula3, 
                 calendar, dayCounter, process, generator, nPaths, curveHandle):
        self.effectiveDate = effectiveDate
        self.maturityDate = maturityDate
        self.initialLevel = initialLevel
        self.notional = notional
        self.inBarrier = inBarrier
        self.outBarrier = outBarrier
        self.RedemptionFormula1 = RedemptionFormula1
        self.RedemptionFormula2 = RedemptionFormula2
        self.RedemptionFormula3 = RedemptionFormula3
        self.calendar = calendar
        self.dayCounter = dayCounter
        self.process = process
        self.generator = generator
        self.nPaths = nPaths
        self.curveHandle = curveHandle
    
    def pastKnockIn(self, pastFixings):
        if min(pastFixings) <= self.inBarrier * self.initialLevel:
            return True
        return False
    
    def pastKnockOut(self, pastFixings):
        for date in pastFixings.index:
            if date in self.outBarrier.index:
                fixing = pastFixings.loc[date].values[0]
                barrier = self.outBarrier.loc[date].values[0]
                if fixing >= barrier:
                    return True
        return False
    
    def valuation(self, valuationDate, pastFixings):
        if valuationDate >= self.maturityDate:
            return 0
        if self.pastKnockOut(pastFixings):
            return 0
        # create date array for path generator
        # in this case all trading dates between effective date and maturity date
        schedule = ql.Schedule(self.effectiveDate, self.maturityDate, ql.Period("1D"),
                               self.calendar, ql.ModifiedFollowing, ql.ModifiedFollowing,
                               ql.DateGeneration.Backward, False)
        # generate paths for a given set of dates, exclude the current spot rate
        paths = self.generator(schedule, self.dayCounter, self.process, self.nPaths)[:, 1:]
        
        # result accumulator
        global_pv = []
        
        # loop through all simulated paths
        for path in paths:
            payoffPV = 0.0
            KnockOut = False
            KnockIn = False
            
            # loop through set of coupon dates and index ratios
            for date, index in zip(schedule, (path / self.initialLevel)):
                payoff = 0
                # if knock out event has been triggered, immediate exit from this path
                if KnockOut:
                    break
                
                # payoff calculation at expiration
                if(date == self.maturityDate):
                    # If knock in event has been triggered
                    if KnockIn:
                        payoff = self.RedemptionFormula2(index * self.initialLevel)
                    # If knock in event has not been triggered
                    else:
                        payoff = self.RedemptionFormula3
                
                # payoff calculation before expiration
                else:
                    # check knock out condition
                    if date in self.outBarrier.index:
                        if index >= self.outBarrier.loc[date].values[0]:
                            KnockOut = True
                            payoff = self.RedemptionFormula1(date)
                    
                    if index <= self.inBarrier:
                        KnockIn = True

                # calculate and add PV to local accumulator
                if date > valuationDate:
                    if payoff != 0:
                        df = self.curveHandle.discount(date)
                        payoffPV += payoff * df
                
            # add path PV to global accumulator
            global_pv.append(payoffPV)
            
        # return PV
        return np.mean(np.array(global_pv))