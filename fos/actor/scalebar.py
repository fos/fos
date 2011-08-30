from .base import *

class ScaleBar(object):

    def __init__(self, name, startlocation, endlocation, unit ):
        """ ScaleBar actor with text
        """
        pass
        # TODO: needs
        # - start & endpoint of scale bar
        # - color
        # - text (aligned with up-direction vector)
        # - type; double-arrow, bar, ...
        # - could compute euclidian distance and display value with Region unit
        #   needs to consider perspective transformation to be accurate, maybe orthogonal perspective
        #   would require a reference to the region it belongs to
        #   would exist along the three axes