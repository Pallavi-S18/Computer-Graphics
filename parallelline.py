import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10, 10, 100)

c_values = [-5, -2, 0, 5, 2]

for c in c_values:
    y = 2 * x + c
    plt.plot(x, y, label=f"y = 2x + {c}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Family of Parallel Lines")
plt.grid(True)
plt.legend()
plt.show()