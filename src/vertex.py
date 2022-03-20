from logger import get_logger


LOGGER = get_logger(__file__)


class VertexSet:
    def __init__(self, buffers: dict,
                 entity, **kwargs):
        self.vertex_buffer_list = buffers.get('vertex_buffer')
        self.index_buffer_list = buffers.get('index_buffer')
        self.entity = entity

        self.init_vertex_entity()

    def init_vertex_entity(self):
        self.entity.scene.renderer.add_triangle_buffer(
            self.entity, self.index_buffer_list, self.vertex_buffer_list)
