import os
import numpy as np
from OpenGL.GL import *

from logger import get_logger
from entity import Entity
from constants import DEFAULT_SHAPES_DIR
from utilities import utils
LOGGER = get_logger(__file__)


class Light(Entity):
    def __init__(self,
                 color: list,
                 scene,
                 shape_buffers: dict,
                 light_name: str,
                 draw_method=GL_LINES,
                 transformations=None,
                 **kwargs):
        super().__init__(
            entity_name=light_name,
            buffers=shape_buffers,
            scene=scene,
            draw_method=draw_method,
            shader=scene.constant_shader,
            transformations=transformations,
            kwargs=kwargs)

        self._color = color or [1.0, 1.0, 1.0]
        self._intensity = 1.0
        self._type = 'lightEntity'
        # self.scene.add_scene_light(self)

    @property
    def color(self) -> np.array:
        return np.array(self._color, dtype=np.float32)

    @color.setter
    def color(self, val: list):
        if not len(val) == 3:
            LOGGER.error(
                'Light Color must have 3 elements .i.e. R,G,B.'
                f'Failed to set current color value ({val}) on '
                f'light {self.name}')
            return
        self._color = val

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, intensity: int):
        self._intensity = intensity


class AmbientLight(Light):
    def __init__(self, scene, light_name: str, color: list = None,
                 transformations=None, **kwargs):
        light_mesh_data = utils.read_pymesh_file(
            os.path.join(DEFAULT_SHAPES_DIR, 'light_bulb.pymesh'))

        _transformations = transformations or [0, 10, -10, 0, 0, 0, 1, 1, 1]

        super().__init__(color=color,
                         scene=scene,
                         light_name=light_name,
                         shape_buffers=light_mesh_data[0]['buffers'],
                         transformations=_transformations,
                         draw_method=GL_TRIANGLES,
                         kwargs=kwargs)

        self._type = 'ambientLightEntity'
