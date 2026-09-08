import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10, 10, 100)

m_values = [-3, -2, -1, 0, 1, 2, 3]

for m in m_values:
    y = m * x
    plt.plot(x, y, label=f"y = {m}x")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Fan Pattern")
plt.grid(True)
plt.legend()
plt.show()