# Need to start with ipython --gui qt

from fos import *

w = Window()

w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )

w.add_actor_to_region( "Main", TriangleActor() )
w.add_actor_to_region( "Main", Axes() )

w.show()