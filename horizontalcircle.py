import numpy as np
import matplotlib.pyplot as plt

# Horizontal center positions
h_values = [-200, -100, 0, 100, 200]

# Radius
r = 50

# Angle
theta = np.linspace(0, 2 * np.pi, 500)

# Draw circles
for h in h_values:
    x = h + r * np.cos(theta)
    y = r * np.sin(theta)
    plt.plot(x, y, label=f"h = {h}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Circles Along Horizontal Axis")

plt.axis("equal")
plt.grid(True)
plt.legend()

plt.show()