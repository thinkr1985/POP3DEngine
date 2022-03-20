import numpy as np
import uuid
from OpenGL.GL import *

from constants import STRIDE
from logger import get_logger
from transformation import Transformations

LOGGER = get_logger(__file__)


class Entity:
    def __init__(self, entity_name: str, buffers: dict, scene,
                 transformations: list = None, user_attributes: dict = None,
                 shader=None, draw_method=GL_TRIANGLES, **kwargs):
        self._name = entity_name
        self._vertex_buffer_list = buffers.get('vertex_buffer')
        self._index_buffer_list = buffers.get('index_buffer')

        self._indices = np.array(self.index_buffer_list, dtype=np.uint32)
        self._vertices = np.array(self.vertex_buffer_list, dtype=np.float32)
        self._vertex_array_buffer = glGenVertexArrays(1)
        self._vertex_buffer = glGenBuffers(1)
        self._index_buffer = glGenBuffers(1)

        self._user_attributes = user_attributes or dict()
        self._scene = scene
        self._draw_method = draw_method
        self._uid = uuid.uuid1()
        self._shader = shader or self.scene.default_shader
        self._transformations = Transformations(
            entity=self, transformations=transformations)

        self.triangles_indices = list()
        self.triangles_vertices = list()

        self._init_entity()

    def __str__(self):
        return f'Entity({self._name}) at {hex(id(self))}'

    def __repr__(self):
        return f'Entity({self._name}) at {hex(id(self))}'

    def _init_entity(self):
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

    def regenerate_uid(self):
        self._uid = uuid.uuid1()

    @property
    def vertex_buffer_list(self) -> list:
        return self._vertex_buffer_list

    @property
    def index_buffer_list(self) -> list:
        return self._index_buffer_list

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
        return self._vertices

    @property
    def indices(self) -> np.array:
        return self._indices

    @property
    def transformations(self) -> Transformations:
        return self._transformations

    @property
    def scene(self):
        return self._scene

    @property
    def name(self):
        return self._name

    @property
    def user_attributes(self):
        return self._user_attributes

    @property
    def uid(self):
        return self._uid

    @property
    def shader(self):
        return self._shader

    @property
    def draw_method(self):
        return self._draw_method

    def draw(self):
        self.shader.use()
        glBindVertexArray(self.vertex_array_buffer)
        glDrawElements(
            self.draw_method,
            len(self.index_buffer_list),
            GL_UNSIGNED_INT,
            None
        )
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_TEXTURE_BUFFER, 0)
        # glDeleteProgram(0)

    def destroy(self):
        glDeleteBuffers(1, (self.vertex_buffer,))
        glDeleteBuffers(1, (self.index_buffer,))
