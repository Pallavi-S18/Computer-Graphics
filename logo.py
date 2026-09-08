import tkinter as tk
import math

# -------------------------------
# WINDOW
# -------------------------------
root = tk.Tk()
root.title("ASAC - Computer Science and Engineering")
root.geometry("900x750")
root.configure(bg="white")

canvas = tk.Canvas(
    root,
    width=900,
    height=750,
    bg="white",
    highlightthickness=0
)
canvas.pack()


# ==================================================
# 1. MAIN COMPUTER CHIP - RECTANGLE
# ==================================================

canvas.create_rectangle(
    270, 100, 630, 460,
    outline="black",
    width=6
)

# Inner chip
canvas.create_rectangle(
    300, 130, 600, 430,
    outline="black",
    width=3
)


# ==================================================
# 2. CHIP PINS - LINES
# ==================================================

# Top pins
for x in range(330, 571, 60):
    canvas.create_line(x, 100, x, 60, width=5)

# Bottom pins
for x in range(330, 571, 60):
    canvas.create_line(x, 460, x, 500, width=5)

# Left pins
for y in range(160, 421, 60):
    canvas.create_line(270, y, 230, y, width=5)

# Right pins
for y in range(160, 421, 60):
    canvas.create_line(630, y, 670, y, width=5)


# ==================================================
# 3. CENTRAL CIRCLE - PROCESSING CORE
# ==================================================

canvas.create_oval(
    350, 200, 550, 400,
    outline="black",
    width=6
)


# ==================================================
# 4. TRIANGLE - A / INNOVATION SYMBOL
# ==================================================

canvas.create_polygon(
    450, 230,
    390, 340,
    510, 340,
    outline="black",
    fill="white",
    width=5
)

# Triangle inner line
canvas.create_line(
    420, 300,
    480, 300,
    width=5
)


# ==================================================
# 5. ELLIPSE - DIGITAL ORBIT
# ==================================================

canvas.create_oval(
    330, 245, 570, 385,
    outline="black",
    width=3
)


# ==================================================
# 6. CIRCUIT NODES
# ==================================================

nodes = [
    (330, 160),
    (570, 160),
    (330, 400),
    (570, 400)
]

for x, y in nodes:
    canvas.create_oval(
        x - 7, y - 7,
        x + 7, y + 7,
        fill="black"
    )


# ==================================================
# 7. ASAC
# ==================================================

canvas.create_text(
    450, 535,
    text="ASAC",
    font=("Arial", 55, "bold"),
    fill="black"
)


# ==================================================
# 8. COMPUTER SCIENCE & ENGINEERING
# ==================================================

canvas.create_text(
    450, 600,
    text="COMPUTER SCIENCE & ENGINEERING",
    font=("Arial", 19, "bold"),
    fill="black"
)


# ==================================================
# KEEP WINDOW OPEN
# ==================================================

root.mainloop()