from exceptions import (VertexShaderCompilationError,
                        FragmentShaderCompilationError, ShaderProgramLinkError)
from OpenGL.GL import *
from OpenGL.GLUT import *

from logger import get_logger
from constants import DEFAULT_SHADER, CONSTANT_SHADER, DEFAULT_TEXTURES
from texture import TextureMap

LOGGER = get_logger(__file__)


class Shader:
    def __init__(self, shader_name: str, vert_src: str, frag_src: str, color_map_src: str = None,
                 normal_map_src: str = None, apply_default_maps=True, **kwargs):
        self.name = shader_name
        self.vert_src = vert_src
        self.frag_src = frag_src
        self.color_map_src = color_map_src
        self.normal_map_src = normal_map_src
        self.apply_default_map = apply_default_maps

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
        if self.apply_default_map:
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
        LOGGER.info(f'Reading {self.vert_src}')
        with open(self.vert_src, 'r') as vp:
            return vp.readlines()

    def default_fragment_shader_code(self):
        LOGGER.info(f'Reading {self.frag_src}')
        with open(self.frag_src, 'r') as fp:
            return fp.readlines()

    def _setup_attribute_pointer(self, attribute_name: str, stride: int, void_pointer: ctypes.c_void_p):
        LOGGER.info(f'Setting up attribute {attribute_name} for shader "{self.name}" with stride {stride}')
        pos_attrib_location = glGetAttribLocation(self.shader_program,
                                                  attribute_name)
        if pos_attrib_location < 0:
            LOGGER.warning(f'Attribute {attribute_name} skipped to set on shader "{self.name}"')
            return
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
                     DEFAULT_SHADER, 'fragment_shader.glsl'),
                 color_map_src: str = None,
                 normal_map_src: str = None,
                 **kwargs):

        self.shader_name = shader_name
        self.vert_src = vert_src
        self.frag_src = frag_src
        self.color_map_src = color_map_src
        self.normal_map_src = normal_map_src

        super().__init__(shader_name=self.shader_name,
                         vert_src=self.vert_src,
                         frag_src=self.frag_src,
                         color_map_src=self.color_map_src,
                         normal_map_src=self.normal_map_src,
                         kwargs=kwargs)


class ConstantShader(Shader):
    def __init__(self,
                 shader_name: str = 'constant_shader',
                 vert_src: str = os.path.join(
                     CONSTANT_SHADER, 'vertex_shader.glsl'),
                 frag_src: str = os.path.join(
                     CONSTANT_SHADER, 'fragment_shader.glsl'),
                 **kwargs):

        self.shader_name = shader_name
        self.vert_src = vert_src
        self.frag_src = frag_src

        super().__init__(shader_name=self.shader_name,
                         vert_src=self.vert_src,
                         frag_src=self.frag_src,
                         apply_default_maps=False,
                         kwargs=kwargs)
