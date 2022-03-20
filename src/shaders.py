import numpy as np

from exceptions import (VertexShaderCompilationError,
                        FragmentShaderCompilationError, ShaderProgramLinkError)
from OpenGL.GL import *
from OpenGL.GLUT import *

from logger import get_logger
from constants import DEFAULT_SHADER, CONSTANT_SHADER, DEFAULT_TEXTURES, STRIDE
from texture import TextureMap

LOGGER = get_logger(__file__)


class Shader:
    def __init__(self, scene, shader_name: str, vert_src: str, frag_src: str, color_map_src: str = None,
                 normal_map_src: str = None, apply_default_maps=True, **kwargs):
        self.name = shader_name
        self.scene = scene
        self.vert_src = vert_src
        self.frag_src = frag_src
        self.color_map_src = color_map_src
        self.normal_map_src = normal_map_src
        self.apply_default_map = apply_default_maps

        self.color_texture_map = None
        self.normal_texture_map = None
        self._in_use = False
        self._stride = STRIDE
        self.scene.add_scene_shader(self)
        self.shader_program = glCreateProgram()
        self._init_shader()

    @property
    def shader_attributes(self):
        '''
        pointer_offset is nothing but byte offset in the set of vertex data
        for that attribute value.
        example, if "normal" starts at 4th location then byte offset should
        be 3 * 4 = 16
        '''
        shader_attribute_dict = {
            'vertexPosition':
                {'location': 0, 'pointer_offset': 0},
            'vertexColor':
                {'location': 1, 'pointer_offset': 24},
            'vertexUV':
                {'location': 2, 'pointer_offset': 40},
            'vertexNormal':
                {'location': 3, 'pointer_offset': 12}
        }
        return shader_attribute_dict

    def _init_shader(self):
        checker_tex = os.path.join( DEFAULT_TEXTURES, 'checker_board.png')
        normal_map = os.path.join(DEFAULT_TEXTURES, 'checker_board_normal.png')

        if self.apply_default_map:
            if not self.color_map_src:
                self.color_texture_map = TextureMap(checker_tex, texture_slot=0)
                self.color_texture_map.init_texture()
            if not self.normal_map_src:
                self.normal_texture_map = TextureMap(normal_map, texture_slot=1)
                self.normal_texture_map.init_texture()

        LOGGER.info(f'Compiling shader {self.name}')

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

    @property
    def in_use(self) -> bool:
        return self._in_use

    @in_use.setter
    def in_use(self, val:bool):
        self._in_use = val

    @property
    def stride(self) -> int:
        return self._stride

    @stride.setter
    def stride(self, stride_val: int):
        self._stride = stride_val

    def default_vertex_shader_code(self):
        LOGGER.info(f'Reading {self.vert_src}')
        with open(self.vert_src, 'r') as vp:
            return vp.readlines()

    def default_fragment_shader_code(self):
        LOGGER.info(f'Reading {self.frag_src}')
        with open(self.frag_src, 'r') as fp:
            return fp.readlines()

    def get_all_active_shader_uniforms(self) -> dict:
        attr_count = glGetProgramiv(self.shader_program, GL_ACTIVE_UNIFORMS)
        active_uniforms = dict()

        for attr_index in range(attr_count):
            attribute = (glGetActiveUniform(self.shader_program, attr_index))
            active_uniforms.update(
                {
                    attr_index: {
                                    'name': attribute[0].decode('utf-8'),
                                    'size': attribute[1],
                                    'type': attribute[2]
                                }
                })
        return active_uniforms

    def get_all_active_shader_attributes(self) -> dict:
        attr_count = glGetProgramiv(self.shader_program, GL_ACTIVE_ATTRIBUTES)
        active_attributes = dict()

        for attr_index in range(attr_count):
            attribute = (glGetActiveAttrib(self.shader_program, attr_index))
            active_attributes.update(
                {
                    attr_index: {
                                    'name': attribute[0].decode('utf-8'),
                                    'size': attribute[1],
                                    'type': attribute[2]
                                }
                })
        return active_attributes

    def setup_attribute_pointers(self, entity, offset: int):
        self.use()

        for attribute_name, attrib_data in self.shader_attributes.items():
            _location = glGetAttribLocation(self.shader_program, attribute_name)
            '''
            if glGetAttribLocation returns you -1, don't necessarily mean
            there is problem, glsl removes the attributes if not used in 
            shader program while compiling hence it returns -1.
            '''
            if _location < 0:
                LOGGER.warning(
                    f'Attribute "{attribute_name}" skipped to set '
                    f'on the shader "{self.name}"')
                continue
            attrib_location = attrib_data.get('location')
            attrib_pointer_offset = attrib_data.get('pointer_offset')
            LOGGER.info(
                f'Setting attribute "{attribute_name}" on the '
                f'shader "{self.name}"')

            glBindBuffer(GL_ARRAY_BUFFER, entity.vertex_buffer)
            glEnableVertexAttribArray(attrib_location)

            glVertexAttribPointer(attrib_location,
                                  3,
                                  GL_FLOAT,
                                  GL_FALSE,
                                  self.stride,
                                  ctypes.c_void_p(offset)
                                  )
            glBindBuffer(GL_ARRAY_BUFFER,
                         entity.index_buffer)

    def use(self):
        # if self.in_use:
        #     return
        if not glGetProgramiv(self.shader_program, GL_LINK_STATUS):
            glLinkProgram(self.shader_program)

        glUseProgram(self.shader_program)

        if self.color_texture_map:
            self.color_texture_map.use()
        if self.normal_texture_map:
            self.normal_texture_map.use()

        self.in_use = True

    def destroy(self):
        glDeleteProgram(self.shader_program)

        if self.color_texture_map:
            self.color_texture_map.destroy()
        if self.normal_texture_map:
            self.normal_texture_map.destroy()
        for attr_name, index in self.shader_attributes.items():
            pos_attrib_location = glGetAttribLocation(self.shader_program,
                                                      attr_name)
            if pos_attrib_location > 0:
                glDisableVertexAttribArray(pos_attrib_location)
        self.in_use = False


