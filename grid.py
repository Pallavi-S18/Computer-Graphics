import numpy as np
import matplotlib.pyplot as plt

k_values = range(-5, 6)

# Vertical lines: x = k
for k in k_values:
    plt.axvline(x=k, label=f"x = {k}")

# Horizontal lines: y = k
for k in k_values:
    plt.axhline(y=k, label=f"y = {k}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Grid Pattern")
plt.xlim(-6, 6)
plt.ylim(-6, 6)
plt.grid(False)

plt.show()