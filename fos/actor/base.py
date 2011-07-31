
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


class DynamicActor(Actor):

    def __init__(self):
        """ Dynamic actor either implemented as a list
        of static actors, or with data arrays having a temporal dimension
        """

        # is the actor currently playing
        self.playing = False

        # the reference to the first time frame
        self.current_time_frame = 0

    def next(self):
        """ Next time step
        """
        pass

    def previous(self):
        """ Previous time step
        """
        pass

    def play(self):
        """ Start playing
        """
        pass

    def pause(self):
        """ Pause playing
        """
        pass

    def stop(self):
        """ Stop playing and reset to start
        """
        pass