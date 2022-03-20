import numpy as np
from OpenGL.GL import *
from renderer import Renderer
from entity import Entity
from logger import get_logger
from shaders import DefaultShader, ConstantShader
from cameras import PerspectiveCamera
from grid import Grid
import lights
from lights import AmbientLight

LOGGER = get_logger(__file__)


class Scene:
    def __init__(self, **kwargs):
        self._width = 512
        self._height = 512

        self._entities = dict()
        self._shaders = dict()
        self._lights = dict()
        self._default_shader: DefaultShader = DefaultShader(scene=self)
        self.constant_shader = ConstantShader(scene=self)
        self._renderer = Renderer(self)
        self._cameras = dict()
        self._active_camera = None

        self.ambient_light = AmbientLight(scene=self, color=[1.0, 1.0, 1.0], light_name='default_ambient_light')
        self.add_entity(self.ambient_light, update_uid=False)
        self._grid = Grid(scene=self)
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
    def grid(self):
        return self._grid

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
    def render_camera(self):
        return self.active_camera

    @property
    def renderer(self):
        return self._renderer

    @property
    def default_shader(self) -> DefaultShader:
        return self._default_shader

    @property
    def shaders(self) -> dict:
        return self._shaders

    @property
    def lights(self) -> dict:
        return self._lights

    def add_scene_shader(self, shader):
        if shader.name not in self._shaders:
            self._shaders.update({shader.name: shader})
        else:
            LOGGER.error(
                f'Failed to add shader {shader.name} to scene'
                f' since similar name shader already present!'
            )

    def add_scene_light(self, light):
        if light.name not in self._lights:
            self._shaders.update({light.name: light})
        else:
            LOGGER.error(
                f'Failed to add light "{light.name}" to scene'
                f' since similar name light already present!'
            )

    def add_entity(self, entity: str or list, update_uid=False):
        if not isinstance(entity, list):
            entities = [entity]
        else:
            entities = entity

        for ent in entities:
            if isinstance(ent, Entity) or isinstance(ent, AmbientLight):
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
                    f'do not have valid type : {type(ent)}')

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
