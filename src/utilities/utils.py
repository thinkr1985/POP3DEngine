import json
import time
from pprint import pprint

from logger import get_logger
LOGGER = get_logger(__file__)


def read_object(json_path):
    """This method reads the given json.
    Args:
        json_path (str): json file path in string format.

    Returns:
        dict: Returns json data in dictionary format.
    """
    LOGGER.info("Reading object : {}".format(json_path))
    with open(json_path, "r") as fp:
        data_dict = json.loads(fp.read())
        return data_dict


def write_object(package_path=None, data_dict=None):
    """This method writes the dictionary in given package path in json format.
    Args:
        package_path (str): json file path in string format.
        data_dict (dict): Dictionary to write in json file.

    Returns:
        bool: Returns True if json file written successfully!
    """
    with open(package_path, "w") as fp:
        json.dump(
            data_dict,
            fp,
            sort_keys=True,
            indent=4,
            separators=(",", ":"),
            ensure_ascii=True
        )
        LOGGER.info("object file written at {}".format(package_path))
        return True


def read_pymesh_file(pymesh_file_path: str, object_name: str = None) -> list:
    file_data = read_object(pymesh_file_path)
    type_ = file_data.get('type')
    entities = list()

    for mesh, mesh_data in file_data.get('objects').items():
        if object_name:
            if mesh != object_name:
                continue
        entity_dict = {
                        'entity_name': mesh,
                        'entity_type': type_,
                        'buffers': mesh_data['buffers'],
                        'user_attributes': mesh_data.get('user_attributes'),
                        'source_files': pymesh_file_path
                }
        entities.append(entity_dict)

    return entities


def timeit(f):
    def timekeeper(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        LOGGER.info('%r execution took: %2.4f sec' % (f.__name__, te-ts))
        return result

    return timekeeper