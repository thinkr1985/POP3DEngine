import uuid
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

from logger import get_logger

LOGGER = get_logger(__file__)


class Light:
    def __init__(self, color: list, scene, shape_buffers: dict, light_name: str, **kwargs):
        self._color = color or [1.0, 1.0, 1.0]
        self._scene = scene
        self._name = light_name
        self._vertex_array_buffer = glGenVertexArrays(1)
        self._vertex_buffer = glGenBuffers(1)
        self._index_buffer = glGenBuffers(1)
        self._vertices_list = shape_buffers.get('vertices_list')
        self._indices_list = shape_buffers.get('indices_list')
        self._uid = uuid.uuid1()

        # self.scene.add_scene_light(self)
        self._init_light()

    def __str__(self):
        return f'Light ({self._name}) at {hex(id(self))}'

    def __repr__(self):
        return f'Light ({self._name}) at {hex(id(self))}'

    def _init_light(self):
        glBindVertexArray(self.vertex_array_buffer)
        self.shader.use()

        # binding vertex data
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices.nbytes,
                     self.vertices,
                     GL_STATIC_DRAW)

        # binding index data
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     self.indices.nbytes,
                     self.indices,
                     GL_STATIC_DRAW)

        # setup shader attributes
        self.shader.setup_attribute_pointers(self, 0)

        # unbind the buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    @property
    def name(self) -> str:
        return self.name

    @property
    def vertex_array_buffer(self) -> glGenVertexArrays:
        return self._vertex_array_buffer

    @property
    def vertex_buffer(self) -> glGenBuffers:
        return self._vertex_buffer

    @property
    def index_buffer(self) -> glGenBuffers:
        return self._index_buffer

    @property
    def vertices(self) -> np.array:
        return np.array(self._vertices_list, dtype=np.uint32)

    @property
    def indices(self) -> np.array:
        return np.array(self._indices_list, dtype=np.uint32)

    @property
    def vertex_buffer_list(self) -> list:
        return self._vertices_list

    @property
    def index_buffer_list(self) -> list:
        return self._indices_list

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
        return self._scene.constant_shader

    def use(self):
        pass

    def draw(self):
        self.shader.use()
        glBindVertexArray(self.vertex_array_buffer)
        glDrawElements(
            GL_LINES,
            len(self.index_buffer_list),
            GL_UNSIGNED_INT,
            None
        )
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # glDeleteProgram(0)

    def destroy(self):
        glDeleteBuffers(1, (self.vertex_buffer,))
        glDeleteBuffers(1, (self.index_buffer,))


class AmbientLight(Light):
    def __init__(self, color: list, scene, light_name: str, **kwargs):
        self._color = color
        self._scene = scene
        self._name = light_name
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
        super().__init__(color=self._color,
                         scene=self._scene,
                         light_name=self._name,
                         shape_buffers={
                             'vertices_list': self._vertices_list,
                             'indices_list': self._indices_list},
                         kwargs=kwargs)

    def __str__(self):
        return f'AmbientLight({self._name}) at {hex(id(self))}'

    def __repr__(self):
        return f'AmbientLight({self._name}) at {hex(id(self))}'
