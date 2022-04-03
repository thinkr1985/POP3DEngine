from PyQt6 import QtGui


class GLSurfaceFormat(QtGui.QSurfaceFormat):
    def __init__(self):
        super().__init__()
        self.setRenderableType(QtGui.QSurfaceFormat.renderableType(self).OpenGL)
        self.setSamples(4)
        self.setDepthBufferSize(24)
        self.setSwapInterval(0)  # Turning vsync off.
        self.setProfile(
            QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.setSwapBehavior(
            QtGui.QSurfaceFormat.SwapBehavior.TripleBuffer)

        # defining color-space
        self.color_space = QtGui.QColorSpace(
            QtGui.QColorSpace.NamedColorSpace.SRgbLinear)
