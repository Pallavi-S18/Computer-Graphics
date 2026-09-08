import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------
# PARAMETERS
# ---------------------------------------

R = 2.5
d = R

# Same intensity everywhere
intensity = 1.0

# ---------------------------------------
# CREATE FIGURE
# ---------------------------------------

fig, ax = plt.subplots()

# ---------------------------------------
# CREATE COORDINATE GRID
# ---------------------------------------

x = np.linspace(-5.5, 5.5, 1200)
y = np.linspace(-5.5, 5.5, 1200)

X, Y = np.meshgrid(x, y)

# ---------------------------------------
# CENTRE CIRCLE
# ---------------------------------------

middle_circle = X**2 + Y**2 <= R**2

# ---------------------------------------
# CENTRES OF SIX OUTER CIRCLES
# ---------------------------------------

centres = []

for angle in range(0, 360, 60):

    a = np.radians(angle)

    h = d * np.cos(a)
    k = d * np.sin(a)

    centres.append((h, k))

# ---------------------------------------
# OUTER CIRCLE COLOURS
# ---------------------------------------

# 0°   RIGHT        = RED
# 60°  UPPER-RIGHT  = BLUE
# 120° UPPER-LEFT   = GREEN
# 180° LEFT         = ORANGE
# 240° LOWER-LEFT   = PURPLE
# 300° LOWER-RIGHT  = LIGHT BLUE

outer_colours = [
    'red',
    'blue',
    'green',
    'orange',
    'purple',
    'lightskyblue'
]

# ---------------------------------------
# COLOUR OUTER CIRCLES
# ---------------------------------------

owner = np.full(X.shape, -1, dtype=int)

for i, (h, k) in enumerate(centres):

    current_circle = (
        (X - h)**2 + (Y - k)**2 <= R**2
    )

    # Do not colour the middle circle
    current_circle = current_circle & (~middle_circle)

    # Give each point only one colour
    current_circle = current_circle & (owner == -1)

    owner[current_circle] = i

# Apply colours
for i in range(6):

    mask = owner == i

    ax.contourf(
        X,
        Y,
        mask.astype(int),
        levels=[0.5, 1.5],
        colors=[outer_colours[i]],
        alpha=intensity
    )

# ---------------------------------------
# CREATE 6 SEPARATE YELLOW PETALS
# ---------------------------------------

for i in range(6):

    # Two neighbouring outer circles
    h1, k1 = centres[i]
    h2, k2 = centres[(i + 1) % 6]

    circle1 = (
        (X - h1)**2 + (Y - k1)**2 <= R**2
    )

    circle2 = (
        (X - h2)**2 + (Y - k2)**2 <= R**2
    )

    # Find the other four circles
    other_circles = np.zeros_like(X, dtype=bool)

    for j in range(6):

        if j != i and j != (i + 1) % 6:

            h, k = centres[j]

            other = (
                (X - h)**2 + (Y - k)**2 <= R**2
            )

            other_circles = other_circles | other

    # -----------------------------------
    # PETAL CONDITION
    # -----------------------------------
    #
    # Inside middle circle
    # AND inside two neighbouring circles
    # AND outside the other four circles
    #

    petal = (
        middle_circle
        & circle1
        & circle2
        & (~other_circles)
    )

    # Fill the petal yellow
    ax.contourf(
        X,
        Y,
        petal.astype(int),
        levels=[0.5, 1.5],
        colors=['yellow'],
        alpha=intensity
    )

# ---------------------------------------
# DRAW ALL 7 CIRCLE BOUNDARIES
# ---------------------------------------

theta = np.linspace(0, 2 * np.pi, 1000)

# Middle circle
x_circle = R * np.cos(theta)
y_circle = R * np.sin(theta)

ax.plot(
    x_circle,
    y_circle,
    color='black',
    linewidth=1.5
)

# Six outer circles
for h, k in centres:

    x_circle = h + R * np.cos(theta)
    y_circle = k + R * np.sin(theta)

    ax.plot(
        x_circle,
        y_circle,
        color='black',
        linewidth=1.5
    )

# ---------------------------------------
# GRAPH SETTINGS
# ---------------------------------------

ax.set_aspect('equal')

ax.set_xlim(-5.5, 5.5)
ax.set_ylim(-5.5, 5.5)

ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")

ax.grid(True)

plt.title("Seven Circle Pattern with Coloured Petals")

plt.show()