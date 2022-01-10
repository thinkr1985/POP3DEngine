from OpenGL.GL import *
from shaders import ConstantShader
from logger import get_logger

LOGGER = get_logger(__file__)


class Grid:
    def __init__(self, scene, grid_length: int = 25, **kwargs):
        self._scene = scene
        self._grid_length = grid_length
        self._divider_value = grid_length // 2
        self._shader = ConstantShader()
        self._VBO = glGenBuffers(1)
        self._EBO = glGenBuffers(1)
        self._init_grid()

    def _init_grid(self):
        LOGGER.info(f'Setting up {self._grid_length} unit grid')
        # create grid here.
        self.vertices_list = list()
        self.indices_list = [x for x in range(self._grid_length * 4)]

        # drawing left lines
        for val in range(self._divider_value):
            line = [-val, 0, self._divider_value, -val, 0, -self._divider_value]
            self.vertices_list.extend(line)

        # drawing right lines
        for val in range(self._divider_value):
            line = [val, 0, self._divider_value, val, 0, -self._divider_value]
            self.vertices_list.extend(line)

        # drawing top lines
        for val in range(self._divider_value):
            line = [self._divider_value, 0, val, -self._divider_value, 0, val]
            self.vertices_list.extend(line)

        # drawing bottom lines
        for val in range(self._divider_value):
            line = [self._divider_value, 0, -val, -self._divider_value, 0, -val]
            self.vertices_list.extend(line)

        self._scene.renderer.add_lines_buffer(
            entity=self,
            indices_list=self.indices_list,
            vertices_list=self.vertices_list,
            vbo=self._VBO,
            ebo=self._EBO)

    @property
    def scene(self):
        return self._scene

    @property
    def shader(self):
        return self._shader
