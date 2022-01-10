import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from widgets import OpenGLViewer


class Viewer(OpenGLViewer):

    def __int__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle('3D viewer')
        self.setGeometry(10, 10, 760, 540)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # for ent in self.entities:
        #     ent.destroy()
        super(Viewer, self).closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Viewer()
    win.show()
    sys.exit(app.exec())
