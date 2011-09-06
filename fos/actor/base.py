from PySide import QtCore

class Actor(object):

    def __init__(self, name):
        """ The base class for Actors
        """
        self.name = name

        # is this actor currently visible
        self.visible = True

        # is this actor currently selected
        self.selected = False

        # affine transformation of the actor
        # relative to the Region it is associated with
        self.transformation = None

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def get_extent_min(self):
        if not self.vertices is None:
            return self.vertices.min( axis = 0 )

    def get_extent_max(self):
        if not self.vertices is None:
            return self.vertices.max( axis = 0 )

    def pick(self, x, y):
        pass

class DynamicActor(Actor):

    def __init__(self, name):
        """ Dynamic actor either implemented as a list
        of static actors, or with data arrays having a temporal dimension
        """
        super(DynamicActor, self).__init__( name )

        # is the actor currently playing
        self.playing = False

        # the reference to the first time frame
        self.current_time_frame = 0

        # init timer
        self.timer = QtCore.QTimer( None )
        self.timer.setInterval( 40 )
        self.timer.timeout.connect( self.next )

    def updatePtr(self):
        """ Updates the pointers to the data arrays
        """
        pass

    def next(self):
        """ Next time step
        """
        if self.current_time_frame == self.max_time_frame:
            return
        self.current_time_frame += 1
        self.updatePtr()

    def previous(self):
        """ Previous time step
        """
        if self.current_time_frame == 0:
            return
        self.current_time_frame -= 1
        self.updatePtr()

    def play(self):
        """ Start playing
        """
        self.timer.start()

    def pause(self):
        """ Pause playing
        """
        self.timer.stop()

    def stop(self):
        """ Stop playing and reset to start
        """
        self.current_time_frame = 0
        self.updatePtr()