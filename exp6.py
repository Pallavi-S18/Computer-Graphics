import matplotlib.pyplot as plt

x1, y1 = 1, 2
x2, y2 = 9, 7

dx = x2 - x1
dy = y2 - y1

x = x1
y = y1

p = 2 * dy - dx

pixels = []

while x <= x2:

    pixels.append((x, y))

    x = x + 1

    if p < 0:
        p = p + 2 * dy
    else:
        y = y + 1
        p = p + 2 * dy - 2 * dx

plt.plot(
    [p[0] for p in pixels],
    [p[1] for p in pixels],
    marker='o'
)

plt.title("Bresenham's Line Drawing Algorithm")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.grid(True)
plt.show()
