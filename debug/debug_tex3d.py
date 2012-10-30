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


def update(dt):
    pass
pyglet.clock.schedule(update)


@window.event
def on_draw():
    global tex
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -150.)#-280
    tex.set_state()
    tex.draw()
    tex.unset_state()


if __name__ == '__main__':
    
    import numpy as np
    import nibabel as nib
    from fos.actor.tex3d import Texture3D

    volume = 255*np.ones((128, 128, 128), dtype=np.ubyte)
    print volume.shape, volume.min(), volume.max()
    affine = None
    
    tex = Texture3D('Buzz', volume, affine, type=GL_RGB)
    w, h, d = volume.shape[:3]
    depindex = 100
    dep = (0.5 + depindex) / np.float(d)
    texcoords = np.array([  [dep, 0, 0], 
                            [dep, 0, 1], 
                            [dep, 1, 1],
                            [dep, 1, 0] ])
    vertcoords = np.array( [ [-w/2., -h/2., 0.],
                            [-w/2., h/2., 0.],
                            [w/2., h/2., 0.],
                            [w/2, -h/2., 0] ])
 
    tex.update_quad(texcoords, vertcoords)
    pyglet.app.run()
