import numpy as np
import pyrr

from logger import get_logger

LOGGER = get_logger(__file__)


class Transformations:
    def __init__(self, entity, transformations: list = None, **kwargs):
        self._entity = entity
        self._transformations = transformations or [0, 0, 0, 0, 0, 0, 1, 1, 1]
        self._identity_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        self._translation = Translation(self, self._transformations[:3])
        self._rotation = Rotation(self, self._transformations[3:6])
        self._scale = Scale(self, self._transformations[6:])
        self._init_transformations()

    def __new__(cls, *args, **kwargs):
        transformations = kwargs.get('transformations')
        entity = kwargs.get('entity')

        if transformations:

            if not isinstance(transformations, list) \
                    and not isinstance(transformations, tuple):
                LOGGER.error(
                    f'Failed to create Transformation component of entity'
                    f' {entity.name}, provided transformations should be either'
                    f' list of tuple type!')
                return

            if not len(transformations) == 9:
                LOGGER.error(
                    f'Failed to create Transformation component of entity'
                    f' {entity.name}, provided transformations element count '
                    f'is  not equal to 9')
                return
        return super(Transformations, cls).__new__(cls)

    def __str__(self):
        return f'Transformations({self._entity.name}, {self._transformations})'

    def __repr__(self):
        return f'Transformations({self._entity.name}, {self.transformations})'

    def _init_transformations(self):
        pass

    @property
    def transformations(self) -> list:
        return self._transformations

    def update_transformations(self):
        self._transformations = [self.translation[0],
                                 self.translation[1],
                                 self.translation[2],
                                 self.rotation[0],
                                 self.rotation[1],
                                 self.rotation[2],
                                 self.scale[0],
                                 self.scale[1],
                                 self.scale[2]]

    @property
    def identity_matrix(self) -> pyrr.matrix44:
        return self._identity_matrix

    @property
    def translate(self):
        return self._translation

    @property
    def rotate(self):
        return self._rotation

    @property
    def size(self):
        return self._scale

    @property
    def position(self) -> np.array:
        return self._translation.np_array

    @property
    def translation(self) -> list:
        return self._translation.translation

    @translation.setter
    def translation(self, val: list):
        self._translation.translation = val

    @property
    def rotation(self) -> list:
        return self._rotation.rotation

    @rotation.setter
    def rotation(self, val: list):
        self._rotation.rotation = val

    @property
    def scale(self) -> list:
        return self._scale.scale

    @scale.setter
    def scale(self, val: list):
        self._scale.scale = val

    def reset_transformations(self):
        self._translation.translation = [0, 0, 0]
        self._rotation.rotation = [0, 0, 0]
        self._scale.scale = [1, 1, 1]


class TransformBase:
    def __init__(self, transformation: Transformations,
                 base_value: list, type_: str = 'TransformBase', **kwargs):
        self._transformations = transformation
        self._transform_base = base_value
        self._type = type_

    def __str__(self):
        return f'{self._type}({self._transform_base}) @ {self.transformations.entity.name}'

    def __repr__(self):
        return f'{self._type}({self._transform_base}) @ {self.transformations.entity.name}'

    @property
    def np_array(self) -> np.array:
        return np.array(self._transform_base, dtype=np.float32)

    @property
    def transformations(self) -> Transformations:
        return self.transformations

    @property
    def transform_base(self) -> list:
        return self._transform_base

    @transform_base.setter
    def transform_base(self, val: list):
        if isinstance(val, tuple):
            val = list(val)

        if not len(val) == 3:
            LOGGER.error(
                f'Failed to set {self._type} on entity'
                f' {self._transformations.entity.name},'
                f'input {self._type} list element count should be 3')
            return
        self._transform_base = val
        self._transformations.update_transformations()

    @property
    def x(self) -> float:
        return self._transform_base[0]

    @x.setter
    def x(self, val: float):
        if isinstance(val, float) or isinstance(val, int):
            self.transform_base = [val,
                                   self._transform_base[1],
                                   self._transform_base[2]]
            self._transformations.update_transformations()

    @property
    def y(self) -> float:
        return self._transform_base[1]

    @y.setter
    def y(self, val: float):
        if isinstance(val, float) or isinstance(val, int):
            self.transform_base = [self._transform_base[0],
                                   val,
                                   self._transform_base[2]]
            self._transformations.update_transformations()

    @property
    def z(self) -> float:
        return self._transform_base[2]

    @z.setter
    def z(self, val: float):
        if isinstance(val, float) or isinstance(val, int):
            self.transform_base = [self._transform_base[0],
                                   self._transform_base[1],
                                   val]
            self._transformations.update_transformations()


class Translation(TransformBase):
    def __init__(self, transformation: Transformations, base_value: list,
                 type_='Translation', **kwargs):
        super().__init__(
            transformation=transformation, base_value=base_value, type_=type_,
            kwargs=kwargs
        )

    @property
    def translation(self) -> list:
        return self.transform_base

    @translation.setter
    def translation(self, val: list):
        self.transform_base = val


class Rotation(TransformBase):
    '''
        pitch: rotation around x axis
        roll: rotation around y axis
        yaw: rotation around z axis
    '''
    def __init__(self, transformation: Transformations, base_value: list,
                 type_='Rotation', **kwargs):
        super().__init__(
            transformation=transformation, base_value=base_value,
            type_=type_, kwargs=kwargs
        )

    @property
    def rotation(self) -> list:
        return self.transform_base

    @rotation.setter
    def rotation(self, val: list):
        self.transform_base = val

    @property
    def pitch(self) -> float:
        return self.x

    @pitch.setter
    def pitch(self, value: float):
        self.x = value

    @property
    def roll(self) -> float:
        return self.y

    @roll.setter
    def roll(self, value: float):
        self.y = value

    @property
    def yaw(self) -> float:
        return self.z

    @yaw.setter
    def yaw(self, value: float):
        self.z = value


class Scale(TransformBase):
    def __init__(self, transformation: Transformations, base_value: list,
                 type_='Scale'):
        super().__init__(
            transformation=transformation, base_value=base_value,
            type_=type_
        )

    @property
    def scale(self) -> list:
        return self.transform_base

    @scale.setter
    def scale(self, val: list):
        self.transform_base = val
