import sys
import numpy as np

import pylab
import fos.util as util

# 10 random points (x,y) in the plane
x,y =  np.array(np.random.standard_normal((2,10)))

tri = util.find_triangulation2d( x, y )

for t in tri:
 t_i = [t[0], t[1], t[2], t[0]]
 pylab.plot(x[t_i],y[t_i])

pylab.plot(x,y,'o')
pylab.show()

