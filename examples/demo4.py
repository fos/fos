from fos import *

gp = GlumpyImage()

w = Window()
w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )
w.add_actor_to_region( "Main", gp )
w.show()