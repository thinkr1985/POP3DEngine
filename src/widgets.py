from opengl_widget import _OpenGLWidget
from gl_surface import GLSurfaceFormat


class OpenGLViewer(_OpenGLWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass


class OpenGLSurfaceFormat(GLSurfaceFormat):
    def __init__(self):
        super().__init__()
