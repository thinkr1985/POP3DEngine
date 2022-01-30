import numpy as np
import uuid
from OpenGL.GL import *

from logger import get_logger
from vertex import VertexSet
from transformation import Transformations

LOGGER = get_logger(__file__)


class Entity:
    def __init__(self, entity_name: str, face_sets: list, scene,
                 transformations: list = None, user_attributes: dict = None,
                 shader=None, **kwargs):
        self._name = entity_name
        self._face_sets = face_sets
        self._user_attributes = user_attributes or dict()
        self._scene = scene
        self._uid = uuid.uuid1()
        self._shader = shader or self._scene.default_shader
        self._vertex_sets = list()
        self._transformations = Transformations(
            entity=self, transformations=transformations)

        self.triangles_VBO = glGenBuffers(1)
        self.triangles_EBO = glGenBuffers(1)
        self.triangles_indices = list()
        self.triangles_vertices = list()

        self.quads_VBO = glGenBuffers(1)
        self.quads_EBO = glGenBuffers(1)
        self.quads_indices = list()
        self.quads_vertices = list()

        self.ngons_VBO = glGenBuffers(1)
        self.ngons_EBO = glGenBuffers(1)
        self.ngons_indices = list()
        self.ngons_vertices = list()

        self._init_entity()

    def __str__(self):
        return f'Entity({self._name}) at {hex(id(self))}'

    def __repr__(self):
        return f'Entity({self._name}) at {hex(id(self))}'

    def _init_entity(self):
        for set_ in self._face_sets:
            for vertices_per_face, buffers in set_.items():
                self.create_vertex_set(
                    vertices_per_face=int(vertices_per_face),
                    buffers=buffers)

    def create_vertex_set(self, vertices_per_face: int, buffers: dict):
        vertex_set = VertexSet(
            vertices_per_face=vertices_per_face, buffers=buffers, entity=self)
        self._vertex_sets.append(vertex_set)

    def regenerate_uid(self):
        self._uid = uuid.uuid1()

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
    def vertex_sets(self):
        return self._vertex_sets

    @property
    def shader(self):
        return self._shader

    def destroy(self):
        glDeleteBuffers(1, (self.triangles_VBO,))
        glDeleteBuffers(1, (self.quads_VBO,))
        glDeleteBuffers(1, (self.ngons_VBO,))

        glDeleteBuffers(1, (self.triangles_EBO,))
        glDeleteBuffers(1, (self.quads_EBO,))
        glDeleteBuffers(1, (self.ngons_EBO,))
