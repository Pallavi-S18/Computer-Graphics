import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basic Geometric Primitives")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

running = True

while running:

    screen.fill(WHITE)

    # 1. Draw a red line
    pygame.draw.line(
        screen,
        RED,
        (100, 100),
        (300, 100),
        5
    )

    # 2. Draw a blue circle
    pygame.draw.circle(
        screen,
        BLUE,
        (200, 220),
        60
    )

    # 3. Draw a green rectangle
    pygame.draw.rect(
        screen,
        GREEN,
        (400, 80, 180, 100)
    )

    # 4. Draw a yellow ellipse
    pygame.draw.ellipse(
        screen,
        YELLOW,
        (400, 220, 180, 100)
    )

    # 5. Draw a purple pentagon
    pentagon_points = [
        (250, 400),
        (200, 350),
        (220, 290),
        (280, 290),
        (300, 350)
    ]

    pygame.draw.polygon(
        screen,
        PURPLE,
        pentagon_points
    )

    # 6. Draw a yellow triangle
    triangle_points = [
        (550, 300),
        (480, 450),
        (620, 450)
    ]

    pygame.draw.polygon(
        screen,
        YELLOW,
        triangle_points
    )

    # Check for window close event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
sys.exit()