from OpenGL.GL import *
from OpenGL.GLUT import *

from exceptions import (ShaderCompilationError, ShaderProgramLinkError,
                        UnsupportedShaderType)
from logger import get_logger
from constants import (SHADER_SRC, DEFAULT_TEXTURES, STRIDE,
                       SUPPORTED_SHADER_TYPES)
from texture import TextureMap

LOGGER = get_logger(__file__)

CACHED_SHADER_SOURCES = dict()
CACHED_TEXTURE_MAPS = dict()


class Shader:
    def __init__(self, scene, shader_name: str, shader_base_dir: str,
                 color_map_src: str = None, normal_map_src: str = None,
                 apply_default_maps=True, **kwargs):
        self._name = shader_name
        self._scene = scene
        self._shader_base_dir = shader_base_dir
        self._color_map_src = color_map_src
        self._normal_map_src = normal_map_src
        self._apply_default_map = apply_default_maps

        self._color_texture_map = None
        self._normal_texture_map = None
        self._stride = STRIDE
        self._shader_program = glCreateProgram()
        self._active_uniforms = None
        self._active_attributes = None

        self._init_shader()

    @property
    def shader_attribute_pointers(self):
        """
        pointer_offset is nothing but byte offset in the set of vertex data
        for that attribute value.
        example, if "normal" starts at 4th location then byte offset should
        be 3 * 4 = 16
        """
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
        self._create_texture_maps()
        shaders = self._compile_shader_sources()
        glLinkProgram(self._shader_program)

        if not glGetProgramiv(self._shader_program, GL_LINK_STATUS):
            error_ = (glGetProgramInfoLog(self._shader_program))
            raise ShaderProgramLinkError(f'Linking error : {error_}')

        for shader in shaders:
            glDetachShader(self._shader_program, shader)

        self._scene.add_scene_shader(self)

        self._active_uniforms = self.get_all_active_shader_uniforms()
        self._active_attributes = self.get_all_active_shader_attributes()

    @property
    def active_uniforms(self) -> dict:
        return self._active_uniforms

    @property
    def active_attributes(self) -> dict:
        return self._active_attributes

    def _create_texture_maps(self):
        checker_tex = os.path.join(DEFAULT_TEXTURES, 'checker_board.png')
        normal_map = os.path.join(DEFAULT_TEXTURES, 'checker_board_normal.png')

        if self._apply_default_map:
            if not self._color_map_src:
                if checker_tex in CACHED_TEXTURE_MAPS:
                    self._color_texture_map = CACHED_TEXTURE_MAPS.get(
                        checker_tex)
                else:
                    self._color_texture_map = TextureMap(
                        checker_tex, texture_slot=0)
                    self._color_texture_map.init_texture()
                    CACHED_TEXTURE_MAPS.update(
                        {checker_tex: self._color_texture_map})

        if self._apply_default_map:
            if not self._normal_map_src:
                if normal_map in CACHED_TEXTURE_MAPS:
                    self._normal_texture_map = CACHED_TEXTURE_MAPS.get(
                        normal_map)
                else:
                    self._normal_texture_map = TextureMap(
                        normal_map, texture_slot=1)
                    self._normal_texture_map.init_texture()
                    CACHED_TEXTURE_MAPS.update(
                        {normal_map: self._normal_texture_map})

    def _compile_shader_sources(self) -> list:
        LOGGER.info(f'Compiling shader {self._name}')

        shader_dir = os.path.join(SHADER_SRC, self._shader_base_dir)
        if not os.path.exists(shader_dir):
            raise ShaderCompilationError(
                f'Failed to locate shader folder "{shader_dir}" to compile '
                f'shader "{self._name}"')

        found = False
        shaders = list()

        for file_ in os.listdir(shader_dir):
            if file_.endswith('.glsl'):
                shader_type = SUPPORTED_SHADER_TYPES.get(file_.split('_')[0])
                if not shader_type:
                    raise UnsupportedShaderType(
                        f'Failed to find shader type for {file_.split("_")[0]}'
                        f' in "SUPPORTED_SHADER_TYPES" variable of '
                        f'constants.py')

                shader = self._compile_shader(
                    shader_src_file=os.path.join(shader_dir, file_),
                    shader_type=shader_type)

                found = True
                shaders.append(shader)

        if not found:
            raise ShaderCompilationError(
                f'No ".glsl" file found im the shader dir {shader_dir} '
                f'to compile shader "{self._name}"')
        return shaders

    def _compile_shader(self, shader_src_file: str, shader_type: GL_SHADER_TYPE) -> GL_SHADER:
        if shader_src_file not in CACHED_SHADER_SOURCES:
            with open(shader_src_file, 'r') as rp:
                LOGGER.info(f'reading shader source {shader_src_file}')
                shader_lines = rp.readlines()
                CACHED_SHADER_SOURCES.update({shader_src_file: shader_lines})
        else:
            shader_lines = CACHED_SHADER_SOURCES.get(shader_src_file)

        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_lines)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error_ = glGetShaderInfoLog(shader).decode()
            raise ShaderCompilationError(
                f"shader {shader_src_file} compilation error: {error_}"
            )
        glAttachShader(self._shader_program, shader)
        return shader

    @property
    def name(self) -> str:
        return self._name

    @property
    def shader_program(self) -> int:
        return self._shader_program

    @property
    def color_map_src(self) -> str:
        return self._color_map_src

    @property
    def normal_map_src(self) -> str:
        return self._normal_map_src

    @property
    def apply_default_map(self) -> bool:
        return self._apply_default_map

    @property
    def stride(self) -> int:
        return self._stride

    @stride.setter
    def stride(self, stride_val: int):
        self._stride = stride_val

    def get_all_active_shader_uniforms(self) -> dict:
        attr_count = glGetProgramiv(self._shader_program, GL_ACTIVE_UNIFORMS)
        active_uniforms = dict()

        for attr_index in range(attr_count):
            attribute = (glGetActiveUniform(self._shader_program, attr_index))
            active_uniforms.update(
                {
                    attribute[0].decode('utf-8'): {
                                    'location': attr_index,
                                    'size': attribute[1],
                                    'type': attribute[2]
                                }
                })
        return active_uniforms

    def get_all_active_shader_attributes(self) -> dict:
        attr_count = glGetProgramiv(self._shader_program, GL_ACTIVE_ATTRIBUTES)
        active_attributes = dict()

        for attr_index in range(attr_count):
            attribute = (glGetActiveAttrib(self._shader_program, attr_index))
            active_attributes.update(
                {
                    attribute[0].decode('utf-8'): {
                                    'location': attr_index,
                                    'size': attribute[1],
                                    'type': attribute[2]
                                }
                })
        return active_attributes

    def setup_attribute_pointers(self, entity, offset: int):
        self.use()

        for attribute_name, attrib_data in self.shader_attribute_pointers.items():
            _location = glGetAttribLocation(self._shader_program, attribute_name)
            '''
            if glGetAttribLocation returns you -1, don't necessarily mean
            there is problem, glsl removes the attributes if not used in 
            shader program while compiling hence it returns -1.
            '''
            if _location < 0:
                LOGGER.warning(
                    f'Attribute "{attribute_name}" skipped to set '
                    f'on the shader "{self._name}" for entity {entity.name}')
                continue
            attrib_location = attrib_data.get('location')
            # attrib_pointer_offset = attrib_data.get('pointer_offset')
            # LOGGER.info(
            #     f'Setting attribute "{attribute_name}" on the '
            #     f'shader "{self._name}" for entity {entity.name}')

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
        if not glGetProgramiv(self._shader_program, GL_LINK_STATUS):
            glLinkProgram(self._shader_program)

        glUseProgram(self._shader_program)

        if self._color_texture_map:
            self._color_texture_map.use()
        if self._normal_texture_map:
            self._normal_texture_map.use()

    def destroy(self):
        glDeleteProgram(self._shader_program)

        if self._color_texture_map:
            self._color_texture_map.destroy()
        if self._normal_texture_map:
            self._normal_texture_map.destroy()
        for attr_name, index in self.shader_attribute_pointers.items():
            pos_attrib_location = glGetAttribLocation(self._shader_program,
                                                      attr_name)
            if pos_attrib_location > 0:
                glDisableVertexAttribArray(pos_attrib_location)


