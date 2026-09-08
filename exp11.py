import pygame
import sys

pygame.init()

WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raster and Vector Graphics")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 180, 0)

screen.fill(WHITE)

# ---------------- RASTER GRAPHICS ----------------
# Draw individual pixels to represent a raster image

pixel_size = 10
start_x = 80
start_y = 180

raster_pixels = [
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 2, 2, 1, 1, 0],
    [1, 1, 2, 2, 2, 2, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [0, 1, 2, 2, 2, 2, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0]
]

colors = {
    0: WHITE,
    1: BLUE,
    2: RED
}

for row in range(len(raster_pixels)):
    for col in range(len(raster_pixels[row])):
        color = colors[raster_pixels[row][col]]

        pygame.draw.rect(
            screen,
            color,
            (
                start_x + col * pixel_size,
                start_y + row * pixel_size,
                pixel_size,
                pixel_size
            )
        )

# ---------------- VECTOR GRAPHICS ----------------
# Draw objects using mathematical shapes

pygame.draw.circle(screen, GREEN, (600, 220), 70)

pygame.draw.rect(
    screen,
    BLUE,
    (520, 330, 160, 100),
    4
)

pygame.draw.line(
    screen,
    RED,
    (480, 480),
    (720, 480),
    5
)

pygame.draw.polygon(
    screen,
    GREEN,
    [(600, 120), (540, 180), (660, 180)]
)

# Text labels
font = pygame.font.Font(None, 36)

raster_text = font.render("Raster Graphics", True, BLACK)
vector_text = font.render("Vector Graphics", True, BLACK)

screen.blit(raster_text, (70, 100))
screen.blit(vector_text, (500, 100))

pygame.display.flip()

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()