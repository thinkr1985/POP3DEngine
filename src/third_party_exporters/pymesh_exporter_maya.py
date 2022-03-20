import platform
import getpass
import json
import pymel.core as pm
import datetime

object_dict = dict()
user = getpass.getuser()
system = platform.system()


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


def get_all_vertices_data(node):
    transform_node = node.getTransform()
    vertices_data = dict()
    for vertex_num in node.getVertices()[1]:
        vertex = pm.PyNode("{}.vtx[{}]".format(transform_node, vertex_num))
        vertices_data.update({vertex_num: get_vertex_data(vertex)})
    return vertices_data


def get_vertex_data(mesh_vertex):
    vertex_data_list = list()
    [vertex_data_list.append(round(float(x), 4)) for x in
     mesh_vertex.getPosition(space='world')]

    [vertex_data_list.append(round(float(x), 4)) for x in
     mesh_vertex.getNormal(space='world')]

    if mesh_vertex.hasColor():
        [vertex_data_list.append(round(float(x), 3)) for x in
         mesh_vertex.getColor()]
    else:
        vertex_data_list.extend([0.5, 0.5, 0.5, 1.0])

    [vertex_data_list.append(round(x, 4)) for x in mesh_vertex.getUV()]

    return vertex_data_list


def get_object_data(node):
    object_data = dict()
    node_transform = node.getTransform()
    all_vertex_data = get_all_vertices_data(node)
    face_count = node.numFaces()

    vertex_buffer = list()
    index_buffer = list()

    processed_vertices = list()

    for face_num in range(face_count):

        face = pm.PyNode('{}.f[{}]'.format(node_transform, face_num))
        face_vertices = face.getVertices()

        if len(face_vertices) == 3:
            for vert in face_vertices:

                if vert not in processed_vertices:
                    processed_vertices.append(vert)
                    index_buffer.append(vert)
                else:
                    index_buffer.append(vert)

        elif len(face_vertices) == 4:
            triangle_one = face_vertices[:3]
            triangle_two = face_vertices[2:]
            triangle_two.append(face_vertices[0])

            for vert in triangle_one:
                if vert not in processed_vertices:
                    processed_vertices.append(vert)
                    index_buffer.append(vert)
                else:
                    index_buffer.append(vert)
            for vert in triangle_two:
                if vert not in processed_vertices:
                    processed_vertices.append(vert)
                    index_buffer.append(vert)
                else:

                    index_buffer.append(vert)
        else:
            raise NotImplementedError(
                'MeshFace not compatible to export {}'.format(face))

    for key in sorted(all_vertex_data.keys()):
        vertex_buffer.extend(all_vertex_data[key])
    object_data = {
        node.getParent().name():
            {
                'buffers':
                    {
                        'vertex_buffer': vertex_buffer,
                        'index_buffer': index_buffer
                    },
                'user_attributes': get_user_attributes(node)
            }
    }

    return object_data


if __name__ == '__main__':

    nodes = pm.ls(type='mesh')

    obj_data = dict()
    for mesh in nodes:
        data = get_object_data(mesh)
        obj_data.update(data)

    data_ = {
        'objects': obj_data,
        'format': 1.0,
        'type': 'static',
        'exported_date': str(datetime.datetime.now()),
        'platform': system,
        'owner': user,
        'application': "Maya.{}".format(pm.about(apiVersion=True)),

    }

    export_path = "/user_data/pymeshes/plane.pymesh"
    write_json(package_path=export_path, data_dict=data_)