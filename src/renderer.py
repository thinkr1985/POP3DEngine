import numpy as np
import re
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *

from logger import get_logger
from exceptions import OpenGLVersionCompatibilityError

LOGGER = get_logger(__file__)


class GLSettings:
    def __init__(self, gl_widget: QOpenGLWidget, **kwargs):
        self.gl_widget = gl_widget
        self.major_gl_version = 4
        self.minor_gl_version = 0

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

        glutInit()
        glutInitDisplayMode(GLUT_RGBA |
                            GLUT_DOUBLE |
                            GLUT_MULTISAMPLE |
                            GLUT_ALPHA |
                            GLUT_DEPTH |
                            GLUT_CORE_PROFILE,
                            )
        glutInitContextProfile(GLUT_CORE_PROFILE)

        self._gl_extensions = list()

    @property
    def gl_extensions(self):
        return self._gl_extensions

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
        LOGGER.info(f'Setting GL property {property_name} to {value}')
        self._properties[property_name] = value
        self.set_glrendersettings()

    @property
    def properties_dict(self) -> dict:
        return self._properties

    def set_properties_dict(self, property_dict: dict):
        for key, value in property_dict.items():
            LOGGER.info(f'Setting GL property {key} to {value}')
            self.set_property(key, value)

    def set_glrendersettings(self):
        LOGGER.info('Configuring OpenGL Settings')
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_DEBUG_OUTPUT)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        if self.smooth_lines:
            glEnable(GL_LINE_SMOOTH)
        else:
            glDisable(GL_LINE_SMOOTH)

        if self.point_mode:
            # glEnable(GL_POINT_SMOOTH)
            glPointSize(self.point_size)
            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)

        else:
            # glDisable(GL_POINT_SMOOTH)
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

        # if self.flat_shading:
        #     glShadeModel(GL_FLAT)
        # else:
        #     glShadeModel(GL_SMOOTH)

        if self.cull_faces:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        else:
            glDisable(GL_CULL_FACE)

        if self.multi_sample:
            glEnable(GL_MULTISAMPLE)
        else:
            glDisable(GL_MULTISAMPLE)

        # glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        # glColorMaterial(GL_FRONT, GL_SPECULAR)
        # glShadeModel(GL_SMOOTH)

        for ext_num in range(glGetIntegerv(GL_NUM_EXTENSIONS)):
            self._gl_extensions.append(
                glGetStringi(GL_EXTENSIONS, ext_num).decode('utf-8').lower())

        self.validate_gl_version()
        self.print_gl_info()

    def print_gl_info(self):
        LOGGER.info(
            f'Using OpenGL'
            f' {self.gl_widget.format.OpenGLContextProfile.CoreProfile.name}')
        LOGGER.info(
            f"OpenGL version is to {glGetString(GL_VERSION).decode('utf-8')}")
        LOGGER.info(
            f"OpenGL Vendor is {glGetString(GL_VENDOR).decode('utf-8')}")
        LOGGER.info(
            f"OpenGL Renderer is {glGetString(GL_RENDERER).decode('utf-8')}")
        LOGGER.info(
            f"GL shading language version is "
            f"{glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8')}")

    def validate_gl_version(self):
        gl_version = glGetString(GL_VERSION).decode('utf-8')
        LOGGER.info(f'OpenGL version supported on this machine is {gl_version}')
        gl_match = '^(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<revision>\d+))?.*'
        match = re.match(gl_match, gl_version)
        if match:
            major_version = int(match.groupdict().get('major'))
            minor_version = int(match.groupdict().get('minor'))

            if not major_version:
                LOGGER.error(
                    'Failed to determine OpenGL major and minor versions!'
                    'setting minimum GL version strings')
                self.gl_widget.format.setVersion(
                    self.major_gl_version, self.minor_gl_version)
                return

            if major_version < 4:
                raise OpenGLVersionCompatibilityError(
                    f'OpenGL version supported om this machine is '
                    f'{major_version}.{minor_version} which is not compatible'
                    f' with this application. \n Please try updating your'
                    f' graphics card drivers!')

            self.major_gl_version = major_version or 4
            self.major_gl_version = minor_version or 0

            LOGGER.info(
                f'Setting OpenGL major.minor version of QOpenGLWidget to '
                f'{major_version}.{minor_version}')
            self.gl_widget.format.setVersion(major_version, minor_version)
        else:
            LOGGER.error(
                'Failed to query OpenGL version,'
                ' setting minimum GL version strings')
            self.gl_widget.format.setVersion(
                self.major_gl_version, self.minor_gl_version)


class Renderer:
    def __init__(self, scene, **kwargs):
        self.scene = scene

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

        # self.__init__renderer()

    def __str__(self):
        return 'Renderer at {}'.format(hex(id(self)))

    def __repr__(self):
        return 'Renderer at {}'.format(hex(id(self)))

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
            self.scene.default_shader.destroy()
            self.scene.grid.shader.use()
            glBindVertexArray(self.lines_VAO)
            glDrawElements(
                GL_LINES, len(self.lines_indices), GL_UNSIGNED_INT, None
            )
            glBindVertexArray(0)
            self.scene.grid.shader.destroy()

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
        self.scene.default_shader.destroy()

        self.scene.active_camera.use()
        self.scene.default_shader.destroy()

        # drawing lines
        # self._draw_lines()

        self.scene.default_shader.use()

        # drawing triangles
        self._draw_triangles()

        # drawing quads
        self._draw_quads()

        # drawing ngons
        self._draw_ngons()

        glBindBuffer(GL_ARRAY_BUFFER, 0)
