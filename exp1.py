import numpy as np
import matplotlib.pyplot as plt

P = np.array([
    [1, 1],
    [3, 1],
    [3, 3],
    [1, 3],
    [1, 1]
])

T = P + [2, 1]

S = P * 1.5

angle = np.radians(45)

R = np.array([
    [np.cos(angle), -np.sin(angle)],
    [np.sin(angle), np.cos(angle)]
])

Rot = P @ R.T

plt.plot(P[:, 0], P[:, 1], label="Original")
plt.plot(T[:, 0], T[:, 1], label="Translation")
plt.plot(S[:, 0], S[:, 1], label="Scaling")
plt.plot(Rot[:, 0], Rot[:, 1], label="Rotation")

plt.title("2D Geometric Transformations")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.grid()
plt.axis("equal")
plt.legend()
plt.show()