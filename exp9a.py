import matplotlib.pyplot as plt

# Clipping window
xmin, ymin = 2, 2
xmax, ymax = 8, 6

# Region codes
INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def compute_code(x, y):
    code = INSIDE

    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT

    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP

    return code


def cohen_sutherland(x1, y1, x2, y2):

    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)

    while True:

        if code1 == 0 and code2 == 0:
            return (x1, y1, x2, y2)

        elif (code1 & code2) != 0:
            return None

        else:

            if code1 != 0:
                code = code1
            else:
                code = code2

            if code & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax

            elif code & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin

            elif code & RIGHT:
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax

            elif code & LEFT:
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            if code == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)


# Input line
x1, y1 = 1, 1
x2, y2 = 10, 8

# Apply Cohen-Sutherland
result = cohen_sutherland(x1, y1, x2, y2)

# Display
plt.figure(figsize=(7, 5))

plt.title("Cohen-Sutherland")

plt.plot(
    [x1, x2], [y1, y2],
    'r--',
    label="Original Line"
)

if result:
    cx1, cy1, cx2, cy2 = result

    plt.plot(
        [cx1, cx2], [cy1, cy2],
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