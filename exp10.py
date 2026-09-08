import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw


# ---------------- CLIPPING WINDOW ----------------

xmin, ymin = 2, 2
xmax, ymax = 8, 7


# ---------------- ORIGINAL POLYGON ----------------

polygon = [
    (1, 3),
    (4, 1),
    (9, 3),
    (7, 8),
    (3, 7)
]


# ---------------- SUTHERLAND-HODGMAN ----------------

def inside(point, edge):

    x, y = point

    if edge == "left":
        return x >= xmin

    elif edge == "right":
        return x <= xmax

    elif edge == "bottom":
        return y >= ymin

    elif edge == "top":
        return y <= ymax


def intersection(p1, p2, edge):

    x1, y1 = p1
    x2, y2 = p2

    if edge == "left":
        x = xmin
        y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)

    elif edge == "right":
        x = xmax
        y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)

    elif edge == "bottom":
        y = ymin
        x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)

    elif edge == "top":
        y = ymax
        x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)

    return (x, y)


def clip_polygon(poly, edge):

    output = []

    if len(poly) == 0:
        return output

    s = poly[-1]

    for e in poly:

        s_inside = inside(s, edge)
        e_inside = inside(e, edge)

        # Case 1: Outside -> Inside
        if not s_inside and e_inside:
            output.append(intersection(s, e, edge))
            output.append(e)

        # Case 2: Inside -> Inside
        elif s_inside and e_inside:
            output.append(e)

        # Case 3: Inside -> Outside
        elif s_inside and not e_inside:
            output.append(intersection(s, e, edge))

        # Case 4: Outside -> Outside
        # Add nothing

        s = e

    return output


def sutherland_hodgman(poly):

    edges = ["left", "right", "bottom", "top"]

    for edge in edges:
        poly = clip_polygon(poly, edge)

    return poly


clipped_polygon = sutherland_hodgman(polygon)


# ---------------- ANTIALIASING ----------------

def draw_antialiased_polygon(poly):

    scale = 4

    width = 500
    height = 500

    image = Image.new(
        "RGB",
        (width * scale, height * scale),
        "white"
    )

    draw = ImageDraw.Draw(image)

    points = []

    for x, y in poly:
        px = int(x * 50 * scale)
        py = int((10 - y) * 50 * scale)
        points.append((px, py))

    draw.polygon(
        points,
        fill="skyblue",
        outline="black"
    )

    # Downsample for antialiasing
    image = image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )

    return image


# ---------------- DISPLAY ----------------

fig, ax = plt.subplots(1, 2, figsize=(12, 5))


# Original polygon
original_x = [p[0] for p in polygon] + [polygon[0][0]]
original_y = [p[1] for p in polygon] + [polygon[0][1]]

ax[0].plot(
    original_x,
    original_y,
    'b-o'
)

ax[0].plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'r-'
)

ax[0].set_title("Original Polygon")
ax[0].set_xlabel("X")
ax[0].set_ylabel("Y")
ax[0].set_xlim(0, 10)
ax[0].set_ylim(0, 10)
ax[0].grid(True)


# Clipped polygon
if clipped_polygon:

    clipped_x = [
        p[0] for p in clipped_polygon
    ] + [clipped_polygon[0][0]]

    clipped_y = [
        p[1] for p in clipped_polygon
    ] + [clipped_polygon[0][1]]

    ax[1].plot(
        clipped_x,
        clipped_y,
        'b-o',
        linewidth=2
    )

ax[1].plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    'r-'
)

ax[1].set_title("Sutherland-Hodgman Clipped Polygon")
ax[1].set_xlabel("X")
ax[1].set_ylabel("Y")
ax[1].set_xlim(0, 10)
ax[1].set_ylim(0, 10)
ax[1].grid(True)

plt.tight_layout()
plt.show()


# Display antialiased polygon
if clipped_polygon:

    aa_image = draw_antialiased_polygon(clipped_polygon)

    plt.figure(figsize=(6, 6))
    plt.imshow(aa_image)
    plt.title("Antialiased Clipped Polygon")
    plt.axis("off")
    plt.show()