#!/usr/bin/env python

import pyglet
pyglet.options['debug_gl'] = True
pyglet.options['debug_gl_trace'] = False
pyglet.options['debug_gl_trace_args'] = False
pyglet.options['debug_lib'] = False
pyglet.options['debug_media'] = False
pyglet.options['debug_trace'] = False
pyglet.options['debug_trace_args'] = False
#pyglet.options['debug_trace_depth'] = 1
pyglet.options['debug_font'] = False
pyglet.options['debug_x11'] = False
pyglet.options['debug_trace'] = False
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
    glTranslatef(0, 0, -280.)
    bz.set_state()
    bz.draw()
    bz.unset_state()

import numpy as np
#import nibabel as nib
from fos.actor.buzztex import BuzzTex
"""
fname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/T1_flirt_out.nii.gz'
img=nib.load(fname)
data = img.get_data()
affine = img.get_affine()
"""
affine = None
data = (255*np.random.rand(256, 256, 256)).astype(np.uint8)
#data[]
#data[:] = 155
#data[]
w = 30
#data[128-w:128+w, 128-w:128+w, 128-w:128+w] = 100
data[:128, :128, :128] = 10

print data.flags
print data.dtype
#1/0
data=np.asfortranarray(data)
bz=BuzzTex('Buzz', data, affine)

pyglet.app.run()
