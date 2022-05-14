from math import exp

class ZeroCouponBond(object):

    def __init__(self, principal, maturity, interest_rate):
        # principal amount / nominal
        self.principal = principal
        # date to mature
        self.maturity = maturity
        # market interest rate (discounting)
        self.interest_rate = interest_rate / 100

    '''
    (  x  )/((1+ r)^n )
    x = principal
    n = maturity is the period in years
    '''
    def discrete_present_value(self, principal, maturity, interest_rate):
        return principal / ((1 + interest_rate) ** maturity)

    def continues_present_value(self, principal, maturity, interest_rate):
        return principal * exp(-interest_rate * maturity)


    def calculate_discrete_price(self):
        return self.discrete_present_value(self.principal, self.maturity, self.interest_rate)

    def calculate_continue_price(self):
        return self.continues_present_value(self.principal, self.maturity, self.interest_rate)

if __name__ == '__main__':
    # investment in dollars
    nominal = 1000
    # duration (years)
    maturity = 2
    # define the interest rate (r) in %
    interest_rate = 4

    bond = ZeroCouponBond(nominal, maturity, interest_rate)
    print("Discrete Zero Coupon Bond Price: %.2f" % bond.calculate_discrete_price())

    bond = ZeroCouponBond(nominal, maturity, interest_rate)
    print("Continues Zero Coupon Bond Price: %.2f" % bond.calculate_continue_price())