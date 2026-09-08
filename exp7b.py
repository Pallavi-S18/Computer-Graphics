import matplotlib.pyplot as plt

def midpoint_ellipse(xc, yc, rx, ry):
    points = []

    x = 0
    y = ry

    rx2 = rx * rx
    ry2 = ry * ry

    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    p1 = ry2 - rx2 * ry + 0.25 * rx2

    while dx < dy:
        points.extend([
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y)
        ])

        x += 1
        dx = 2 * ry2 * x

        if p1 < 0:
            p1 += dx + ry2
        else:
            y -= 1
            dy = 2 * rx2 * y
            p1 += dx - dy + ry2

    p2 = (
        ry2 * (x + 0.5) ** 2
        + rx2 * (y - 1) ** 2
        - rx2 * ry2
    )

    while y >= 0:
        points.extend([
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y)
        ])

        y -= 1
        dy = 2 * rx2 * y

        if p2 > 0:
            p2 += rx2 - dy
        else:
            x += 1
            dx = 2 * ry2 * x
            p2 += dx - dy + rx2

    return points


xc = 0
yc = 0
rx = 80
ry = 50

points = midpoint_ellipse(xc, yc, rx, ry)

x = [p[0] for p in points]
y = [p[1] for p in points]

plt.scatter(x, y)
plt.axis("equal")
plt.title("Midpoint Ellipse")
plt.show()