from math import exp

'''
x(1+r)n
	    r: interest rate (0.05 for 5%)
        n: number of days
'''
def future_discrete_value(amount, interest_rate, periods_years):
    return amount * (1 + interest_rate) ** periods_years

'''
considering that has a cash flow in the future

x / (1+r)n
	    r: interest rate (0.05 for 5%)
        n: number of days
'''
def present_discrete_value(amount, interest_rate, periods_years):
    return amount * (1 + interest_rate) ** -periods_years


def future_continues_value(amount, interest_rate, time):
    return amount * exp(interest_rate * time)

def present_continues_value(amount, interest_rate, time):
    return amount * exp(-interest_rate * time)

if __name__ == '__main__':
    # investment in dollars
    amount = 100
    # define the interest rate (r)
    interest_rate = 0.05
    # duration (years)
    periods_years = 5

    print("Future value (discrete model) of   x: %s" % future_discrete_value(amount, interest_rate, periods_years))
    print("Present value (discrete model) value of  x: %s" % present_discrete_value(amount, interest_rate, periods_years))
    print("Future value (continues model) value of  x: %s" % future_continues_value(amount, interest_rate, periods_years))
    print("Present value (continues model) value of x: %s" % present_continues_value(amount, interest_rate, periods_years))