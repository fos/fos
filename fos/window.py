from PySide import QtCore, QtGui, QtOpenGL

from vsml import vsml
from world import *
from actor import *

try:
    from pyglet.gl import *
except ImportError:
    print("Need pyglet for OpenGL rendering")

class Window(QtGui.QWidget):
    def __init__(self, parent = None, caption = "fos - pyside", width = 640, height = 480,
                 bgcolor = (0,0,0), fullscreen = False, dynamic = False, enable_light = False ):
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
        # TODO: add PySide.QtOpenGL.QGLFormat to configure the OpenGL context
        QtGui.QWidget.__init__(self, parent)
        self.glWidget = GLWidget( parent = self, width = width, height = height,
                                  bgcolor = bgcolor, enable_light = enable_light )
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr(caption))

        self.spinCameraTimer = self.timerInit( interval = 30 )
        
        if dynamic:
            self.dynamicWindowTimer = self.timerInit( interval = 30 )
            self.dynamicWindowTimer.timeout.connect(self.glWidget.updateGL)
            self.dynamicWindowTimer.start()

        if fullscreen:
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.show()
            self.fullscreen = False

    def initSpincamera(self, angle = 0.007 ):
        self.spinCameraTimer.timeout.disconnect()
        
        def rotate_camera():
            self.glWidget.world.camera.rotate_around_focal( angle, "yup" )
            self.glWidget.updateGL()
            
        self.spinCameraTimer.timeout.connect(rotate_camera)

    def spinCameraToggle(self):

        if not self.spinCameraTimer.isActive():
            self.spinCameraTimer.start()
        else:
            self.spinCameraTimer.stop()


    def timerInit(self, interval = 30):
        timer = QtCore.QTimer(self)
        timer.setInterval( interval )
        return timer

    def test_actor(self):
        """ Dummy test function
        """
        region = Region( regionname = "Main",
                         extent_min = np.array( [-5.0, -5, -5] ),
                         extent_max = np.array( [5, 5, 5] ) )
        sphere = Sphere( "MySphere", radius = 2, iterations = 2 )
        region.add_actor( sphere )
        self.add_region (region )
        self.refocus_camera()
        self.glWidget.updateGL()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def add_region(self, region):
        self.glWidget.world.add_region( region )

    def set_camera(self, camera):
        self.glWidget.world.camera = camera

    def refocus_camera(self):
        self.glWidget.world.refocus_camera()

    def update_light_position(self, x, y, z):
        if not self.glWidget.world.light is None:
            self.glWidget.world.update_lightposition(x, y, z)

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
            self.glWidget.world.camera.reset()
        elif key == QtCore.Qt.Key_F:
            if self.fullscreen:
                self.showNormal()
            else:
                self.showFullScreen()
            self.fullscreen = not self.fullscreen
        elif key == QtCore.Qt.Key_N:
            self.glWidget.world.nextTimeFrame()
        elif key == QtCore.Qt.Key_B:
            self.glWidget.world.previousTimeFrame()
        elif key == QtCore.Qt.Key_R:
            self.glWidget.world.refocus_camera()
            self.glWidget.world.camera.update()
            self.glWidget.updateGL()
        elif key == QtCore.Qt.Key_S:
            if (event.modifiers() & QtCore.Qt.ShiftModifier):
                self.initSpincamera( angle = -0.01 )
                self.spinCameraToggle()
            else:
                self.initSpincamera( angle = 0.01 )
                self.spinCameraToggle()
            
        elif key == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super(Window, self).keyPressEvent( event )


# if event.key() == Qt.Key_O and ( event.modifiers() & Qt.ControlModifier ): # & == bit wise "and"!

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None, width = None, height = None, bgcolor = None, enable_light = False):
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.lastPos = QtCore.QPoint()
        self.bgcolor = QtGui.QColor.fromRgbF(bgcolor[0], bgcolor[1], bgcolor[2], 1.0)
        self.width = width
        self.height = height
        self.enable_light = enable_light
        self.world = World()

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.width, self.height)

    def initializeGL(self):
        self.qglClearColor(self.bgcolor)
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ZERO) #_MINUS_SRC_ALPHA)

        if self.enable_light:
            self.world.setup_light()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.world.draw_all()

    def resizeGL(self, width, height):
        #side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)
        if height == 0:
            height = 1
        vsml.setSize( width, height )
        self.width = width
        self.height = height
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

        if (event.modifiers() & QtCore.Qt.ControlModifier):
            x, y = event.x(), event.y()
            self.world.pick_all( x, self.height - y)

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            shift = True
        else:
            shift = False

        if (event.modifiers() & QtCore.Qt.ControlModifier):
            ctrl = True
        else:
            ctrl = False
            
        if event.buttons() & QtCore.Qt.LeftButton:

            if not ctrl:
                # should rotate
                if dx != 0:
                    # rotate around yup
                    if dx > 0:
                        angle = -0.01
                    else:
                        angle = 0.01

                    if shift:
                        angle *= 2

                    self.world.camera.rotate_around_focal( angle, "yup" )

                if dy != 0:
                    # rotate around right
                    if dy > 0:
                        angle = -0.01
                    else:
                        angle = 0.01

                    if shift:
                        angle *= 2

                    self.world.camera.rotate_around_focal( angle, "right" )

                self.updateGL()

            else:
                # with control, do many selects!
                x, y = event.x(), event.y()
                self.world.pick_all( x, self.height - y)

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

            self.world.camera.pan( pandx, pandy )
            self.updateGL()
            
        self.lastPos = QtCore.QPoint(event.pos())



    def wheelEvent(self, e):
        numSteps = e.delta() / 15 / 8
        #print "numsteps", numSteps
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            ctrl = True
        else:
            ctrl = False

        if (e.modifiers() & QtCore.Qt.ShiftModifier):
            shift = True
        else:
            shift = False

        if ctrl:
            if shift:
                self.world.camera.move_forward_all( numSteps * 10 )
            else:
                self.world.camera.move_forward_all( numSteps )
        else:
            if shift:
                self.world.camera.move_forward( numSteps * 10 )
            else:
                self.world.camera.move_forward( numSteps )

        self.updateGL()
