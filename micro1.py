import numpy as np
import matplotlib.pyplot as plt


# -----------------------------------------
# Transformation Matrices
# -----------------------------------------

def translation(tx, ty):
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ], dtype=float)


def rotation(angle):
    theta = np.radians(angle)

    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0, 0, 1]
    ], dtype=float)


def scaling(sx, sy):
    return np.array([
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ], dtype=float)


# -----------------------------------------
# Apply Transformation
# -----------------------------------------

def apply_transformation(points, matrix):

    ones = np.ones((1, points.shape[1]))

    homogeneous_points = np.vstack((points, ones))

    transformed = matrix @ homogeneous_points

    return transformed[:2, :]


# -----------------------------------------
# Display Object
# -----------------------------------------

def display_object(original, transformed, title):

    plt.figure(figsize=(8, 6))

    # Original object
    plt.plot(
        np.append(original[0], original[0][0]),
        np.append(original[1], original[1][0]),
        'b--',
        linewidth=2,
        label="Original Object"
    )

    # Transformed object
    plt.plot(
        np.append(transformed[0], transformed[0][0]),
        np.append(transformed[1], transformed[1][0]),
        'r-',
        linewidth=2,
        label="Transformed Object"
    )

    # Axes
    plt.axhline(0)
    plt.axvline(0)

    plt.grid(True)
    plt.axis("equal")

    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    plt.title(title)

    plt.legend()

    plt.show()


# -----------------------------------------
# MAIN PROGRAM
# -----------------------------------------

print("==============================================")
print(" Sequential Geometric Transformation Visualizer")
print("==============================================")


# Original Triangle
original = np.array([
    [1, 4, 2],
    [1, 1, 3]
], dtype=float)


# Current object
current = original.copy()


# Composite matrix
composite_matrix = np.eye(3)


step = 1


while True:

    print("\n==============================================")
    print("STEP", step)
    print("==============================================")

    print("1. Translation")
    print("2. Rotation")
    print("3. Scaling")

    choice = int(input("Enter your choice (1/2/3): "))


    # -----------------------------------------
    # Translation
    # -----------------------------------------

    if choice == 1:

        tx = float(input("Enter Tx (translation in X): "))
        ty = float(input("Enter Ty (translation in Y): "))

        matrix = translation(tx, ty)

        transformation_name = (
            f"Translation (Tx={tx}, Ty={ty})"
        )


    # -----------------------------------------
    # Rotation
    # -----------------------------------------

    elif choice == 2:

        angle = float(input("Enter rotation angle: "))

        matrix = rotation(angle)

        transformation_name = (
            f"Rotation ({angle} degrees)"
        )


    # -----------------------------------------
    # Scaling
    # -----------------------------------------

    elif choice == 3:

        sx = float(input("Enter Sx (scaling in X): "))
        sy = float(input("Enter Sy (scaling in Y): "))

        matrix = scaling(sx, sy)

        transformation_name = (
            f"Scaling (Sx={sx}, Sy={sy})"
        )


    else:

        print("Invalid choice!")
        continue


    # -----------------------------------------
    # Apply transformation to CURRENT object
    # -----------------------------------------

    current = apply_transformation(current, matrix)


    # -----------------------------------------
    # Update Composite Matrix
    # -----------------------------------------

    composite_matrix = matrix @ composite_matrix


    # -----------------------------------------
    # Print information
    # -----------------------------------------

    print("\n----------------------------------------------")
    print("Step", step, ":", transformation_name)
    print("----------------------------------------------")

    print("\nTransformation Matrix:")

    print(matrix)

    print("\nCurrent Object Coordinates:")

    print(current)


    # -----------------------------------------
    # Display current step
    # -----------------------------------------

    display_object(
        original,
        current,
        f"Step {step}: {transformation_name}"
    )


    # -----------------------------------------
    # Increase step number
    # -----------------------------------------

    step = step + 1


    # -----------------------------------------
    # Ask for another transformation
    # -----------------------------------------

    again = input(
        "\nDo you want to apply another transformation? (y/n): "
    )


    if again.lower() != "y":

        break


# -----------------------------------------
# FINAL RESULT
# -----------------------------------------

print("\n==============================================")
print("FINAL COMPOSITE TRANSFORMATION")
print("==============================================")


print("\nComposite Transformation Matrix:")

print(composite_matrix)


print("\nFinal Object Coordinates:")

print(current)


# Final graph

display_object(
    original,
    current,
    "Final Composite Transformation"
)


print("\nProgram Completed Successfully!")