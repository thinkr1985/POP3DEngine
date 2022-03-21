import os
import numpy as np
import imageio
from OpenGL.GL import *
from OpenGL.GLUT import *

from logger import get_logger

LOGGER = get_logger(__file__)
CACHED_TEXTURE_SOURCES = dict()


class TextureMap:
    def __init__(self, texture_path: str, texture_slot: int, **kwargs):
        self._texture_path = texture_path
        self._texture_slot = texture_slot
        self._width = 0
        self._height = 0
        self._texture_type = GL_RGBA
        self._image_format = None
        self._num_channels = 3
        self._level_of_detail = 0   # 0 is for default
        self._wrapping_method = kwargs.get('wrapping_method') or GL_REPEAT
        self._texture_buffer = None
        self._texture_data = None
        self._in_use = False

    def __str__(self):
        return f'Texture2D({self._texture_path}) at {hex(id(self))}'

    def __repr__(self):
        return f'Texture2D({self._texture_path}) at {hex(id(self))}'

    def init_texture(self, reload: bool = False):
        LOGGER.info(f'Creating Texture buffer for {self._texture_path}')
        self.read_texture(reload=reload)
        self._texture_buffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture_buffer)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.wrapping_method)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.wrapping_method)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D,
                     self._level_of_detail,
                     self._texture_type,
                     self._width,
                     self._height,
                     0,
                     self._texture_type,
                     GL_UNSIGNED_BYTE,
                     self._texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def read_texture(self, reload: bool = False):
        if self._texture_path in CACHED_TEXTURE_SOURCES and not reload:
            texture_data = CACHED_TEXTURE_SOURCES.get(self._texture_path)
            self._width = texture_data.get('width')
            self._height = texture_data.get('height')
            self._num_channels = texture_data.get('num_channels')
            self._image_format = texture_data.get('format')
            self._texture_type = texture_data.get('texture_type')
            self._texture_data = texture_data.get('texture_array')
        else:
            LOGGER.info(f'Reading Texture file {self._texture_path}')
            with imageio.get_reader(self._texture_path) as reader:
                # for texture sequences you need to loop through reader length
                self._width, self._height, self._num_channels = reader.get_data(0).shape
                self._image_format = reader.format

                if self._num_channels == 3:
                    self._texture_type = GL_RGB
                elif self._num_channels > 3:
                    self._texture_type = GL_RGBA

                # flipped_image = reader.get_data(0)
                self._texture_data = np.flipud(reader.get_data(0))
                self._texture_data = np.rot90(self._texture_data)
                self._texture_data = np.array(self._texture_data, np.uint8)

                CACHED_TEXTURE_SOURCES.update(
                    {
                        self._texture_path:
                            {
                                'width': self._width,
                                'height': self._height,
                                'num_channels': self._num_channels,
                                'format': self._image_format,
                                'texture_type': self._texture_type,
                                'texture_array': self._texture_data}
                    })
        # following is optional method with PIL
        '''
        image = Image.open(self._texture_path)
        self._texture_data = np.array(list(image.getdata()), np.uint8)
        '''

    @property
    def in_use(self) -> bool:
        return self._in_use

    @in_use.setter
    def in_use(self, val: bool):
        self._in_use = val

    @property
    def texture_slot(self):
        return self._texture_slot

    @property
    def num_channels(self):
        return self._num_channels

    @property
    def wrapping_method(self):
        if self._wrapping_method:
            return self._wrapping_method
        else:
            return GL_REPEAT

    @wrapping_method.setter
    def wrapping_method(self, wrapping_method):
        self._wrapping_method = wrapping_method
        self.reload()

    @property
    def image_format(self):
        return self._image_format

    @property
    def texture(self):
        return self._texture_buffer

    @property
    def texture_data(self):
        return self._texture_data

    @property
    def texture_path(self):
        return self._texture_path

    @texture_path.setter
    def texture_path(self, texture_path: str):
        if not os.path.exists(texture_path):
            LOGGER.error(f'Failed to set Texture path!,'
                         f' File does not exists {texture_path}')
            return
        self._texture_path = texture_path
        self.reload()

    @property
    def level_of_detail(self):
        return self._level_of_detail

    @level_of_detail.setter
    def level_of_detail(self, lod):
        if not isinstance(lod, int):
            LOGGER.error(f'Failed to set lod {lod} of texture '
                         f'{self._texture_path}, lod must be int not '
                         f'{type(lod)}')
            return
        self._level_of_detail = lod
        self.reload()

    def reload(self):
        glDeleteTextures(1, (self._texture_buffer,))
        self.init_texture(reload=True)

    def use(self):
        # if self.in_use:
        #     return

        if self._texture_slot == 0:
            glActiveTexture(GL_TEXTURE0)
        elif self._texture_slot == 1:
            glActiveTexture(GL_TEXTURE1)
        elif self._texture_slot == 2:
            glActiveTexture(GL_TEXTURE2)
        elif self._texture_slot == 3:
            glActiveTexture(GL_TEXTURE3)
        elif self._texture_slot == 4:
            glActiveTexture(GL_TEXTURE4)

        glBindTexture(GL_TEXTURE_2D, self._texture_buffer)
        self.in_use = True

    def destroy(self):
        glBindTexture(GL_TEXTURE_2D, 0)
        glDeleteTextures(1, (self._texture_buffer, ))
        self.in_use = False
