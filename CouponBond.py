from ZeroCouponBond import ZeroCouponBond


class CouponBond(ZeroCouponBond):

    def __init__(self, principal, coupon_rate, maturity, interest_rate):
        super().__init__(principal, maturity, interest_rate)
        # rate of the bond
        self.coupon_rate = coupon_rate / 100

    def coupons(self, model):
        price_payments = 0
        amount = (self.principal * self.coupon_rate)
        for t in range(1, self.maturity + 1):
            coupon = model(amount, t, self.interest_rate)
            print("Period [%s] coupon payment: %.2f" % (t, coupon))
            price_payments += coupon
        print("Discount coupons payments: %.2f" % price_payments)
        return price_payments

    def calculate_discrete_price(self):
        # discount the coupons payments
        price_payments = self.coupons(self.discrete_present_value)

        # discount present value
        present_value = self.discrete_present_value(self.principal, self.maturity, self.interest_rate)

        return price_payments + present_value

    def calculate_continue_price(self):
        # discount the coupons payments
        price_payments = self.coupons(self.continues_present_value)

        # discount present value
        present_value = self.continues_present_value(self.principal, self.maturity, self.interest_rate)

        return price_payments + present_value

if __name__ == '__main__':
    # investment in dollars
    nominal = 1000
    # duration (years)
    maturity = 3
    # define the interest rate (r) in %
    interest_rate = 4
    # coupon rate in %
    coupon_rate = 10

    bond = CouponBond(nominal, coupon_rate, maturity, interest_rate)
    print("Coupon Bond Price: %.2f" % bond.calculate_discrete_price())

    print("Coupon Bond Price: %.2f" % bond.calculate_continue_price())