import numpy as np
import matplotlib.pyplot as plt

P = np.array([
    [1, 1, 2],
    [2, 1, 4],
    [2, 2, 4],
    [1, 2, 2]
])

f = 2

x = f * P[:, 0] / P[:, 2]
y = f * P[:, 1] / P[:, 2]

fig = plt.figure(figsize=(10, 7))

ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(P[:, 0], P[:, 1], P[:, 2])
ax1.set_title("3D Points")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_zlabel("z")

ax2 = fig.add_subplot(122)
ax2.scatter(x, y)
ax2.set_title("Perspective Projection")
ax2.set_xlabel("x")
ax2.set_ylabel("y")
ax2.grid()

plt.show()