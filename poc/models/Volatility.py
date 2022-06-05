import pandas as pd
import numpy as np

# https://corporatefinanceinstitute.com/resources/knowledge/strategy/asset-allocation/
# https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/volatility-vol/
def price_move():
    prices = {}
    prices['close'] = [10,12,9,14]
    data = pd.DataFrame(prices)
    data['diff'] = data - data.mean()
    data['sqrt'] = data['diff']**2
    print("data:",data)
    print("std:",np.sqrt(data['sqrt'].mean()))
    print('finished...')

def price_move_pct():
    prices = {}
    prices['close'] = [10, 12, 9, 14]
    data = pd.DataFrame(prices)
    #data['diff'] = np.log(1 + data.pct_change())
    data['diff'] = data.pct_change()
    data['sqrt'] = data['diff']**2
    print("data:",data)
    print("std:",np.sqrt(data['sqrt'].mean()))
    print('finished...')

def price_mean():
    prices = {}
    prices['close'] = [0.15, -0.09, 0.1, 0.06]
    data = pd.DataFrame(prices)
    mean = data.mean()
    print("mean:", mean)
    std = data.std()
    print("std:",std)

price_mean()