class DefaultShader(Shader):
    def __init__(self,
                 scene,
                 shader_name: str = 'default_shader',
                 shader_base_dir: str = os.path.join(SHADER_SRC, 'lambert'),
                 color_map_src: str = None,
                 normal_map_src: str = None,
                 **kwargs):

        super().__init__(
                        scene=scene,
                        shader_name=shader_name,
                        shader_base_dir=shader_base_dir,
                        color_map_src=color_map_src,
                        normal_map_src=normal_map_src,
                        kwargs=kwargs
                        )


class ConstantShader(Shader):
    def __init__(self,
                 scene,
                 shader_name: str = 'constant_shader',
                 shader_base_dir: str = os.path.join(SHADER_SRC, 'constant'),
                 color: list = None,
                 **kwargs):

        super().__init__(
                        scene=scene,
                        shader_name=shader_name,
                        shader_base_dir=shader_base_dir,
                        apply_default_maps=False,
                        kwargs=kwargs
                        )
        if color is None:
            color = [1.0, 1.0, 1.0, 1.0]
        if len(color) == 3:
            color.append(1.0)
        self._color = color
        self._set_color(
            self._color[0], self._color[1], self.color[2], self.color[3]
        )

    @property
    def color(self) -> list:
        return self._color

    @color.setter
    def color(self, color: list):
        if len(color) < 3 or len(color) > 4:
            LOGGER.error(
                f'Failed to set color value "({color})" on shader '
                f'{self._name}, input color list should have 4 elements'
                f' representing r,g,b,a in it.')
            return
        if len(color) == 3:
            self._color = [color[0], color[1], color[2], 1.0]
        else:
            self._color = color
        self._set_color(r=self._color[0], g=self._color[1], b=self._color[2],
                        a=self._color[3])

    def _set_color(self, r: float, g: float, b: float, a: float = 1.0):

        self.use()
        color_location = glGetUniformLocation(
            self._shader_program, "constant_color")
        glUniform4f(color_location, r, g, b, a)
