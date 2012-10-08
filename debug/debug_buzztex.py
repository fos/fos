#!/usr/bin/env python

import pyglet
debug = False
pyglet.options['debug_gl'] = debug
pyglet.options['debug_gl_trace'] = debug
pyglet.options['debug_gl_trace_args'] = debug
pyglet.options['debug_lib'] = debug
pyglet.options['debug_media'] = debug
pyglet.options['debug_trace'] = debug
pyglet.options['debug_trace_args'] = debug
pyglet.options['debug_trace_depth'] = 1
pyglet.options['debug_font'] = debug
pyglet.options['debug_x11'] = debug
pyglet.options['debug_trace'] = debug
from pyglet.gl import *


try:
    # Try and create a window with multisampling (antialiasing)
    config = Config(sample_buffers=1, samples=4, 
                    depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)
except pyglet.window.NoSuchConfigException:
    # Fall back to no multisampling for old hardware
    window = pyglet.window.Window(resizable=True)


@window.event
def on_resize(width, height):
    # Override the default on_resize handler to create a 3D projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

#global zzz 
#zzz = 0

def update(dt):
    #global zzz 
    #zzz -= 0.1
    #print zzz
    pass
pyglet.clock.schedule(update)


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -100.)#-280
    bz.set_state()
    bz.draw()
    bz.unset_state()

if __name__ == '__main__':
    
    import numpy as np
    import nibabel as nib
    from fos.actor.buzztex import BuzzTex
    """
    fname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/T1_flirt_out.nii.gz'
    img=nib.load(fname)
    data = img.get_data()
    affine = img.get_affine()
    affine = None

    volume = np.zeros(data.shape+(3,))
    volume[...,0] = data.copy()
    volume[...,1] = data.copy()
    volume[...,2] = data.copy()
    volume = volume.astype(np.ubyte)
    print volume.shape, volume.min(), volume.max()
    """
    affine=None
    szx = 128#30
    szy = 64#20
    szz = 16#4
    #data = (255*np.random.rand(sz, sz, sz, 3)).astype(np.ubyte)
    #data[:] = 255
    data = (np.zeros((szx, szy, szz)+(3,))).astype(np.ubyte)
    data[:, :, :] = (0, 0, 255)
    w = 8
    data[szx - w : szx + w, szy - w : szy + w] = (100, 0, 0)
    print data.shape
    print data.dtype
    print data.min(), data.max()
    volume = data
    #data=np.asfortranarray(data)
    bz=BuzzTex('Buzz', volume, affine, 8)
    pyglet.app.run()
