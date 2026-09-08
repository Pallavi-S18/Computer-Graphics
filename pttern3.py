import matplotlib.pyplot as plt
import numpy as np

# Circle radius
R = 5

# Create figure
fig, ax = plt.subplots()

# Create grid
x = np.linspace(-R, R, 1000)
y = np.linspace(-R, R, 1000)

X, Y = np.meshgrid(x, y)

# Check points inside the circle
inside = X**2 + Y**2 <= R**2

# Slope of all parallel lines
m = 0.5

# Four parallel lines
c1 = -2
c2 = -1
c3 = 1
c4 = 2

# Empty array
Z = np.zeros_like(X)

# --------------------------------
# RED BAND 1
# Between line 1 and line 2
# --------------------------------
Z[
    (Y >= m * X + c1) &
    (Y < m * X + c2) &
    inside
] = 1

# --------------------------------
# RED BAND 2
# Between line 3 and line 4
# --------------------------------
Z[
    (Y >= m * X + c3) &
    (Y < m * X + c4) &
    inside
] = 1

# Fill only the red regions
ax.contourf(
    X,
    Y,
    Z,
    levels=[0.5, 1.5],
    colors=['red']
)

# --------------------------------
# Draw 4 parallel lines
# --------------------------------
for c in [c1, c2, c3, c4]:

    x_values = np.linspace(-R, R, 2000)

    # Equation: y = mx + c
    y_values = m * x_values + c

    # Keep only the part inside the circle
    mask = x_values**2 + y_values**2 <= R**2

    ax.plot(
        x_values[mask],
        y_values[mask],
        color='black',
        linewidth=2
    )

# --------------------------------
# Draw circle
# --------------------------------
circle = plt.Circle(
    (0, 0),
    R,
    fill=False,
    color='black',
    linewidth=2
)

ax.add_patch(circle)

# --------------------------------
# Graph settings
# --------------------------------
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")

ax.set_aspect('equal')
ax.grid(True)

plt.title("Pattern Recognition and Colouring")

plt.show()