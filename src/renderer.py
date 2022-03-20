from OpenGL.GL import *

from logger import get_logger

LOGGER = get_logger(__file__)


class Renderer:
    def __init__(self, scene, **kwargs):
        self._scene = scene

    def __str__(self):
        return 'Renderer at {}'.format(hex(id(self)))

    def __repr__(self):
        return 'Renderer at {}'.format(hex(id(self)))

    @property
    def scene(self):
        return self._scene

    def _draw_entities(self):
        for entity in self.scene.entities.values():
            entity.draw()

    def render(self):
        self.scene.active_camera.use()
        self._draw_entities()
        self.scene.ambient_light.draw()

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_TEXTURE_BUFFER, 0)
        glDeleteProgram(0)
