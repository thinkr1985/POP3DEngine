import os
import pyrr
import numpy as np
from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLUT import *

from exceptions import CameraCreationError
from logger import get_logger

LOGGER = get_logger(__file__)


class Camera:
    def __init__(self,
                 focal_length: float,
                 width: int,
                 height: int,
                 far_clip: float,
                 near_clip: float,
                 camera_type: str,
                 camera_name: str,
                 scene,
                 **kwargs):

        self._focal_length = focal_length
        self._width = width
        self._height = height
        self._far_clip = far_clip
        self._near_clip = near_clip
        self._camera_type = camera_type
        self._camera_name = camera_name
        self._scene = scene

        self._identity_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        self._translation = [0, 0, -2]
        self._rotation = [-30, 0, 0]
        self._model_uniform_location = None
        self._project_uniform_location = None
        self._view_uniform_location = None

        self._init_camera()

    def __new__(cls, *args, **kwargs):
        scene = kwargs.get('scene')
        if not scene:
            raise CameraCreationError(
                'Failed to create camera, scene not provided!')

        if not kwargs.get('width'):
            raise CameraCreationError(
                'Failed to create camera, width not provided!')

        if not kwargs.get('height'):
            raise CameraCreationError(
                'Failed to create camera, height not provided!')

        camera_name = kwargs.get('camera_name')
        if not camera_name:
            raise CameraCreationError(
                'Failed to create camera, camera_name not provided!')

        if camera_name in scene.cameras:
            raise CameraCreationError(
                f'Failed to create camera, camera with name {camera_name} '
                f'already exists in the scene!'
            )
        return super(Camera, cls).__new__(cls)

    def __str__(self):
        return f'{self._camera_type}({self._camera_name}) at {hex(id(self))}'

    def __repr__(self):
        return f'{self._camera_type}({self._camera_name}) at {hex(id(self))}'

    def _init_camera(self):
        self._scene.add_camera(self)

    @property
    def focal_length(self):
        return self._focal_length

    @property
    def aspect_ratio(self):
        return self._width / self._height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: int):
        self._width = int(width)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: int):
        self._height = int(height)

    @property
    def camera_type(self):
        return self._camera_type

    @property
    def camera_name(self):
        return self._camera_name

    @camera_name.setter
    def camera_name(self, new_name: str):
        self._camera_name = new_name

    @property
    def far_clip(self) -> float:
        return self._far_clip

    @far_clip.setter
    def far_clip(self, far_clip: float):
        self._far_clip = float(far_clip)

    @property
    def near_clip(self) -> float:
        return self._near_clip

    @near_clip.setter
    def near_clip(self, near_clip: float):
        self._near_clip = float(near_clip)

    @property
    def scene(self):
        return self._scene

    @property
    def shader(self):
        return self._scene.default_shader

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, translation: list):
        self._translation = translation

    @property
    def translateX(self):
        return self._translation[0]

    @translateX.setter
    def translateX(self, value):
        self._translation = [value, self.translateY, self.translateZ]

    @property
    def translateY(self):
        return self._translation[1]

    @translateY.setter
    def translateY(self, value):
        self._translation = [self.translateX, value, self.translateZ]

    @property
    def translateZ(self):
        return self._translation[2]

    @translateZ.setter
    def translateZ(self, value):
        self._translation = [self.translateX, self.translateY, value]

    @property
    def pitch(self):
        return self._rotation[0]

    @pitch.setter
    def pitch(self, value):
        self._rotation = [value, self.roll, self.yaw]

    @property
    def roll(self):
        return self._rotation[1]

    @roll.setter
    def roll(self, value):
        self._rotation = [self.pitch, value, self.yaw]

    @property
    def yaw(self):
        return self._rotation[2]

    @yaw.setter
    def yaw(self, value):
        self._rotation = [self.pitch, self.roll, value]

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, rotation: list):
        self._rotation = rotation

    @property
    def identity_matrix(self):
        return self._identity_matrix

    @property
    def model_uniform_location(self) -> int:
        return self._model_uniform_location

    @property
    def project_uniform_location(self) -> int:
        return self._project_uniform_location

    @property
    def view_uniform_location(self) -> int:
        return self._view_uniform_location

    def reset_transformations(self):
        self._translation = [0, 0, -2]
        self._rotation = [-30, 0, 0]

    def use(self):
        """
            pitch: rotation around x axis
            roll:rotation around z axis
            yaw: rotation around y axis
        """

        transform_matrix = pyrr.matrix44.create_perspective_projection_matrix(
            fovy=self._focal_length,
            aspect=self.aspect_ratio,
            near=self._near_clip,
            far=self._far_clip,
            dtype=np.float32
        )

        rotation_matrix = pyrr.matrix44.multiply(
            m1=self._identity_matrix,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self._rotation), dtype=np.float32
            )
        )
        model_matrix = pyrr.matrix44.multiply(
            m1=rotation_matrix,
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self._translation), dtype=np.float32
            )
        )
        for shader in self.scene.shaders.values():
            shader.use()
            self._project_uniform_location = glGetUniformLocation(shader.shader_program, "projection")
            self._model_uniform_location = glGetUniformLocation(shader.shader_program, "model")

            glUniformMatrix4fv(self.project_uniform_location, 1, GL_FALSE,
                               transform_matrix)

            glUniformMatrix4fv(self._model_uniform_location, 1, GL_FALSE,
                               model_matrix)

    def destroy(self):
        self._scene.remove_camera(camera_name=self._camera_name)


class PerspectiveCamera(Camera):
    def __init__(self, width, height, camera_name, scene, focal_length=35.0,
                 near_clip=0.1, far_clip=10.0, **kwargs):
        super().__init__(focal_length=focal_length,
                         width=width,
                         height=height,
                         far_clip=far_clip,
                         near_clip=near_clip,
                         camera_name=camera_name,
                         camera_type='PerspectiveCamera',
                         scene=scene,
                         kwargs=kwargs)
        LOGGER.info(f'Creating Perspective camera with name {camera_name}')
