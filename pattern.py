import matplotlib.pyplot as plt
import numpy as np

# Size of the pattern
rows = 8
cols = 8

# Create empty grid
pattern = np.zeros((rows, cols))

# Pattern recognition and colouring
for i in range(rows):
    for j in range(cols):
        if (i + j) % 2 == 0:
            pattern[i][j] = 1
        else:
            pattern[i][j] = 0

# Display the pattern
plt.imshow(pattern, cmap="coolwarm")

# Add grid lines
plt.xticks(np.arange(-0.5, cols, 1))
plt.yticks(np.arange(-0.5, rows, 1))
plt.grid(color="black", linewidth=1)

plt.title("Pattern Recognition and Colouring")
plt.show()