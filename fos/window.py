from PySide import QtCore, QtGui, QtOpenGL

from vsml import vsml
from world import World
from actor import *

try:
    from pyglet.gl import *
except ImportError:
    print("Need pyglet for OpenGL rendering")


class Window(QtGui.QWidget):
    def __init__(self, parent = None, caption = "fos - pyside", width = 640, height = 480, bgcolor = (0,0,0) ):
        """ Create a window
        Parameters
        ----------
        `caption` : str or unicode
            Initial caption (title) of the window.
        `width` : int
            Width of the window, in pixels.  Defaults to 640, or the
            screen width if `fullscreen` is True.
        `height` : int
            Height of the window, in pixels.  Defaults to 480, or the
            screen height if `fullscreen` is True.
        `bgcolor` : tuple
            Specify the background RGB color as 3-tuple with values
            between 0 and 1
        """
        QtGui.QWidget.__init__(self, parent)

        self.world = World()

        self.glWidget = GLWidget( parent = self, width = width, height = height, bgcolor = bgcolor )

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr(caption))


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def new_region(self, regionname, transform, resolution ):
        self.world.new_region( regionname, transform, resolution )

    def add_actor_to_region(self, regionname, actor):
        self.world.add_actor_to_region( regionname, actor )

    def remove_actor_from_region(self, regionname, actor):
        self.world.remove_actor_from_region( regionname, actor )

    def set_camera(self, camera):
        self.world.camera = camera

    def screenshot(self, filename):
        """ Store current OpenGL context as image
        """
        self.glWidget.grabFrameBuffer().save( filename )
        
    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Up:
            print("Up")
        elif key == QtCore.Qt.Key_Down:
            print("Down")
        elif key == QtCore.Qt.Key_Left:
            print("Left")
        elif key == QtCore.Qt.Key_Right:
            self.world.camera.reset()
        elif key == QtCore.Qt.Key_R:
            self.world.camera.reset()
            self.glWidget.repaint()
        elif key == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super(Window, self).keyPressEvent( event )


# if event.key() == Qt.Key_O and ( event.modifiers() & Qt.ControlModifier ): # & == bit wise "and"!

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None, width = None, height = None, bgcolor = None):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.lastPos = QtCore.QPoint()
        self.bgcolor = QtGui.QColor.fromRgb(bgcolor[0], bgcolor[1], bgcolor[2])
        self.parent = parent
        self.width = width
        self.height = height

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.width, self.height)

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
            # should rotate
            if dx != 0:
                # rotate around yup
                if dx > 0:
                    angle = -0.01
                else:
                    angle = 0.01
                self.parent.world.camera.rotate_around_focal( angle, "yup" )

            if dy != 0:
                # rotate around right
                if dy > 0:
                    angle = -0.01
                else:
                    angle = 0.01
                self.parent.world.camera.rotate_around_focal( angle, "right" )

        elif event.buttons() & QtCore.Qt.RightButton:
            # should pan

            if dx > 0:
                pandx = -1.0
            elif dx < 0:
                pandx = 1.0
            else:
                pandx = 0.0


            if dy > 0:
                pandy = 0.5
            elif dy < 0:
                pandy = -0.5
            else:
                pandy = 0.0

            self.parent.world.camera.pan( pandx, pandy )
            
        self.lastPos = QtCore.QPoint(event.pos())

        self.repaint()

    def wheelEvent(self, e):
        numSteps = e.delta() / 15 / 8
        print "numsteps", numSteps
        shift = False
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            print "ctrl modifier"

        if (e.modifiers() & QtCore.Qt.ShiftModifier):
            shift = True

        if shift:
            self.parent.world.camera.move_forward_all( numSteps )
        else:
            self.parent.world.camera.move_forward( numSteps )

        self.repaint()

