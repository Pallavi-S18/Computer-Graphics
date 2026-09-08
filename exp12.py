import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

# Initialize Pygame
pygame.init()

# Window size
WIDTH = 800
HEIGHT = 600

# Create OpenGL window
pygame.display.set_mode(
    (WIDTH, HEIGHT),
    DOUBLEBUF | OPENGL
)

pygame.display.set_caption("GPU Based Rendering using OpenGL")

# Set background color
glClearColor(0.1, 0.1, 0.1, 1.0)

# Set projection
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, WIDTH, 0, HEIGHT)

# Set model view
glMatrixMode(GL_MODELVIEW)

running = True

while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw triangle
    glBegin(GL_TRIANGLES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex2f(400, 500)

    glColor3f(0.0, 1.0, 0.0)
    glVertex2f(250, 200)

    glColor3f(0.0, 0.0, 1.0)
    glVertex2f(550, 200)

    glEnd()

    # Display rendered frame
    pygame.display.flip()

    # Control frame rate
    pygame.time.wait(10)

# Quit
pygame.quit()
sys.exit()