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
        self._msp = 0
        self._swap_buffer = self._gl_widget.format.swapBehavior().name
        self._glsl_version = None
        self._vsync = self._gl_widget.format.swapInterval()

    @property
    def opengl_version(self):
        return self._opengl_version

    @property
    def glsl_version(self):
        return self._glsl_version

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, val):
        self._fps = val

    @property
    def millisecond_per_frame(self):
        return self._msp

    @millisecond_per_frame.setter
    def millisecond_per_frame(self, val):
        self._msp = val

    @property
    def swap_buffer(self):
        return self._swap_buffer

    @property
    def vsync(self):
        if not self._vsync:
            return "Off"
        else:
            return "On"

    def glut_print(self, text) -> None:
        # TODO this needs to change to something else.

        # glutBitmapString(self._font, text.encode())
        pass

    def _init_headsup_display(self):
        self._opengl_version = glGetString(GL_VERSION).decode('utf-8')
        self._glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')
        self._fps = 0

    def show_default_elements(self):
        display_string = f'OpenGL Version : {self.opengl_version}\n'
        display_string += f'GLSL Version : {self.glsl_version}\n'
        display_string += f'FPS : {self.fps} / {self.millisecond_per_frame} milliseconds per frame\n'
        display_string += f'Swap Buffer : {self.swap_buffer}\n'
        display_string += f'VSync : {self.vsync}\n'
        self.glut_print(display_string)

    def draw(self):
        glDisable(GL_DEPTH_TEST)
        blending = False
        if glIsEnabled(GL_BLEND):
            blending = True

        self.show_default_elements()

        if not blending:
            glDisable(GL_BLEND)

        glEnable(GL_DEPTH_TEST)
