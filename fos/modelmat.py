from pyglet.gl import *
from pyglet.gl.gl import c_float, c_double, c_int, glGetFloatv, GL_MODELVIEW_MATRIX
#before it was pyglet.gl
import numpy as np

#import pyglet
#print pyglet.__file__
def vec(*args):
    return (GLfloat * len(args))(*args)

def get_model_matrix(array_type=c_float, glGetMethod=glGetFloatv):
    """
    Returns the current modelview matrix.
    """
    m = (array_type*16)()
    glGetMethod(GL_MODELVIEW_MATRIX, m)
#    print "model matrix", np.array(m)
    return m

def get_projection_matrix(array_type=c_float, glGetMethod=glGetFloatv):
    """
    Returns the current modelview matrix.
    """
    m = (array_type*16)()
    glGetMethod(GL_PROJECTION_MATRIX, m)
    return m

def get_viewport():
    """
    Returns the current viewport.
    """
    m = (c_int*4)()
    glGetIntegerv(GL_VIEWPORT, m)
    return m

def get_direction_vectors():
    m = get_model_matrix()
    return ((m[0], m[4], m[8]),
            (m[1], m[5], m[9]),
            (m[2], m[6], m[10]))

def get_view_direction_vectors():
    m = get_model_matrix()
    return ((m[0], m[1], m[2]),
            (m[4], m[5], m[6]),
            (m[8], m[9], m[10]))

def get_basis_vectors():
    return ((1,0,0), (0,1,0), (0,0,1))

def screen_to_model(x,y,z):
    m = get_model_matrix(c_double, glGetDoublev)
    p = get_projection_matrix(c_double, glGetDoublev)
    w = get_viewport()
    mx,my,mz = c_double(),c_double(),c_double()
    gluUnProject(x,y,z,m,p,w,mx,my,mz)
    return float(mx.value),float(my.value),float(mz.value)

def model_to_screen(x,y,z):
    m = get_model_matrix(c_double, glGetDoublev)
    p = get_projection_matrix(c_double, glGetDoublev)
    w = get_viewport()
    mx,my,mz = c_double(),c_double(),c_double()
    gluProject(x,y,z,m,p,w,mx,my,mz)
    return float(mx.value),float(my.value),float(mz.value)

def billboard_matrix():
    """
    Removes rotational components of
    current matrix so that primitives
    are always drawn facing the viewer.

    |1|0|0|x|
    |0|1|0|x|
    |0|0|1|x| (x means left unchanged)
    |x|x|x|x|
    """
    m = get_model_matrix()
    m[0] =1;m[1] =0;m[2] =0
    m[4] =0;m[5] =1;m[6] =0
    m[8] =0;m[9] =0;m[10]=1
    glLoadMatrixf(m)

