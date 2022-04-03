import re
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *

from exceptions import OpenGLVersionCompatibilityError
from logger import get_logger

LOGGER = get_logger(__file__)


class GLSettings:
    def __init__(self, gl_widget: QOpenGLWidget, **kwargs):
        self.gl_widget = gl_widget
        self.major_gl_version = 4
        self.minor_gl_version = 0

        self._properties = {
            'smooth_lines': True,
            'line_width': 1,
            'smooth_polygons': False,
            'wireframe_mode': False,
            'point_mode': False,
            'point_size': 3,
            'flat_shading': True,
            'cull_faces': False,
            'multi_sample': True
        }

        glutInit()
        glutInitDisplayMode(GLUT_RGBA |
                            GLUT_DOUBLE |
                            GLUT_MULTISAMPLE |
                            GLUT_ALPHA |
                            GLUT_DEPTH |
                            GLUT_CORE_PROFILE |
                            GL_CONTEXT_PROFILE_MASK
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

