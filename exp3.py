import numpy as np
import matplotlib.pyplot as plt

P = np.array([
    [1, 1, 1],
    [4, 1, 1],
    [2, 3, 1]
])

T = np.array([
    [1, 0, 2],
    [0, 1, 1],
    [0, 0, 1]
])

S = np.array([
    [2, 0, 0],
    [0, 2, 0],
    [0, 0, 1]
])

angle = np.radians(45)

R = np.array([
    [np.cos(angle), -np.sin(angle), 0],
    [np.sin(angle), np.cos(angle), 0],
    [0, 0, 1]
])

# Apply transformations
P_scaled = S @ P.T
P_rotated = R @ P_scaled
P_translated = T @ P_rotated

# Convert back to coordinates
P_scaled = P_scaled.T
P_rotated = P_rotated.T
P_translated = P_translated.T

# Plot
fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(
    P[:, 0],
    P[:, 1],
    marker='o',
    label='Original'
)

ax.plot(
    P_scaled[:, 0],
    P_scaled[:, 1],
    marker='o',
    label='Scale'
)

ax.plot(
    P_rotated[:, 0],
    P_rotated[:, 1],
    marker='o',
    label='Rotate'
)

ax.plot(
    P_translated[:, 0],
    P_translated[:, 1],
    marker='o',
    label='Translate'
)

ax.set_title('Composite and Affine Transformation')
ax.axhline(0)
ax.axvline(0)
ax.grid(True)
ax.set_aspect('equal')

plt.legend()
plt.show()