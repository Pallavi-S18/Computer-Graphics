import matplotlib.pyplot as plt

def midpoint_circle(xc, yc, r):
    points = []

    x = 0
    y = r
    p = 1 - r

    while x <= y:
        points.extend([
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y),
            (xc + y, yc + x),
            (xc - y, yc + x),
            (xc + y, yc - x),
            (xc - y, yc - x)
        ])

        x += 1

        if p < 0:
            p = p + 2 * x + 1
        else:
            y -= 1
            p = p + 2 * (x - y) + 1

    return points


xc = 0
yc = 0
r = 50

points = midpoint_circle(xc, yc, r)

x = [p[0] for p in points]
y = [p[1] for p in points]

plt.scatter(x, y)
plt.axis("equal")
plt.title("Midpoint Circle")
plt.show()