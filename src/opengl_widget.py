import time

from PyQt6 import QtGui, QtWidgets, QtCore, QtOpenGLWidgets
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from glfw import *
import numpy as np
import primitives_
from constants import ICONS_PATH
from utilities import pymesh_reader
from scene import Scene

from logger import get_logger

LOGGER = get_logger(__file__)


class _OpenGLViewer(QtWidgets.QWidget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.opengl_widget = _OpenGLWidget()
        self.layout.addWidget(self.opengl_widget)


class _OpenGLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # setting Format of the openGL context
        self.format = QtGui.QSurfaceFormat()
        self.setFormat(self.format)
        self.format.setVersion(3, 3)
        self.format.setSamples(4)
        self.format.setProfile(QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        self._scene = None

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.viewport_color = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.grid = True
        self.setMinimumSize(QtCore.QSize(120, 120))

        self.rotate_pixmap = QtGui.QPixmap(os.path.join(ICONS_PATH, 'rotate.png'))
        self.move_pixmap = QtGui.QPixmap(os.path.join(ICONS_PATH, 'move.png'))
        self.zoom_in_pixmap = QtGui.QPixmap(os.path.join(ICONS_PATH, 'zoom_in.png'))
        self.zoom_out_pixmap = QtGui.QPixmap(
            os.path.join(ICONS_PATH, 'zoom_out.png'))
        self.zoom_in_cursor = QtGui.QCursor(self.zoom_in_pixmap)
        self.zoom_out_cursor = QtGui.QCursor(self.zoom_out_pixmap)
        self.move_cursor = QtGui.QCursor(self.move_pixmap)
        self.rotate_cursor = QtGui.QCursor(self.rotate_pixmap)

        self.initial_time = time.time()

        self.nframes = 1
        self.mouse_drag = False
        self.mouse_pos = QtCore.QPoint(0, 0)
        self.pan_mode = False
        self.zoom_mode = False
        self.rotate_mode = False

        self.camera_focal_length = 35.0
        self.camera_aspect_ratio = 1.00
        self.camera_near_plane_distance = 1.0
        self.camera_far_plane_distance = 50.0

        self.grid_on = True
        self._font = GLUT_BITMAP_HELVETICA_12
        self._connect()

    def _connect(self):
        pass

    @staticmethod
    def normalized_angle(angle):
        while angle > np.pi:
            angle -= 2.0 * np.pi

        while angle < -np.pi:
            angle += 2.0 * np.pi

        return angle

    def draw_heads_up_info(self):
        self.draw_fps()
        self.draw_opengl_version()

    def draw_opengl_version(self):
        primitives_.glut_print(2.0, 1.4,
                               self._font,
                              f"openGL Ver : {glGetString(GL_VERSION).decode('utf-8')}",
                               [1.0, 1.0, 1.0]
                               )

    def draw_fps(self):
        elapsed_time = time.time() - self.initial_time
        self.nframes += 1
        fps = round(self.nframes / elapsed_time, 2)
        primitives_.glut_print(
            2.0, 1.5, self._font,
            f"FPS : {fps}",
            [1.0, 1.0, 1.0])

    def resizeGL(self, width: int, height: int) -> None:
        self._scene.active_camera.height = height
        self._scene.active_camera.width = width

    def paintGL(self) -> None:
        glClearColor(0.3, 0.3, 0.3, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.nframes += 1
        self._scene.renderer.render()
        self.update()
        glFlush()

    def initializeGL(self) -> None:
        LOGGER.info('Initializing OpenGL')

        glutInit()
        glutInitDisplayMode(GLUT_RGBA |
                            GLUT_DOUBLE |
                            GLUT_MULTISAMPLE |
                            GLUT_ALPHA |
                            GLUT_DEPTH |
                            GLUT_CORE_PROFILE)

        self._scene = Scene(width=self.width(), height=self.height())

        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)

        glEnable(GL_LIGHTING)
        glMatrixMode(GL_MODELVIEW)
        self.initial_time = time.time()

        teapot = pymesh_reader.import_pymesh("E:\\projects\\3d_viewer\\src\\pymesh_examples\\teapot_high.pymesh", scene=self._scene)
        self._scene.add_entity(teapot)

        # teapot2 = pymesh_reader.import_pymesh("E:\\projects\\3d_viewer\\src\\pymesh_examples\\multiple_planes.pymesh", scene=self._scene)
        # self._scene.add_entity(teapot2)
        # glfw.poll_events()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Up or event.key() == QtCore.Qt.Key.Key_W:
            self.setCursor(self.zoom_in_cursor)
            self._scene.render_camera.translateZ = self._scene.render_camera.translateZ + 0.1
        if event.key() == QtCore.Qt.Key.Key_Down or event.key() == QtCore.Qt.Key.Key_S:
            self.setCursor(self.zoom_in_cursor)
            self._scene.render_camera.translateZ = self._scene.render_camera.translateZ - 0.1
        if event.key() == QtCore.Qt.Key.Key_Left or event.key() == QtCore.Qt.Key.Key_A:
            self.setCursor(self.move_cursor)
            self._scene.render_camera.translateX = self._scene.render_camera.translateX + 0.1
        if event.key() == QtCore.Qt.Key.Key_Right or event.key() == QtCore.Qt.Key.Key_D:
            self.setCursor(self.move_cursor)
            self._scene.render_camera.translateX = self._scene.render_camera.translateX - 0.1
        if event.key() == QtCore.Qt.Key.Key_R:
            self._scene.render_camera.reset_transformations()
        if event.key() == QtCore.Qt.Key.Key_G:
            if self.grid_on == False:
                self.grid_on = True
            else:
                self.grid_on = False
        if event.key() == QtCore.Qt.Key.Key_4:
            self._scene.renderer.set_property('wireframe_mode', True)
        if event.key() == QtCore.Qt.Key.Key_5:
            self._scene.renderer.set_property('wireframe_mode', False)

        super(_OpenGLWidget, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super(_OpenGLWidget, self).keyReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        self.setCursor(self.zoom_in_cursor)
        if event.angleDelta().y() > 0:
            self._scene.render_camera.translateZ = self._scene.render_camera.translateZ + 0.5
        if event.angleDelta().y() < 0:
            self._scene.render_camera.translateZ = self._scene.render_camera.translateZ - 0.5
        super(_OpenGLWidget, self).wheelEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        key_modifiers = QtWidgets.QApplication.keyboardModifiers()

        if event.button() == QtCore.Qt.MouseButton.MiddleButton and \
                (bool(key_modifiers == QtCore.Qt.KeyboardModifier.AltModifier)):
            self.mouse_drag = True
            self.pan_mode = True

        if event.button() == QtCore.Qt.MouseButton.RightButton and \
                (bool(key_modifiers == QtCore.Qt.KeyboardModifier.AltModifier)):
            self.mouse_drag = True
            self.zoom_mode = True

        if event.button() == QtCore.Qt.MouseButton.LeftButton and \
                (bool(key_modifiers == QtCore.Qt.KeyboardModifier.AltModifier)):
            self.mouse_drag = True
            self.rotate_mode = True

        self.mouse_pos = event.pos()
        super(_OpenGLWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mouse_drag and self.pan_mode:
            self.setCursor(self.move_cursor)
            if event.pos().x() > self.mouse_pos.x():
                self._scene.render_camera.translateX = self._scene.render_camera.translateX + 0.1
            elif event.pos().x() < self.mouse_pos.x():
                self._scene.render_camera.translateX = self._scene.render_camera.translateX - 0.1
            if event.pos().y() > self.mouse_pos.y():
                self._scene.render_camera.translateY = self._scene.render_camera.translateY - 0.1
            elif event.pos().y() < self.mouse_pos.y():
                self._scene.render_camera.translateY = self._scene.render_camera.translateY + 0.1

        if self.mouse_drag and self.zoom_mode:
            self.setCursor(self.zoom_in_cursor)
            if event.pos().x() > self.mouse_pos.x():
                self._scene.render_camera.translateZ = self._scene.render_camera.translateZ + 0.1
            elif event.pos().x() < self.mouse_pos.x():
                self._scene.render_camera.translateZ = self._scene.render_camera.translateZ - 0.1
            if event.pos().y() > self.mouse_pos.y():
                pass
            elif event.pos().y() < self.mouse_pos.y():
                pass

        if self.mouse_drag and self.rotate_mode:
            self.setCursor(self.rotate_cursor)
            if event.pos().x() > self.mouse_pos.x():
                self._scene.render_camera.yaw = self._scene.render_camera.yaw - 1.5
            elif event.pos().x() < self.mouse_pos.x():
                self._scene.render_camera.yaw = self._scene.render_camera.yaw + 1.5
            if event.pos().y() > self.mouse_pos.y():
                self._scene.render_camera.pitch = self._scene.render_camera.pitch - 1.5
            elif event.pos().y() < self.mouse_pos.y():
                self._scene.render_camera.pitch = self._scene.render_camera.pitch + 1.5

        self.mouse_pos = event.pos()
        super(_OpenGLWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_drag = False
        self.pan_mode = False
        self.zoom_mode = False
        self.rotate_mode = False
        self.mouse_pos = QtCore.QPoint(0, 0)
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super(_OpenGLWidget, self).mouseReleaseEvent(event)
