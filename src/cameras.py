import pyrr
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

from entity import Entity
from utilities import utils
from constants import (NUM_LIGHT_LIMITS, ATMOSPHERE_DIFFUSE_COLOR,
                       ATMOSPHERE_DIFFUSE_INTENSITY, DEFAULT_SHAPES_DIR)
from logger import get_logger

LOGGER = get_logger(__file__)


class Camera(Entity):
    def __init__(self,
                 focal_length: float,
                 width: float,
                 height: float,
                 far_clip: float,
                 near_clip: float,
                 camera_name: str,
                 shape_buffers: dict,
                 scene,
                 draw_method=GL_LINES,
                 transformations=None,
                 **kwargs):
        super().__init__(
            entity_name=camera_name,
            buffers=shape_buffers,
            scene=scene,
            draw_method=draw_method,
            shader=scene.constant_shader,
            transformations=transformations,
            kwargs=kwargs)

        self._type = 'cameraEntity'
        self._focal_length = focal_length
        self._width = width
        self._height = height
        self._far_clip = far_clip
        self._near_clip = near_clip

        self.theta = 0
        self.phi = 0
        self.update_vectors()

    def update_vectors(self):
        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi))
            ],
            dtype=np.float32
        )

        globalUp = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.cross(self.forwards, globalUp)
        self.up = np.cross(self.right, self.forwards)

    @property
    def focal_length(self) -> float:
        return self._focal_length

    @property
    def aspect_ratio(self) -> float:
        return self._width / self._height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, width: int):
        self._width = int(width)

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, height: int):
        self._height = int(height)

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

    def use(self):
        """
            pitch: rotation around x axis
            roll:rotation around z axis
            yaw: rotation around y axis
        """
        projection_matrix = pyrr.matrix44.create_perspective_projection_matrix(
            fovy=self._focal_length,
            aspect=self.aspect_ratio,
            near=self._near_clip,
            far=self._far_clip,
            dtype=np.float32
        )
        view_matrix = pyrr.matrix44.create_look_at(
            eye=self.transformations.position,
            target=self.transformations.position + self.forwards,
            up=self.up,
            dtype=np.float32
        )
        rotation_matrix = pyrr.matrix44.multiply(
            m1=self.transformations.identity_matrix,
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.transformations.rotate.np_array),
                dtype=np.float32
            )
        )
        model_matrix = pyrr.matrix44.multiply(
            m1=rotation_matrix,
            m2=pyrr.matrix44.create_from_translation(
                vec=self.transformations.translate.np_array,
                dtype=np.float32
            )
        )

        scene_lights = self.scene.get_all_lights()

        for shader in self.scene.shaders.values():
            shader.use()
            atmosphere_color_location = glGetUniformLocation(
                shader.shader_program,
                "atmosphereColor")
            atmosphere_intensity_location = glGetUniformLocation(
                shader.shader_program,
                "atmosphereIntensity")

            glUniform3fv(atmosphere_color_location, 1, GL_FALSE,
                               ATMOSPHERE_DIFFUSE_COLOR)

            glUniform1fv(atmosphere_intensity_location, 1, GL_FALSE,
                               ATMOSPHERE_DIFFUSE_INTENSITY)

            project_shade_location = glGetUniformLocation(shader.shader_program, "projection")
            model_shade_location = glGetUniformLocation(shader.shader_program, "model")
            view_uniform_location = glGetUniformLocation(shader.shader_program, "view")
            camera_position_uniform = glGetUniformLocation(shader.shader_program, "cameraPosition")

            glUniformMatrix4fv(project_shade_location, 1, GL_FALSE,
                               projection_matrix)

            glUniformMatrix4fv(model_shade_location, 1, GL_FALSE, model_matrix)

            glUniformMatrix4fv(view_uniform_location, 1, GL_FALSE, view_matrix)

            glUniform3fv(camera_position_uniform, 1, GL_FALSE,
                               self.transformations.position)

            # sending lights information
            light_location = {
                "position": [
                    glGetUniformLocation(shader.shader_program, f"Lights[{i}].position")
                    for i in range(NUM_LIGHT_LIMITS)
                ],
                "color": [
                    glGetUniformLocation(shader.shader_program, f"Lights[{i}].color")
                    for i in range(NUM_LIGHT_LIMITS)
                ],
                "intensity": [
                    glGetUniformLocation(shader.shader_program, f"Lights[{i}].intensity")
                    for i in range(NUM_LIGHT_LIMITS)
                ]
            }

            for i, light in enumerate(scene_lights):
                glUniform3fv(light_location["position"][i], 1,
                             light.transformations.position)
                glUniform3fv(light_location["color"][i], 1, light.color)
                glUniform1f(light_location["intensity"][i], light.intensity)


class PerspectiveCamera(Camera):
    def __init__(self, width: float, height, camera_name: str, scene,
                 focal_length: float = 35.0, near_clip: float = 0.1,
                 far_clip: float = 10.0, transformations: list = None,
                 **kwargs):

        camera_mesh_data = utils.read_pymesh_file(
            os.path.join(DEFAULT_SHAPES_DIR, 'camera.pymesh'))

        _transformations = transformations or [0, 10, -10, 0, 0, 0, 1, 1, 1]

        super().__init__(focal_length=focal_length,
                         width=width,
                         height=height,
                         far_clip=far_clip,
                         near_clip=near_clip,
                         camera_name=camera_name,
                         scene=scene,
                         draw_method=GL_LINES,
                         shape_buffers=camera_mesh_data[0]['buffers'],
                         kwargs=kwargs)
