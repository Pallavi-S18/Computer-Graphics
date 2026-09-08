import pygame
import sys
import math

pygame.init()

# Window dimensions
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Transformations and Animation")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

# Initial position
x = 100
y = 300

# Transformation values
angle = 0
scale = 1.0

# Movement direction
dx = 3

running = True

while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill(WHITE)

    # Translation
    x += dx

    # Reverse direction at boundaries
    if x > WIDTH - 100 or x < 100:
        dx = -dx

    # Rotation
    angle += 2

    # Scaling
    scale = 1.0 + 0.3 * math.sin(angle * 0.05)

    # Create object
    size = int(100 * scale)

    object_surface = pygame.Surface((100, 100), pygame.SRCALPHA)

    # Draw a rectangle on the object surface
    pygame.draw.rect(
        object_surface,
        BLUE,
        (10, 10, 80, 80)
    )

    # Draw a circle
    pygame.draw.circle(
        object_surface,
        RED,
        (50, 50),
        20
    )

    # Apply rotation
    rotated_object = pygame.transform.rotate(
        object_surface,
        angle
    )

    # Apply scaling
    transformed_object = pygame.transform.smoothscale(
        rotated_object,
        (
            int(rotated_object.get_width() * scale),
            int(rotated_object.get_height() * scale)
        )
    )

    # Display transformed object
    rect = transformed_object.get_rect(
        center=(x, y)
    )

    screen.blit(transformed_object, rect)

    # Update display
    pygame.display.flip()

    # Control animation speed
    clock.tick(60)

pygame.quit()
sys.exit()