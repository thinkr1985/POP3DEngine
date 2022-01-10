import platform
import getpass
import json
import pymel.core as pm
import datetime
from multiprocessing.pool import Pool
from pprint import pprint

export_path = "/u/ncj/Desktop/multiple_planes.pymesh"
object_dict = dict()
user = getpass.getuser()
system = platform.system()

cached_vertices_data = dict()


def write_json(package_path=None, data_dict=None):
    with open(package_path, "w") as fp:
        json.dump(
            data_dict,
            fp,
            sort_keys=True,
            indent=3,
            separators=(",", ":"),
            ensure_ascii=True
        )
        print("json file written at {}".format(package_path))
        return True


def get_user_attributes(shape):
    user_attrs = shape.listAttr(ud=True)
    if not user_attrs:
        return
    attr_dict = dict()
    for attr in user_attrs:
        value = attr.get()
        if not isinstance(value, (int, float, str, bool)):
            value = str(value)
        attr_dict.update({attr.attrName(): value})

    return attr_dict


def get_vertex_data(mesh_vertex):
    vtx_id = int(mesh_vertex.split(".vtx[")[-1].split("]")[0])
    if vtx_id in cached_vertices_data:
        return cached_vertices_data.get(vtx_id)

    vertex_data_list = list()
    [vertex_data_list.append(round(float(x), 4)) for x in
     mesh_vertex.getPosition(space='world')]

    [vertex_data_list.append(round(float(x), 4)) for x in
     mesh_vertex.getNormal(space='world')]

    if mesh_vertex.hasColor():
        [vertex_data_list.append(round(float(x), 3)) for x in mesh_vertex.getColor()]
    else:
        vertex_data_list.extend([0.5, 0.5, 0.5, 1.0])

    [vertex_data_list.append(round(x, 4)) for x in mesh_vertex.getUV()]
    cached_vertices_data.update({vtx_id: vertex_data_list})

    return vertex_data_list


def get_face_sets(shape):
    face_buffer_data = dict()

    for num in range(shape.numFaces()):
        transform_name = shape.getParent()
        face_obj = pm.PyNode("{}.f[{}]".format(transform_name, num))
        face_vertices = face_obj.getVertices()
        vtx_num = len(face_vertices)
        vertex_buffer = list()

        if vtx_num not in face_buffer_data:
            face_buffer_data.update({vtx_num: [face_obj]})
        else:
            new_faces = face_buffer_data[vtx_num]
            new_faces.append(face_obj)
            face_buffer_data[vtx_num] = new_faces

    vertex_buffer_data = list()

    for vtx_num, faces in face_buffer_data.items():
        face_dict = dict()

        processed_ids = dict()

        vertex_buffer = list()
        index_buffer = list()

        id_counter = 0

        for face in faces:
            vertex_ids = face.getVertices()
            for id_ in vertex_ids:

                if id_ in processed_ids:
                    index_buffer.append(processed_ids.get(id_))
                else:
                    index_buffer.append(id_counter)
                    vert_data = get_vertex_data(
                        pm.PyNode("{}.vtx[{}]".format(
                            face._node.getParent().name(), id_))
                    )
                    vertex_buffer.extend(vert_data)
                    processed_ids.update({id_: id_counter})

                    id_counter += 1

        face_dict.update({vtx_num: {'index_buffer': index_buffer,
                                    'vertex_buffer': vertex_buffer}})
        vertex_buffer_data.append(face_dict)
    return vertex_buffer_data


def get_shape_data(mesh):
    print('Generating data for {}'.format(mesh))
    face_data = get_face_sets(mesh)
    user_attributes = get_user_attributes(mesh)

    data = {mesh.getParent().name(): {'face_sets': face_data,
                                        'user_attributes': user_attributes}}
    return data


if __name__ == "__main__":
    nodes = pm.ls(type='mesh')

    obj_data = dict()
    for mesh in nodes:
        data = get_shape_data(mesh)
        obj_data.update(data)
        cached_vertices_data = dict()

    data_ = {
        'objects': obj_data,
        'format': 1.0,
        'type': 'static',
        'exported_date': str(datetime.datetime.now()),
        'platform': system,
        'owner': user,
        'application': "Maya.{}".format(pm.about(apiVersion=True)),

    }

    write_json(package_path=export_path, data_dict=data_)
