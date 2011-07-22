
import sys
import math
from PySide import QtCore, QtGui, QtOpenGL

try:
    import pyglet.gl as GL
#    from OpenGL import GL
    
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class World(object):

    def __init__(self):

        self.actors = []
        self.camera = None

    def add_actor(self, actor):
        if not actor in self.actors:
            self.actors.append( actor )

    def remove_actor(self, actor):
        if actor in self.actors:
            self.actors.remove( actor )

    def set_camera(self, camera):
        self.camera = camera

    def draw_all(self):
        """ Draw all actors
        """
        for actor in self.actors:
            actor.draw()

class TriangleActor(object):
    def __init__(self):
        pass

    def draw(self):

        GL.glBegin(GL.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)

        GL.glEnd()

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):

        GL.glVertex3d(x1, y1, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x3, y3, -0.05)
        GL.glVertex3d(x4, y4, -0.05)

        GL.glVertex3d(x4, y4, +0.05)
        GL.glVertex3d(x3, y3, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x1, y1, +0.05)

    

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.world = World()

        self.add_actor( TriangleActor() )

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

        self.object = 0
        self.lastPos = QtCore.QPoint()
        self.bgcolor = QtGui.QColor.fromRgb(0, 0, 0)

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

        self.parent = parent


    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def initializeGL(self):
        self.qglClearColor(self.bgcolor)
        #self.object = self.makeObject()
        GL.glShadeModel(GL.GL_FLAT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(0.0, 0.0, -10.0)
        # draw world of parent window
        self.parent.world.draw_all()
    
    def resizeGL(self, width, height):
        side = min(width, height)
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    # EVENTHANDLING

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            print("Left button pressed")

        elif event.buttons() & QtCore.Qt.RightButton:
            print("Right button pressed")

        self.lastPos = QtCore.QPoint(event.pos())
