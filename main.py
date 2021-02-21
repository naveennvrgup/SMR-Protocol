import numpy as np
import matplotlib.pyplot as plt

plt.axis([0, 1, 0, 1])

for i in range(1000):
    x = np.random.random()
    y = np.random.random()
    plt.scatter(x, y)
    plt.pause(0.05)

plt.show()