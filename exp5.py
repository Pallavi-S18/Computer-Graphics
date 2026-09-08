import matplotlib.pyplot as plt

x1, y1 = 2, 3
x2, y2 = 8, 6

dx = x2 - x1
dy = y2 - y1

steps = max(abs(dx), abs(dy))

x_inc = dx / steps
y_inc = dy / steps

x = x1
y = y1

pixels = []

for i in range(steps + 1):
    pixels.append((round(x), round(y)))
    x += x_inc
    y += y_inc

x_pixels = [p[0] for p in pixels]
y_pixels = [p[1] for p in pixels]

plt.scatter(x_pixels, y_pixels, s=50)
plt.plot(x_pixels, y_pixels, linestyle='--')
plt.title("DDA Line Drawing Algorithm")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.xticks(range(0, 11))
plt.yticks(range(0, 11))
plt.show()