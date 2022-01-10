from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GLUT as glut
import ctypes


def box():
    glBegin(GL_QUADS)

    glColor3f(1.0, 0.0, 0.0)

    glVertex3f(-0.5, -0.5, 0.5)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-0.5, 0.5, 0.5)

    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glColor3f(0.0, 1.0, 0.0)

    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-0.5, 0.5, -0.5)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)

    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.5, 0.5, 0.5)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.5, -0.5, 0.5)

    glColor3f(0.0, 0.0, 1.0)

    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glColor3f(1.0, 0.0, 0.0)

    glVertex3f(-0.5, -0.5, 0.5)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glEnd()


def torus():
    pass


def grid(grid_number=10):
    glBegin(GL_LINES)

    for x in range(1, grid_number):
        glColor3f(0.4, 0.4, 0.4)

        glVertex3f(float(grid_number) - x, 0.0, float(grid_number))
        glVertex3f(float(grid_number) - x, 0.0, - float(grid_number))

        glVertex3f(0.0 - x, 0.0, - float(grid_number))
        glVertex3f(0.0 - x, 0.0, float(grid_number))

        glVertex3f(float(grid_number), 0.0, float(grid_number) - x)
        glVertex3f(- float(grid_number), 0.0, float(grid_number) - x)

        glVertex3f(float(grid_number), 0.0, 0.0 - x)
        glVertex3f(- float(grid_number), 0.0, 0.0 - x)

    glVertex3f(0.0 - float(grid_number), 0.0, - float(grid_number))
    glVertex3f(0.0 - float(grid_number), 0.0, float(grid_number))

    glVertex3f(float(grid_number), 0.0, 0.0 - float(grid_number))
    glVertex3f(- float(grid_number), 0.0, 0.0 - float(grid_number))

    glVertex3f(0.0 - float(grid_number), 0.0, float(grid_number))
    glVertex3f(0.0 + float(grid_number), 0.0, float(grid_number))

    glVertex3f(0.0 + float(grid_number), 0.0, float(grid_number))
    glVertex3f(0.0 + float(grid_number), 0.0, -float(grid_number))

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, float(grid_number))
    glVertex3f(0.0, 0.0, - float(grid_number))

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(float(grid_number), 0.0, 0.0)
    glVertex3f(- float(grid_number), 0.0, 0.0)

    glEnd()


def glut_print(posX: float,  posY: float,  font: str,  text: str, color: list) -> None:
    # glut.glutInit()
    blending = False
    if glIsEnabled(GL_BLEND):
        blending = True

    glColor3f(color[0], color[1], color[2])
    glRasterPos2f(posX, posY)
    for character in text:
        glut.glutBitmapCharacter(font, ord(character))

    if not blending:
        glDisable(GL_BLEND)


def origin_axis():
    glBegin(GL_LINES)

    # drawing Y axis
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)

    glVertex3f(0.1, 2.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)

    glVertex3f(0.1, 2.0, 0.0)
    glVertex3f(0.0, 2.1, 0.0)

    glVertex3f(-0.1, 2.0, 0.0)
    glVertex3f(0.0, 2.1, 0.0)

    glVertex3f(-0.1, 2.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)

    glVertex3f(0.0, 2.0, 0.1)
    glVertex3f(0.0, 2.0, 0.0)

    glVertex3f(0.0, 2.0, 0.1)
    glVertex3f(0.0, 2.1, 0.0)

    glVertex3f(0.0, 2.0, -0.1)
    glVertex3f(0.0, 2.1, 0.0)

    glVertex3f(0.0, 2.0, -0.1)
    glVertex3f(0.0, 2.0, 0.0)

    # drawing X axis
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.0)

    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(2.0, 0.1, 0.0)

    glVertex3f(2.0, 0.1, 0.0)
    glVertex3f(2.1, 0.0, 0.0)

    glVertex3f(2.1, 0.0, 0.0)
    glVertex3f(2.0, -0.1, 0.0)

    glVertex3f(2.0, -0.1, 0.0)
    glVertex3f(2.0, 0.0, 0.0)

    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.1)

    glVertex3f(2.0, 0.0, 0.1)
    glVertex3f(2.1, 0.0, 0.0)

    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, -0.1)

    glVertex3f(2.0, 0.0, -0.1)
    glVertex3f(2.1, 0.0, 0.0)

    # drawing Z axis
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 2.0)

    glVertex3f(0.0, 0.0, 2.0)
    glVertex3f(0.0, 0.1, 2.0)

    glVertex3f(0.0, 0.1, 2.0)
    glVertex3f(0.0, 0.0, 2.1)

    glVertex3f(0.0, 0.0, 2.1)
    glVertex3f(0.0, -0.1, 2.0)

    glVertex3f(0.0, -0.1, 2.0)
    glVertex3f(0.0, 0.0, 2.0)

    glVertex3f(0.0, 0.0, 2.0)
    glVertex3f(0.1, 0.0, 2.0)

    glVertex3f(0.1, 0.0, 2.0)
    glVertex3f(0.0, 0.0, 2.1)

    glVertex3f(0.0, 0.0, 2.1)
    glVertex3f(-0.1, 0.0, 2.0)

    glVertex3f(-0.1, 0.0, 2.0)
    glVertex3f(0.0, 0.0, 2.0)

    glEnd()
