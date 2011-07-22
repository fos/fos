# Need to start with ipython --gui qt

from fospyside import *
w = Window()

w.add_actor( TriangleActor() )
w.add_actor( Axes() )

w.show()