class DefaultShader(Shader):
    def __init__(self,
                 scene,
                 shader_name: str = 'default_shader',
                 vert_src: str = os.path.join(
                     DEFAULT_SHADER, 'vertex_shader.glsl'),
                 frag_src: str = os.path.join(
                     DEFAULT_SHADER, 'fragment_shader.glsl'),
                 color_map_src: str = None,
                 normal_map_src: str = None,
                 **kwargs):

        super().__init__(
                        scene=scene,
                        shader_name=shader_name,
                        vert_src=vert_src,
                        frag_src=frag_src,
                        color_map_src=color_map_src,
                        normal_map_src=normal_map_src,
                        kwargs=kwargs
                        )


class ConstantShader(Shader):
    def __init__(self,
                 scene,
                 shader_name: str = 'constant_shader',
                 vert_src: str = os.path.join(
                     CONSTANT_SHADER, 'vertex_shader.glsl'),
                 frag_src: str = os.path.join(
                     CONSTANT_SHADER, 'fragment_shader.glsl'),
                 color: list = None,
                 **kwargs):

        super().__init__(
                        scene=scene,
                        shader_name=shader_name,
                        vert_src=vert_src,
                        frag_src=frag_src,
                        apply_default_maps=False,
                        kwargs=kwargs
                        )
        if color is None:
            color = [1.0, 1.0, 1.0, 1.0]
        self._color = color
        self._set_color(
            self._color[0], self._color[1], self.color[2], self.color[3]
        )

    @property
    def color(self) -> list:
        return self._color

    @color.setter
    def color(self, color: list):
        if not len(color) == 4:
            LOGGER.error(
                f'Failed to set color value "({r},{g},{b},{a})" on shader '
                f'{self.name}, input color list should have 4 elements'
                f' representing r,g,b,a in it.')
            return
        self._color = color
        self._set_color(color[0], color[1], color[2], color[3])

    def _set_color(self, r: float, g: float, b: float, a: float = 1.0):
        if not r or not b or not g:
            LOGGER.error(
                f'Failed to set color value "({r},{g},{b},{a})" on shader '
                f'{self.name}, input color list should have 3 elements'
                f' representing r,g,b in it.')
            return

        self.use()
        color_location = glGetUniformLocation(
            self.shader_program, "constant_color")
        glUniform4f(color_location, r, g, b, a)
