import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10, 10, 100)

# Four lines
plt.plot(x, x, label="y = x")
plt.plot(x, -x, label="y = -x")
plt.plot(x, np.zeros_like(x), label="y = 0")

# x = 0 is a vertical line
plt.axvline(x=0, label="x = 0")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Star Pattern")
plt.grid(True)
plt.legend()
plt.show()