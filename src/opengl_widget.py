import os
import time
from pygltflib import GLTF2, Scene
from OpenGL.raw.GL.NVX.gpu_memory_info import *
from PyQt6 import QtGui, QtWidgets, QtCore, QtOpenGLWidgets
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from OpenGL.GLU import *
from glfw import *
import psutil


from constants import ICONS_PATH, PS_PROCESS
from utilities import pymesh_reader
from scene import Scene
from heads_up_display import HeadsUpDisplay
from gl_config import GLSettings

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
        self.format = QtGui.QSurfaceFormat()
        self.gl_settings = GLSettings(gl_widget=self)

        # setting Format of the openGL context
        self.format.setRenderableType(QtGui.QSurfaceFormat.renderableType(self.format).OpenGL)
        self.format.setSamples(4)
        self.format.setDepthBufferSize(24)
        self.format.setSwapInterval(0)  # Turning vsync off.
        self.format.setProfile(QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.format.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.TripleBuffer)

        # defining color-space
        self.color_space = QtGui.QColorSpace(QtGui.QColorSpace.NamedColorSpace.SRgbLinear)
        self.format.setColorSpace(self.color_space)

        self.setFormat(self.format) # make sure to set format after you defined all the parameters of your format.
        QtGui.QSurfaceFormat.setDefaultFormat(self.format)
        self.makeCurrent()

        self.heads_up_display = HeadsUpDisplay(gl_widget=self)
        self._scene = None

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.viewport_color = [0.3, 0.3, 0.3, 1.0]
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
        self.prev_time = 0

        self.frames_counter = 1
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
        self._connect()

    def _connect(self):
        pass

    @staticmethod
    def get_gpu_usage():
        try:
            # print(glGetString(GL_VENDOR))
            if "NVIDIA" in glGetString(GL_VENDOR).decode('utf-8'):
                total_mem_kb = glGetIntegerv(GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX)
                free_mem_kb = glGetIntegerv(GL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX)
                return f'{round((free_mem_kb / total_mem_kb) * 100, 2)}%'
            else:
                LOGGER.error('Unable to fetch GPU usage')
                return 'N/A'
        except Exception as error_txt:
            LOGGER.error(error_txt)
            return 0

    def calculate_fps(self):
        current_time = glutGet(GLUT_ELAPSED_TIME)
        time_diff = current_time - self.prev_time
        cpu_usage = round(PS_PROCESS.cpu_percent(), 2)
        memory_used = round(PS_PROCESS.memory_percent(), 2)
        gpu_usage = self.get_gpu_usage()

        delta = time_diff
        if delta >= 1000:
            frame_rate = int(1000.0 * self.frames_counter / delta)
            self.heads_up_display.fps = frame_rate or 0.1
            self.prev_time = current_time
            self.frames_counter = -1
            if frame_rate ==0:
                frame_rate = 0.1
            frame_time = round(float(1000.0 / frame_rate), 2)
            self.heads_up_display.millisecond_per_frame = frame_time
            title_string = 'POP3D Viewer F.P.S.: {}'.format(round(frame_rate / frame_time, 2))
            title_string += f' ,CPU used: {cpu_usage}%'
            title_string += f' ,RAM used: {memory_used}%'
            title_string += f' ,GPU used: {gpu_usage}'
            self.setWindowTitle(title_string)

        self.frames_counter += 1

        self.heads_up_display.draw()

    def resizeGL(self, width: int, height: int) -> None:
        self._scene.active_camera.height = height
        self._scene.active_camera.width = width
        glViewport(0, 0, width, height)
        self.update()

    def paintGL(self) -> None:
        glClearColor(self.viewport_color[0], self.viewport_color[1],
                     self.viewport_color[2], self.viewport_color[3])

        glClear(
            GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT
            )

        self._scene.renderer.render()
        self.calculate_fps()

        self.update()
        glFlush()
        self.doneCurrent()

    def initializeGL(self) -> None:
        LOGGER.info('Initializing OpenGLWidget')
        self.gl_settings.set_glrendersettings()
        self.gl_settings.print_gl_info()
        self._scene = Scene(width=self.width(), height=self.height())

        glClearDepth(1.0)
        self.heads_up_display._init_headsup_display()
        self.initial_time = time.time()
        self.prev_time = glutGet(GLUT_ELAPSED_TIME)

        teapot = pymesh_reader.import_pymesh(r"E:\GitHub\POP3DEngine\src\pymesh_examples\deer.pymesh", scene=self._scene)
        self._scene.add_entity(teapot)

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
            if not self.grid_on:
                self.grid_on = True
            else:
                self.grid_on = False
        if event.key() == QtCore.Qt.Key.Key_4:
            self.gl_settings.set_property('wireframe_mode', True)

        if event.key() == QtCore.Qt.Key.Key_5:
            self.gl_settings.set_property('wireframe_mode', False)

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
