import uuid
from PyQt6 import QtGui, QtWidgets, QtCore, QtOpenGLWidgets
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from glfw import *
import numpy as np
from constants import DEFAULT_SHADER, DEFAULT_TEXTURES
from utilities import utils
from exceptions import (VertexShaderCompilationError,
                        FragmentShaderCompilationError, ShaderProgramLinkError)
from logger import get_logger
from cameras import PerspectiveCamera
from texture import TextureMap

LOGGER = get_logger(__file__)


class Shader:
    def __init__(self, shader_name: str, vert_src: str, frag_src: str, color_map_src: str = None,
                 normal_map_src: str = None, **kwargs):
        self.name = shader_name
        self.vert_src = vert_src
        self.frag_src = frag_src
        self.color_map_src = color_map_src
        self.normal_map_src = normal_map_src

        self.color_texture_map = None
        self.normal_texture_map = None

        self._shader_attribute_dict = {
            'position': ctypes.c_void_p(0),
            'normalTex': ctypes.c_void_p(12),
            'color': ctypes.c_void_p(24),
            'inTexCoords': ctypes.c_void_p(40),
        }

        self.shader_program = glCreateProgram()
        self._init_shader()

    def _init_shader(self):
        if not self.color_map_src:
            self.color_texture_map = TextureMap(os.path.join(
                DEFAULT_TEXTURES, 'checker_board.png'), texture_slot=0)
            self.color_texture_map.init_texture()
        if not self.normal_map_src:
            self.normal_texture_map = TextureMap(os.path.join(
                DEFAULT_TEXTURES, 'checker_board_normal.png'), texture_slot=1)
            self.normal_texture_map.init_texture()

        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

        glShaderSource(vertex_shader, self.default_vertex_shader_code())
        glShaderSource(fragment_shader, self.default_fragment_shader_code())

        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error_ = glGetShaderInfoLog(vertex_shader).decode()
            raise VertexShaderCompilationError(
                f"Vertex shader compilation error: {error_}"
            )

        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error_ = glGetShaderInfoLog(fragment_shader).decode()
            raise FragmentShaderCompilationError(
                f"Fragment shader compilation error: {error_}"
            )

        glAttachShader(self.shader_program, vertex_shader)
        glAttachShader(self.shader_program, fragment_shader)
        glLinkProgram(self.shader_program)

        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            error_ = (glGetProgramInfoLog(self.shader_program))
            raise ShaderProgramLinkError(f'Linking error : {error_}')

        glDetachShader(self.shader_program, vertex_shader)
        glDetachShader(self.shader_program, fragment_shader)

    def default_vertex_shader_code(self):
        with open(self.vert_src, 'r') as vp:
            return vp.readlines()

    def default_fragment_shader_code(self):
        with open(self.frag_src, 'r') as fp:
            return fp.readlines()

    def _setup_attribute_pointer(self, attribute_name: str, stride: int, void_pointer: ctypes.c_void_p):
        LOGGER.info(f'Setting up attribute {attribute_name} for shader {self.name} with stride {stride}')
        pos_attrib_location = glGetAttribLocation(self.shader_program,
                                                  attribute_name)
        glEnableVertexAttribArray(pos_attrib_location)
        glVertexAttribPointer(pos_attrib_location, 3, GL_FLOAT, GL_FALSE,
                              stride, void_pointer)

    def setup_attribute_pointers(self, stride):
        for attribute_name, pointer in self._shader_attribute_dict.items():
            self._setup_attribute_pointer(
                attribute_name=attribute_name,
                stride=stride,
                void_pointer=pointer)

    def use(self):
        glUseProgram(self.shader_program)
        if self.color_texture_map:
            self.color_texture_map.use()
        if self.normal_texture_map:
            self.normal_texture_map.use()

    def destroy(self):
        glDeleteProgram(self.shader_program)
        if self.color_texture_map:
            self.color_texture_map.destroy()
        if self.normal_texture_map:
            self.normal_texture_map.destroy()


class DefaultShader(Shader):
    def __init__(self,
                 shader_name: str = 'default_shader',
                 vert_src: str = os.path.join(
                     DEFAULT_SHADER, 'vertex_shader.glsl'),
                 frag_src: str = os.path.join(
                     DEFAULT_SHADER, 'geometry_shader.glsl'),
                 color_map_src: str = None,
                 normal_map_src: str = None,
                 **kwargs):

        self.name = shader_name
        self.vert_src = vert_src
        self.frag_src = frag_src
        self.color_map_src = color_map_src
        self.normal_map_src = normal_map_src

        super().__init__(shader_name=self.name,
                         vert_src=self.vert_src,
                         frag_src=self.frag_src,
                         color_map_src=self.color_map_src,
                         normal_map_src=self.normal_map_src,
                         kwargs=kwargs)


