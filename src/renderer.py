import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

from logger import get_logger

LOGGER = get_logger(__file__)


class Renderer:
    def __init__(self, scene, **kwargs):
        self.scene = scene
        self._properties = {
            'smooth_lines': False,
            'line_width': 1,
            'smooth_polygons': False,
            'wireframe_mode': False,
            'point_mode': False,
            'point_size': 3,
            'flat_shading': False,
            'cull_faces': False,
            'multi_sample': False
        }

        self.lines_VAO = glGenVertexArrays(1)
        self.lines_indices = list()
        self.lines_vertices = list()

        self.triangles_VAO = glGenVertexArrays(1)
        self.triangles_indices = list()
        self.triangles_vertices = list()

        self.quads_VAO = glGenVertexArrays(1)
        self.quads_indices = list()
        self.quads_vertices = list()

        self.ngons_VAO = glGenVertexArrays(1)
        self.ngons_indices = list()
        self.ngons_vertices = list()

        self.__init__renderer()

    def __str__(self):
        return 'Renderer at {}'.format(hex(id(self)))

    def __repr__(self):
        return 'Renderer at {}'.format(hex(id(self)))

    def __getattr__(self, property_name: str):
        if property_name in self._properties:
            return self._properties[property_name]
        else:
            LOGGER.error(
                f'Failed to get Property!, {property_name} does not exists'
                f' in Renderer!')

    def set_property(self, property_name: str, value) -> None:
        if property_name not in self._properties:
            LOGGER.error(
                f'Failed to set Render property!,'
                f' {property_name} is not a Renderer property_name')
            return
        self._properties[property_name] = value
        self.__init__renderer()

    @property
    def properties_dict(self) -> dict:
        return self._properties

    def set_properties_dict(self, property_dict: dict):
        for key, value in property_dict.items():
            self.set_property(key, value)

    def __init__renderer(self):
        LOGGER.info('Configuring Renderer')
        if self.smooth_lines:
            glEnable(GL_LINE_SMOOTH)
        else:
            glDisable(GL_LINE_SMOOTH)

        if self.point_mode:
            glEnable(GL_POINT_SMOOTH)
            glPointSize(self.point_size)
            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)

        else:
            glDisable(GL_POINT_SMOOTH)
            glPointSize(1)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        if self.smooth_polygons:
            glEnable(GL_POLYGON_SMOOTH)
        else:
            glDisable(GL_POLYGON_SMOOTH)

        if self.wireframe_mode:
            glLineWidth(self.line_width)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glLineWidth(1)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        if self.flat_shading:
            glShadeModel(GL_FLAT)
        else:
            glShadeModel(GL_SMOOTH)

        if self.cull_faces:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        else:
            glDisable(GL_CULL_FACE)

        if self.multi_sample:
            glEnable(GL_MULTISAMPLE)
        else:
            glDisable(GL_MULTISAMPLE)

        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(5)

        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glColorMaterial(GL_FRONT, GL_SPECULAR)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_DEBUG_OUTPUT)
        glEnable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

    @staticmethod
    def bind_buffer(vao, vbo, ebo, indices, vertices, entity, stride):
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices,
                     GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices,
                     GL_STATIC_DRAW)

        entity.shader.setup_attribute_pointers(stride)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def add_lines_buffer(self, entity, indices_list: list, vertices_list: list, vbo, ebo):
        element_index = len(set(self.lines_vertices))
        new_index_buffer = [x + element_index for x in indices_list]

        self.lines_indices.extend(new_index_buffer)
        self.lines_vertices.extend(vertices_list)

        indices = np.array(self.lines_indices, dtype=np.uint32)
        vertices = np.array(self.lines_vertices, dtype=np.float32)

        self.bind_buffer(self.lines_VAO,
                         vbo,
                         ebo,
                         indices,
                         vertices,
                         entity,
                         12)

    def add_triangle_buffer(self, entity, indices_list: list, vertices_list: list):
        element_index = len(set(self.triangles_indices))
        new_index_buffer = [x + element_index for x in indices_list]

        self.triangles_indices.extend(new_index_buffer)
        self.triangles_vertices.extend(vertices_list)

        indices = np.array(self.triangles_indices, dtype=np.uint32)
        vertices = np.array(self.triangles_vertices, dtype=np.float32)

        self.bind_buffer(self.triangles_VAO,
                         entity.triangles_VBO,
                         entity.triangles_EBO,
                         indices,
                         vertices,
                         entity,
                         48)

    def add_quad_buffer(self, entity, indices_list: list, vertices_list: list):
        element_index = len(set(self.quads_indices))
        new_index_buffer = [x + element_index for x in indices_list]

        self.quads_indices.extend(new_index_buffer)
        self.quads_vertices.extend(vertices_list)

        indices = np.array(self.quads_indices, dtype=np.uint32)
        vertices = np.array(self.quads_vertices, dtype=np.float32)

        self.bind_buffer(self.quads_VAO,
                         entity.quads_VBO,
                         entity.quads_EBO,
                         indices,
                         vertices,
                         entity,
                         48)

    def add_ngon_buffer(self, entity, indices_list: list, vertices_list: list):
        element_index = len(set(self.ngons_indices))
        new_index_buffer = [x + element_index for x in indices_list]

        self.ngons_indices.extend(new_index_buffer)
        self.ngons_vertices.extend(vertices_list)

        indices = np.array(self.ngons_indices, dtype=np.uint32)
        vertices = np.array(self.ngons_vertices, dtype=np.float32)

        self.bind_buffer(self.ngons_VAO,
                         entity.ngons_VBO,
                         entity.ngons_EBO,
                         indices,
                         vertices,
                         entity,
                         48)

    def _draw_lines(self):
        if self.lines_indices:
            # self.scene.default_shader.destroy()
            # self.scene.grid.shader.use()
            glBindVertexArray(self.lines_VAO)
            glDrawElements(
                GL_LINES, len(self.lines_indices), GL_UNSIGNED_INT, None
            )
            glBindVertexArray(0)
            # self.scene.grid.shader.destroy()

    def _draw_triangles(self):
        if self.triangles_indices:
            glBindVertexArray(self.triangles_VAO)
            glDrawElements(
                GL_TRIANGLES, len(self.triangles_indices), GL_UNSIGNED_INT, None
            )
            glBindVertexArray(0)

    def _draw_quads(self):
        if self.quads_indices:
            glBindVertexArray(self.quads_VAO)
            glDrawElements(
                GL_QUADS, len(self.quads_indices), GL_UNSIGNED_INT, None
            )
            glBindVertexArray(0)

    def _draw_ngons(self):
        if self.ngons_indices:
            glBindVertexArray(self.ngons_VAO)
            glDrawElements(
                GL_POLYGON, len(self.ngons_indices), GL_UNSIGNED_INT, None
            )
            glBindVertexArray(0)

    def render(self):
        self.scene.active_camera.use()

        # drawing lines
        self._draw_lines()

        self.scene.default_shader.use()

        # drawing triangles
        self._draw_triangles()

        # drawing quads
        self._draw_quads()

        # drawing ngons
        self._draw_ngons()

        self.scene.default_shader.destroy()
        glBindBuffer(GL_ARRAY_BUFFER, 0)
