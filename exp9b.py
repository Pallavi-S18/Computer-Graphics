import matplotlib.pyplot as plt

# Clipping window
xmin, ymin = 2, 2
xmax, ymax = 8, 6


def liang_barsky(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [
        x1 - xmin,
        xmax - x1,
        y1 - ymin,
        ymax - y1
    ]

    t1 = 0.0
    t2 = 1.0

    for pi, qi in zip(p, q):

        if pi == 0:

            if qi < 0:
                return None

        else:

            t = qi / pi

            if pi < 0:
                t1 = max(t1, t)

            else:
                t2 = min(t2, t)

    if t1 > t2:
        return None

    nx1 = x1 + t1 * dx
    ny1 = y1 + t1 * dy

    nx2 = x1 + t2 * dx
    ny2 = y1 + t2 * dy

    return (nx1, ny1, nx2, ny2)


# Input line
x1, y1 = 1, 1
x2, y2 = 10, 8

# Apply Liang-Barsky
result = liang_barsky(x1, y1, x2, y2)

# Display
plt.figure(figsize=(7, 5))

plt.title("Liang-Barsky")

plt.plot(
    [x1, x2], [y1, y2],
    'r--',
    label="Original Line"
)

if result:
    lx1, ly1, lx2, ly2 = result

    plt.plot(
        [lx1, lx2], [ly1, ly2],
        'b',
        linewidth=3,
        label="Clipped Line"
    )

# Clipping window
plt.plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'k'
)

plt.xlim(0, 11)
plt.ylim(0, 9)
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.legend()

plt.show()