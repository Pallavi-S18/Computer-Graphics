import numpy as np
import matplotlib.pyplot as plt

polygon = [(20,20), (40,20), (80,60), (50,80), (20,60)]

WIDTH = 100
HEIGHT = 100

def flood_fill(img, x, y, old, new):
    if old == new:
        return

    stack = [(x,y)]

    while stack:
        x,y = stack.pop()

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue

        if img[y,x] != old:
            continue

        img[y,x] = new

        stack.append((x+1,y))
        stack.append((x-1,y))
        stack.append((x,y+1))
        stack.append((x,y-1))

img = np.zeros((HEIGHT, WIDTH), dtype=int)

for i in range(len(polygon)):
    x1,y1 = polygon[i]
    x2,y2 = polygon[(i+1)%len(polygon)]

    steps = max(abs(x2-x1), abs(y2-y1))

    for i in range(steps+1):
        x = int(x1 + (x2-x1)*i / steps)
        y = int(y1 + (y2-y1)*i / steps)
        img[y,x] = 1

flood_fill(img, 50, 40, 0, 2)

fig, ax = plt.subplots(1,2, figsize=(10,5))

ax[0].imshow(img, origin="lower")
ax[0].set_title("Flood Fill")
ax[0].set_xlabel("x")
ax[0].set_ylabel("y")

plt.tight_layout()
plt.show()