import numpy as np
import matplotlib.pyplot as plt

# Center of the circles
h = 0
k = 0

# Radii
r_values = [20, 40, 60, 80, 100]

# Angle
theta = np.linspace(0, 2 * np.pi, 500)

# Draw concentric circles
for r in r_values:
    x = h + r * np.cos(theta)
    y = k + r * np.sin(theta)
    plt.plot(x, y, label=f"r = {r}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Concentric Circles")

plt.axis("equal")
plt.grid(True)
plt.legend()

plt.show()