from OpenGL.GL import *
from OpenGL.GLUT import *

from logger import get_logger

LOGGER = get_logger(__file__)


class HeadsUpDisplay:
    def __init__(self, gl_widget, **kwargs):
        self._gl_widget = gl_widget
        self._font = GLUT_BITMAP_9_BY_15
        self._attribute_color = (1.0, 0.0, 0.0)
        self._display_attributes = dict()

        self._opengl_version = None
        self._fps = 0
        self._swap_buffer = self._gl_widget.format.swapBehavior().name

    @property
    def opengl_version(self):
        return self._opengl_version

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, val):
        self._fps = val

    @property
    def swap_buffer(self):
        return self._swap_buffer

    def glut_print(self, pos_x: float, pos_y: float, text: str) -> None:
        glColor3f(self._attribute_color[0], self._attribute_color[1], self._attribute_color[2])
        glRasterPos2f(pos_x, pos_y)
        for character in text:
            glutBitmapCharacter(self._font, ord(character))

    def _init_headsup_display(self):
        self._opengl_version = glGetString(GL_VERSION).decode('utf-8')
        self._fps = 0

    def show_default_elements(self):
        current_y_pos = self._gl_widget.height() - 20

        self.glut_print(0, current_y_pos,
                        f'OpenGL Version : {self.opengl_version}')
        self.glut_print(0, current_y_pos - 20,
                        f'FPS : {self.fps}')

        self.glut_print(0, current_y_pos - 40,
                        f'Swap Buffer : {self.swap_buffer}')

    def draw(self):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION) # switch to 2D projection
        glPushMatrix()  # save matrix state
        glLoadIdentity()    # reset

        # set 2D projection matrix
        glOrtho(0, self._gl_widget.width(), 0, self._gl_widget.height(), -1, 1)

        glMatrixMode(GL_MODELVIEW)  # switch to model view matrix
        glPushMatrix()  # save state
        glLoadIdentity()    # reset

        blending = False
        if glIsEnabled(GL_BLEND):
            blending = True

        self.show_default_elements()

        if not blending:
            glDisable(GL_BLEND)

        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION) # switch back to 3D projection
        glPopMatrix()   # retrieve matrix state
        glMatrixMode(GL_MODELVIEW)  # switch to model matrix view
        glPopMatrix()   # retrieve matrix
