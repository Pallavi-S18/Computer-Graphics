import numpy as np
import matplotlib.pyplot as plt

# Center
b = 0
k = 0

# Initial radius
r0 = 60

# Decrease in radius
n = 10

# Values of i
for i in range(5):
    r = r0 - i * n

    theta = np.linspace(0, 2 * np.pi, 500)

    x = b + r * np.cos(theta)
    y = k + r * np.sin(theta)

    plt.plot(x, y, label=f"i = {i}, r = {r}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Decreasing Size Circles")

plt.axis("equal")
plt.grid(True)
plt.legend()

plt.show()