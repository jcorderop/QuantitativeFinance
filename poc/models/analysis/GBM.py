'''
Geometrical brownian motion
'''
import matplotlib.pyplot as plt
import numpy as np

'''
S0  it is the initial value of the stock
T   time horizont
N   number of items to generate
mu  mean of the random walk
sigma   random fluctuation around the mean
        the size of the sigma is the size the fluctuation
'''
def simulate_geometric_random_walk(S0, T=2, N=1000, mu=0.1, sigma=0.05):
    dt = T/N
    # time-steps
    t = np.linspace(0, T, N)
    # standard normal distribution N(0,1)
    W = np.random.standard_normal(size=N)
    # N(0,dt) = sqrt(dt) * N(0,1)
    W = np.cumsum(W) * np.sqrt(dt)
    X = (mu - 0.5 * sigma ** 2) * t + sigma * W
    S = S0 * np.exp(X)

    return t, S


def plot_simulation(t, S):
    plt.plot(t, S)
    plt.xlabel('Time (t)')
    plt.ylabel('Stock Price S(t)')
    plt.title('Geometric Brownian Motion')
    plt.show()


if __name__ == '__main__':

    time, data = simulate_geometric_random_walk(1)
    plot_simulation(time, data)