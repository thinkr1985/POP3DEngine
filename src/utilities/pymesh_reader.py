import os
from utilities import utils
from logger import get_logger
from entity import MeshEntity
LOGGER = get_logger(__file__)


@utils.timeit
def import_pymesh(filepath: str, object_name: str = None, scene=None) -> list:
    if not os.path.exists(filepath):
        LOGGER.error(
            f'Failed to import pymesh, file {filepath} does not exists!'
        )
        return
    LOGGER.info(f'Importing pymesh from file {filepath}')

    file_data = utils.read_pymesh_file(
        pymesh_file_path=filepath, object_name=object_name)

    if not file_data:
        return
    entities = list()
    for num, entity_data in enumerate(file_data):
        entity = MeshEntity(
            buffers=entity_data.get('buffers'),
            entity_name=entity_data.get('entity_name'),
            entity_type=entity_data.get('entity_type'),
            user_attributes=entity_data.get('user_attributes'),
            source_file=entity_data.get('source_file'),
            scene=scene,
            shader=scene.default_shader)

        entities.append(entity)

    return entities
