from renderer import Renderer
from entity import Entity
from logger import get_logger
from shaders import DefaultShader, ConstantShader
from cameras import PerspectiveCamera
from grid import Grid
from lights import AmbientLight
from exceptions import SceneCreationError

LOGGER = get_logger(__file__)


class Scene:
    def __init__(self, width: int, height: int, scene_name: str = 'default_scene', **kwargs):
        self._scene_name = scene_name
        self._width = width or 512
        self._height = height or 512

        self._entities = dict()
        self._shaders = dict()
        self._lights = dict()
        self._default_shader: DefaultShader = DefaultShader(scene=self)
        self.constant_shader = ConstantShader(scene=self)
        self._renderer = Renderer(self)
        self._active_camera = None
        self._init_scene()

        self.ambient_light = AmbientLight(scene=self,
                                          light_name='default_ambient_light',
                                          color=[0.1, 0.0, 0.5])
        self.add_entity(self.ambient_light, update_uid=False)
        self._grid = Grid(scene=self)

    def __new__(cls, *args, **kwargs):
        scene_name = kwargs.get('scene_name')
        width = kwargs.get('width')
        height = kwargs.get('height')

        if not scene_name:
            raise SceneCreationError('Cant create scene without "scene_name"')
        if not width:
            raise SceneCreationError('Cant create scene without width')
        if not height:
            raise SceneCreationError('Cant create a scene without height')

        return super(Scene, cls).__new__(cls)

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
    def scene_name(self) -> str:
        return self._scene_name

    @property
    def grid(self) -> Grid:
        return self._grid

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def entities(self) -> dict:
        return self._entities

    @property
    def cameras(self) -> list:
        camera_entities = list()
        for ent_uid, ent in self._entities.items():
            if ent.type == 'cameraEntity':
                camera_entities.append(ent)
        return camera_entities

    @property
    def active_camera(self) -> Entity:
        return self._active_camera

    @property
    def render_camera(self) -> Entity:
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

    def create_perspective_camera(self, camera_name: str, width: int,
                                  height: int, near_clip: float = 0.1,
                                  far_clip: float = 10.0) -> PerspectiveCamera:
        camera = PerspectiveCamera(camera_name=camera_name,
                                   width=width,
                                   height=height,
                                   near_clip=near_clip,
                                   far_clip=far_clip,
                                   scene=self)
        self.add_entity(camera)
        return camera

    def get_all_lights(self) -> list:
        light_list = list()

        for ent_uid, entity in self.entities.items():
            if entity.type in ['ambientLightEntity', 'lightEntity']:
                light_list.append(entity)
        return light_list
