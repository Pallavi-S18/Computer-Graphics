import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10, 10, 100)

m_values = [-2, -1, 0, 1, 2]
c = 0

for m in m_values:
    y = m * x + c
    plt.plot(x, y, label=f"y = {m}x + {c}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Family of Lines - Different Slopes")
plt.grid(True)
plt.legend()
plt.show()