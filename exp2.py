import numpy as np
import matplotlib.pyplot as plt

P = np.array([
    [1, 1, 1],
    [4, 1, 1],
    [2, 4, 1]
])

Rx = np.array([
    [1, 0, 0],
    [0, -1, 0],
    [0, 0, 1]
])

Ry = np.array([
    [-1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
])

Shx = np.array([
    [1, 1, 0],
    [0, 1, 0],
    [0, 0, 1]
])

Shy = np.array([
    [1, 0, 0],
    [1, 1, 0],
    [0, 0, 1]
])

objects = [
    ("original", P),
    ("Reflection x", Rx @ P),
    ("Reflection y", Ry @ P),
    ("Shearing x", Shx @ P),
    ("Shearing y", Shy @ P)
]

fig, axes = plt.subplots(1, 5, figsize=(15, 4))

for ax, (title, obj) in zip(axes, objects):
    x = list(obj[0]) + [obj[0][0]]
    y = list(obj[1]) + [obj[1][0]]
    ax.plot(x, y, marker='o')
    ax.set_title(title)
    ax.axhline(0)
    ax.axvline(0)
    ax.grid(True)
    ax.set_aspect('equal')

plt.tight_layout()
plt.show()