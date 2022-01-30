import uuid
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from logger import get_logger

LOGGER = get_logger(__file__)


class Light:
    def __init__(self, color: list, scene, shape_buffers: dict, **kwargs):
        self._color = color or [1.0, 1.0, 1.0]
        self._scene = scene
        self._VAO = scene.renderer.lines_VAO
        self._VBO = glGenBuffers(1)
        self._EBO = glGenBuffers(1)
        self._vertices_list = shape_buffers.get('vertices_list')
        self._indices_list = shape_buffers.get('indices_list')
        self._uid = uuid.uuid1()

        self._init_light()

    def __str__(self):
        return f'Light at {hex(id(self))}'

    def __repr__(self):
        return f'Light at {hex(id(self))}'

    def _init_light(self):
        self._scene.renderer.add_lines_buffer(
            entity=self,
            indices_list=self._indices_list,
            vertices_list=self._vertices_list,
            vbo=self._VBO,
            ebo=self._EBO)

    @property
    def uid(self):
        return self._uid

    @property
    def color(self) -> list:
        return self._color

    @color.setter
    def color(self, val: list):
        self._color = val

    @property
    def scene(self):
        return self._scene

    @property
    def renderer(self):
        return self._scene.renderer

    @property
    def shader(self):
        return self._scene.default_shader

    def use(self):
        pass

    def destroy(self):
        pass


class AmbientLight(Light):
    def __init__(self, color: list, scene, **kwargs):
        # self._color = color
        # self._scene = scene
        self._vertices_list = [-0.5, 0.0, 0.0,
                               -0.5, 1.0, 0.0,
                               -1.0, 2.0, 0.0,
                               -1.0, 4.0, 0.0,
                               0.0, 5.0, 0.0,
                               1.0, 4.0, 0.0,
                               1.0, 2.0, 0.0,
                               0.5, 1.0, 0.0,
                               0.5, 0.0, 0.0,
                               ]

        self._indices_list = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 0]
        #
        super().__init__(color=color,
                         scene=scene,
                         shape_buffers={
                             'vertices_list': self._vertices_list,
                             'indices_list': self._indices_list},
                         kwargs=kwargs)

    def __str__(self):
        return f'AmbientLight at {hex(id(self))}'

    def __repr__(self):
        return f'AmbientLight at {hex(id(self))}'
