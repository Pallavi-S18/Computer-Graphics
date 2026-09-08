import pygame
import math

pygame.init()

# Window
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Line Transformation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 180, 0)

# Original line coordinates
x1, y1 = 200, 300
x2, y2 = 400, 300

# Transformation values
tx = 100
ty = -50
scale = 1.5
angle = 45


# Translation
def translate(x, y, tx, ty):
    return x + tx, y + ty


# Scaling
def scale_point(x, y, sx, sy, cx, cy):
    x_new = cx + (x - cx) * sx
    y_new = cy + (y - cy) * sy
    return x_new, y_new


# Rotation
def rotate_point(x, y, angle, cx, cy):
    radians = math.radians(angle)

    x_new = cx + (x - cx) * math.cos(radians) - (y - cy) * math.sin(radians)
    y_new = cy + (x - cx) * math.sin(radians) + (y - cy) * math.cos(radians)

    return x_new, y_new


running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Clear screen
    screen.fill(WHITE)

    # Draw coordinate axes
    pygame.draw.line(screen, BLACK, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 1)
    pygame.draw.line(screen, BLACK, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 1)

    # Original line
    pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 4)

    # Translation
    if keys[pygame.K_t]:
        p1 = translate(x1, y1, tx, ty)
        p2 = translate(x2, y2, tx, ty)

        pygame.draw.line(screen, BLUE, p1, p2, 4)

    # Scaling
    elif keys[pygame.K_s]:
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        p1 = scale_point(x1, y1, scale, scale, cx, cy)
        p2 = scale_point(x2, y2, scale, scale, cx, cy)

        pygame.draw.line(screen, GREEN, p1, p2, 4)

    # Rotation
    elif keys[pygame.K_r]:
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        p1 = rotate_point(x1, y1, angle, cx, cy)
        p2 = rotate_point(x2, y2, angle, cx, cy)

        pygame.draw.line(screen, BLUE, p1, p2, 4)

    # Text
    font = pygame.font.Font(None, 30)

    title = font.render("LINE TRANSFORMATION", True, BLACK)
    instructions = font.render(
        "Press T = Translation   S = Scaling   R = Rotation",
        True,
        BLACK
    )

    screen.blit(title, (280, 30))
    screen.blit(instructions, (180, 550))

    pygame.display.update()

pygame.quit()