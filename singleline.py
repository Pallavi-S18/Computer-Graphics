import matplotlib.pyplot as plt

# Values of x
x = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]

# Calculate y = 2x + 1
y = [2*i + 1 for i in x]

# Draw the line
plt.plot(x, y)

# Labels and title
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("Graph of y = 2x + 1")

# Show grid
plt.grid(True)

# Display graph
plt.show()