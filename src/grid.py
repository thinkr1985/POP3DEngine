import numpy as np
from OpenGL.GL import *

from entity import Entity
from shaders import ConstantShader
from logger import get_logger

LOGGER = get_logger(__file__)


class Grid(Entity):
    def __init__(self, scene=None, grid_length: int = 25, **kwargs):
        self._buffers = {'vertex_buffer': list(), 'index_buffer': list()}
        self._shader = ConstantShader(
            shader_name='GridShader', scene=scene, color=[0.5, 0.5, 0.5, 1.0]
        )
        self._shader.stride = 12
        self._grid_length = grid_length
        self._divider_value = grid_length // 2

        self._build_buffers()

        super().__init__(entity_name='DefaultGrid',
                         buffers=self._buffers,
                         shader=self._shader,
                         scene=scene,
                         draw_method=GL_LINES,
                         kwargs=kwargs)
        self._scene.add_entity(entity=self)
        self._type = 'gridEntity'

    def _build_buffers(self):
        LOGGER.info(f'Setting up {self._grid_length} unit grid')
        # create grid here.
        vertices_list = list()
        self._buffers.update({'index_buffer': [x for x in range(self._grid_length * 4)]})

        # drawing left lines
        for val in range(self._divider_value):
            line = [-val, 0, self._divider_value, -val, 0, -self._divider_value]
            vertices_list.extend(line)

        # drawing right lines
        for val in range(self._divider_value):
            line = [val, 0, self._divider_value, val, 0, -self._divider_value]
            vertices_list.extend(line)

        # drawing top lines
        for val in range(self._divider_value):
            line = [self._divider_value, 0, val, -self._divider_value, 0, val]
            vertices_list.extend(line)

        # drawing bottom lines
        for val in range(self._divider_value):
            line = [self._divider_value, 0, -val, -self._divider_value, 0, -val]
            vertices_list.extend(line)
        self._buffers.update({'vertex_buffer': vertices_list})
