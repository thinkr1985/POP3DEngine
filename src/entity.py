import numpy as np
import uuid
from OpenGL.GL import *

from logger import get_logger
from exceptions import EntityCreationError
import transformation

LOGGER = get_logger(__file__)


class Entity:
    def __init__(self, entity_name: str, buffers: dict, scene,
                 transformations: list = None, user_attributes: dict = None,
                 shader=None, draw_method=GL_TRIANGLES, **kwargs):
        self._type = 'baseEntity'
        self._name = entity_name
        self._vertex_buffer_list = buffers.get('vertex_buffer')
        self._index_buffer_list = buffers.get('index_buffer')
        self._visibility = kwargs.get('visibility') or True

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
        self._transformations = transformation.Transformations(
            entity=self, transformations=transformations)
        self.triangles_indices = list()
        self.triangles_vertices = list()

        self._init_entity()

    def __new__(cls, *args, **kwargs):
        ent_name = kwargs.get('entity_name')
        # if not ent_name:
        #     raise EntityCreationError(
        #         'Failed to create entity, name not provided!')

        scene = kwargs.get('scene')
        if not scene:
            raise EntityCreationError(
                f'Failed to create entity {ent_name}, scene not provided!')

        if ent_name in [x.name for x in scene.entities.values()]:
            raise EntityCreationError(
                f'Failed to create entity, Entity with name {ent_name}'
                f' already exists!')

        # if not kwargs.get('buffers'):
        #     raise EntityCreationError(
        #         f'Failed to create entity {ent_name}, buffers not provided!')

        return super(Entity, cls).__new__(cls)

    def __str__(self):
        return f'{self._type}({self._name}) at {hex(id(self))}'

    def __repr__(self):
        return f'{self._type}({self._name}) at {hex(id(self))}'

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

    @property
    def translate(self) -> transformation.Translation:
        return self._transformations.translate

    @property
    def rotate(self) -> transformation.Rotation:
        return self._transformations.rotate

    @property
    def size(self) -> transformation.Scale:
        return self._transformations.size

    @property
    def visibility(self) -> (int, bool):
        return self._visibility

    @visibility.setter
    def visibility(self, visibility: (int, bool)):
        self._visibility = visibility

    @property
    def type(self) -> str:
        return self._type

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
    def transformations(self) -> transformation.Transformations:
        return self._transformations

    @property
    def scene(self):
        return self._scene

    @property
    def name(self) -> str:
        return self._name

    @property
    def user_attributes(self) -> (None, dict):
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

    def re_calculate_matrices(self):
        """This method needs to override in camera entity"""
        pass

    def setup_mvp_matrix(self):
        glUniformMatrix4fv(
            self.shader.active_uniforms['modelMatrix']['location'],
            1,
            GL_FALSE,
            self.transformations.model_matrix
        )

        glUniformMatrix4fv(
            self.shader.active_uniforms['viewMatrix']['location'],
            1,
            GL_FALSE,
            self.scene.active_camera.view_matrix
        )

        glUniformMatrix4fv(
            self.shader.active_uniforms['projectionMatrix']['location'],
            1,
            GL_FALSE,
            self.scene.active_camera.projection_matrix
        )

        glUniform3fv(
            self.shader.active_uniforms['cameraPosition']['location'],
            1,
            GL_FALSE,
            self.scene.active_camera.transformations.position
        )

    def draw(self):
        if not self._visibility:
            return
        if self._type != 'gridEntity' and self._type != 'cameraEntity':
            self.transformations.rotate.y = self.transformations.rotate.y + 0.5

        self.shader.use()
        self.setup_mvp_matrix()

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


class MeshEntity(Entity):
    def __init__(self, entity_name: str, buffers: dict, scene,
                 transformations: list = None, user_attributes: dict = None,
                 shader=None, draw_method=GL_TRIANGLES, **kwargs):

        super().__init__(
            entity_name=entity_name,
            buffers=buffers,
            scene=scene,
            transformations=transformations,
            user_attributes=user_attributes,
            shader=shader,
            draw_method=draw_method,
            kwargs=kwargs)

        self._type = 'meshEntity'
