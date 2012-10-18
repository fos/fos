import sys
import numpy as np
from fos import *

w = Window()

mytransform = IdentityTransform()
mytransform.set_translation( x = 5 )
mytransform.set_scale( 1.5, 1, 1 )
mytransform.rotate( 45, 1.0, 0, 0 )

scene = Scene( scenename = "Main",
                 transform = mytransform,
                 extent_min = np.array( [-5.0, -5, -5] ),
                 extent_max = np.array( [5, 5, 5] )  )

scene.add_actor( Axes( name = "3 axes", linewidth = 5.0) )
w.add_scene ( scene )

mytransform = IdentityTransform()
mytransform.set_translation( x = -40 )

scene2 = Scene( scenename = "Main2",
                  transform = mytransform,
                  extent_min = np.array( [-5.0, -5, -5] ),
                  extent_max = np.array( [5, 5, 5] ) )

scene2.add_actor( Axes( name = "3 axes", linewidth = 2.0) )
w.add_scene( scene2 )



w.refocus_camera()
