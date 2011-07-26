# Need to start with ipython --gui qt
# Shows a Shader

from fos import *
w = Window()
w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )
w.show()


def a():
    global w
    act = ShaderActor()
    w.add_actor_to_region( "Main", act )
    return act