class Scene:
    def __init__(self, **kwargs):
        self._width = 512
        self._height = 512
        self._entities = dict()
        self._default_shader = DefaultShader()
        self._renderer = Renderer(self)
        self._cameras = dict()
        self._active_camera = None

        self._init_scene()

    def __str__(self):
        return f'Scene() @ {hex(id(self))}'

    def __repr__(self):
        return f'Scene() @ {hex(id(self))}'

    def _init_scene(self):
        camera = self.create_perspective_camera(width=self._width,
                                                height=self._height,
                                                far_clip=50.0,
                                                near_clip=0.1,
                                                camera_name='persp')
        self._active_camera = camera

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def entities(self):
        return self._entities

    @property
    def cameras(self):
        return self._cameras

    @property
    def active_camera(self):
        return self._active_camera

    @property
    def renderer(self):
        return self._renderer

    @property
    def default_shader(self):
        return self._default_shader

    def add_entity(self, entity: str or list, update_uid=False):
        if not isinstance(entity, list):
            entities = [entity]
        else:
            entities = entity

        for ent in entities:
            if isinstance(ent, Entity):
                if not update_uid:
                    if ent.uid in self._entities:
                        LOGGER.error(
                            f'Failed to add Entity!, entity with uid {ent.uid} '
                            f'already exists in the scene.')
                        return
                    else:
                        self._entities.update({ent.uid: ent})
                else:
                    ent.regenerate_uid()
                    self.add_entity(ent, update_uid=True)
            else:
                LOGGER.error(
                    f'Failed to add entity!, provided entity {ent} '
                    f'do not have valid type')

    def destroy_entity(self, entity):
        if entity.uid not in self._entities:
            LOGGER.info(
                f'Failed to destroy entity!, entity with uid {entity.uid}'
                f' does not exists in this scene!')
            return
        self._entities.pop(entity.uid)
        entity.destroy()

    def add_camera(self, camera_object):
        if camera_object.camera_name not in self._cameras:
            LOGGER.info(
                f'Adding camera "{camera_object.camera_name}" to the scene')
            self._cameras.update({camera_object.camera_name: camera_object})
        else:
            LOGGER.error(
                f'Failed to add camera to Scene because camera with name '
                f'{camera_object.camera_name} already exists!')

    def remove_camera(self, camera_name: str):
        if camera_name in self._cameras:
            self._cameras.pop(camera_name)
        else:
            LOGGER.error(
                f'Failed to remove camera with name {camera_name} because '
                f'No camera with this name exists in the scene.'
            )

    def create_perspective_camera(self, camera_name: str, width: int,
                                  height: int, near_clip: float = 0.1,
                                  far_clip: float = 10.0) -> PerspectiveCamera:
        camera = PerspectiveCamera(camera_name=camera_name,
                                   width=width,
                                   height=height,
                                   near_clip=near_clip,
                                   far_clip=far_clip,
                                   scene=self)
        return camera


class Renderer:
    def __init__(self, scene: Scene, **kwargs):
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
        self.setup_renderer()

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
        else:
            glDisable(GL_CULL_FACE)

        if self.multi_sample:
            glEnable(GL_MULTISAMPLE)
        else:
            glDisable(GL_MULTISAMPLE)

        glEnable(GL_DEPTH_TEST)
        # glDepthFunc(GL_ALWAYS)
        # glEnable(GL_DEBUG_OUTPUT)
        glEnable(GL_TEXTURE_2D)

    @staticmethod
    def bind_buffer(vao, vbo, ebo, indices, vertices, entity):
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices,
                     GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices,
                     GL_STATIC_DRAW)

        entity.shader.setup_attribute_pointers(12 * 4)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

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
                         entity)

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
                         entity)

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
                         entity)

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
        self.scene.default_shader.use()

        # drawing triangles
        self._draw_triangles()

        # drawing quads
        self._draw_quads()

        # drawing ngons
        self._draw_ngons()

        self.scene.default_shader.destroy()
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    
class Entity:
    def __init__(self, entity_name: str, face_sets: list, scene: Scene,
                 user_attributes: dict = None, shader=None, **kwargs):
        self._name = entity_name
        self._face_sets = face_sets
        self._user_attributes = user_attributes or dict()
        self._scene = scene
        self._uid = uuid.uuid1()
        self._shader = shader or self._scene.default_shader
        self._vertex_sets = list()

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


class VertexSet:
    def __init__(self, vertices_per_face: int, buffers: dict, entity: Entity, **kwargs):
        self.vertices_per_face = vertices_per_face
        self.vertex_buffer_list = buffers.get('vertex_buffer')
        self.index_buffer_list = buffers.get('index_buffer')
        self.entity = entity

        self.init_vertex_entity()

    def init_vertex_entity(self):
        if self.vertices_per_face == 3:
            self.entity.scene.renderer.add_triangle_buffer(
                self.entity, self.index_buffer_list, self.vertex_buffer_list)

        if self.vertices_per_face == 4:
            self.entity.scene.renderer.add_quad_buffer(
                self.entity, self.index_buffer_list, self.vertex_buffer_list)

        elif self.vertices_per_face > 4:
            self.entity.scene.renderer.add_ngon_buffer(
                self.entity, self.index_buffer_list, self.vertex_buffer_list)


class _OpenGLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # setting Format of the openGL context
        self.format = QtGui.QSurfaceFormat()
        self.setFormat(self.format)
        self.format.setVersion(3, 3)
        self.format.setSamples(4)
        self.format.setProfile(QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(QtCore.QSize(120, 120))

    def paintGL(self) -> None:
        glClearColor(0.3, 0.3, 0.3, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        self.scene.renderer.render()
        self.update()
        glFlush()

    def initializeGL(self) -> None:
        LOGGER.info('Initializing OpenGL')

        glutInit()
        glutInitDisplayMode(GLUT_RGBA |
                            GLUT_DOUBLE |
                            GLUT_MULTISAMPLE |
                            GLUT_ALPHA |
                            GLUT_DEPTH |
                            GLUT_CORE_PROFILE)
        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)

        self.scene = Scene()

        entities = utils.read_pymesh_file('E:\\projects\\3d_viewer\\src\\pymesh_examples\\arab_man.pymesh')

        for entity_data in entities:
            face_sets = entity_data.get('face_sets')
            new_entity = Entity(entity_name="test", face_sets=face_sets, scene=self.scene)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = _OpenGLWidget()
    win.show()
    app.exec()
