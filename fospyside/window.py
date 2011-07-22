from PySide import QtCore, QtGui, QtOpenGL

from vsml import vsml
from world import World
from actor import *

try:
    from pyglet.gl import *
except ImportError:
    print("Need pyglet for OpenGL rendering")


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.world = World()

        self.add_actor( TriangleActor() )
        self.add_actor( Axes() )

        self.glWidget = GLWidget( self )

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("fos - pyside"))


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def add_actor(self, actor):
        self.world.add_actor( actor )

    def remove_actor(self, actor):
        self.world.remove_actor( actor )

    def set_camera(self, camera):
        self.world.camera = camera


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.lastPos = QtCore.QPoint()
        self.bgcolor = QtGui.QColor.fromRgb(0, 0, 0)
        self.parent = parent

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def initializeGL(self):
        self.qglClearColor(self.bgcolor)
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.parent.world.draw_all()

    def resizeGL(self, width, height):
        #side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)
        if height == 0:
            height = 1
        ratio =  width * 1.0 / height
        glViewport(0, 0, width, height)
        vsml.loadIdentity(vsml.MatrixTypes.PROJECTION)
        vsml.perspective(60., ratio, .1, 8000)
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(vsml.get_projection())
        glMatrixMode(GL_MODELVIEW)

    # EVENTHANDLING

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            pass
        elif event.buttons() & QtCore.Qt.RightButton:
            self.parent.world.camera.translate(dx,0,0 )
            self.parent.world.camera.translate(0,-dy,0 )
            
        self.lastPos = QtCore.QPoint(event.pos())
        self.repaint()

    def wheelEvent(self, e):
        numSteps = e.delta() / 15
        self.parent.world.camera.translate(0,0, numSteps )
        self.repaint()
