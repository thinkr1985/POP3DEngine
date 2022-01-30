import numpy as np
from logger import get_logger

LOGGER = get_logger(__file__)


class Transformations:
    def __init__(self, entity, transformations: list = None, **kwargs):
        self._entity = entity
        self._transformations = transformations or [0, 0, 0, 0, 0, 0, 1, 1, 1]
        self._position = np.array(self._transformations[:3], dtype=np.float32)
        self._eulers = np.array(self._transformations[3:6], dtype=np.float32)

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
        return f'Transformations({self._entity.name}, {self._transformations}) at {hex(id(self))}'

    def __repr__(self):
        return f'Transformations({self._entity.name}, {self.transformations}) at {hex(id(self))}'

    def _init_transformations(self):
        pass

    @property
    def transformations(self) -> list:
        return self._transformations

    @transformations.setter
    def transformations(self, val: list):
        if isinstance(val, tuple):
            val = list(val)

        if not len(val) == 9:
            LOGGER.error(
                f'Failed to set transformations on entity {self._entity.name}')
            return
        if 0 in val[6:]:
            LOGGER.error(f'Failed to set transformations on entity {self._entity.name},'
                         f'scale component cannot be equal to zero!')
            return

        self._transformations = val

    @property
    def translation(self) -> list:
        return self._transformations[:3]

    @translation.setter
    def translation(self, val: list):
        if isinstance(val, tuple):
            val = list(val)

        if not len(val) == 3:
            LOGGER.error(f'Failed to set translation on entity {self._entity.name},'
                         f'input translation list element count should be 3')
            return
        self._transformations = [val, self.rotation, self.scale]

    @property
    def rotation(self) -> list:
        return self._transformations[3:6]

    @rotation.setter
    def rotation(self, val: list):
        if isinstance(val, tuple):
            val = list(val)

        if not len(val) == 3:
            LOGGER.error(f'Failed to set rotation on entity {self._entity.name},'
                         f'input rotation list element count should be 3')
            return
        self._transformations = [self.translation, val, self.scale]

    @property
    def scale(self) -> list:
        return self._transformations[6:]

    @scale.setter
    def scale(self, val: list):
        if isinstance(val, tuple):
            val = list(val)

        if not len(val) == 3:
            LOGGER.error(f'Failed to set scale on entity {self._entity.name},'
                         f'input scale list element count should be 3')
            return
        self._transformations = [self.translation, self.rotation, val]

    @property
    def translateX(self) -> float:
        return self.translation[0]

    @translateX.setter
    def translateX(self, val: float):
        if not val:
            val = 0
        self.translation = [val, self.translation[1], self.translation[2]]

    @property
    def translateY(self) -> float:
        return self.translation[1]

    @translateY.setter
    def translateY(self, val: float):
        self.translation = [self.translation[0], val, self.translation[2]]

    @property
    def translateZ(self) -> float:
        return self.translation[2]

    @translateZ.setter
    def translateZ(self, val: float):
        self.translation = [self.translation[0], self.translation[1], val]

    @property
    def rotateX(self) -> float:
        return self.rotation[0]

    @rotateX.setter
    def rotateX(self, val: float):
        self.rotation = [val, self.rotation[0], self.rotation[1]]

    @property
    def rotateY(self) -> float:
        return self.rotation[1]

    @rotateY.setter
    def rotateY(self, val: float):
        self.rotation = [self.rotation[0], val, self.rotation[1]]

    @property
    def rotateZ(self) -> float:
        return self.rotation[2]

    @rotateZ.setter
    def rotateZ(self, val: float):
        self.rotation = [self.rotation[0], self.rotation[1], val]

    @property
    def scaleX(self) -> float:
        return self.scale[0]

    @scaleX.setter
    def scaleX(self, val: float):
        self.scale = [val, self.scale[0], self.scale[1]]

    @property
    def scaleY(self) -> float:
        return self.scale[1]

    @scaleY.setter
    def scaleY(self, val):
        self.scale = [self.scale[0], val, self.scale[1]]

    @property
    def scaleZ(self) -> float:
        return self.scale[2]

    @scaleZ.setter
    def scaleZ(self, val: float):
        self.scale = [self.scale[0], self.scale[1], val]
