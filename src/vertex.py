from logger import get_logger


LOGGER = get_logger(__file__)


class VertexSet:
    def __init__(self, vertices_per_face: int, buffers: dict,
                 entity, **kwargs):
        self.vertices_per_face = vertices_per_face
        self.vertex_buffer_list = buffers.get('vertex_buffer')
        self.index_buffer_list = buffers.get('index_buffer')
        self.entity = entity

        self.init_vertex_entity()

    def init_vertex_entity(self):
        if self.vertices_per_face == 3:
            self.entity.scene.renderer.add_triangle_buffer(
                self.entity, self.index_buffer_list, self.vertex_buffer_list)

        if self.vertices_per_face == 4:
            self.entity.scene.renderer.add_quad_buffer(
                self.entity, self.index_buffer_list, self.vertex_buffer_list)

        elif self.vertices_per_face > 4:
            self.entity.scene.renderer.add_ngon_buffer(
                self.entity, self.index_buffer_list, self.vertex_buffer_list)
