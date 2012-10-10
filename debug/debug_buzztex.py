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

class Bar:
    def __init__(self, sze):
        self.i = int(np.random.uniform(0,sze))
        self.j = int(np.random.uniform(0,sze))
        self.k1 = int(np.random.uniform(0,sze/3))
        self.k2 = int(np.random.uniform(0,sze/3))
        self.w1 = int(np.random.uniform(1,10))
        self.w2 = int(np.random.uniform(1,10))
        self.value = np.random.uniform(0,1)


def aVolume(N=5, size=64):
    """ aVolume(N=5, size=64)
    
    Creates a volume (3D image) with random bars. 
    The returned numpy array has values between 0 and 1.
    Intended for quick illustration and test purposes.
    
    Parameters
    ----------
    N : int
        The number of bars for each dimension.
    size : int
        The size of the volume (for each dimension).
    
    """
    
    # Create volume
    vol = np.zeros((size,size,size), dtype=np.float32)

    # Make bars
    for iter in range(N):
        # x
        b = Bar(size)
        vol[ b.i-b.w1:b.i+b.w1, b.j-b.w2:b.j+b.w2, b.k1:-b.k2 ] += b.value
        # y
        b = Bar(size)
        vol[ b.i-b.w1:b.i+b.w1, b.k1:-b.k2, b.j-b.w2:b.j+b.w2 ] += b.value
        # z
        b = Bar(size)
        vol[ b.k1:-b.k2, b.i-b.w1:b.i+b.w1, b.j-b.w2:b.j+b.w2 ] += b.value

    # Clip and return
    vol[vol>1.0] = 1.0    
    return vol


def update(dt):
    #global zzz 
    #zzz -= 0.1
    #print zzz
    pass
pyglet.clock.schedule(update)


def make_red_bible_image(szx, szy, szz, w):

    image = np.zeros((szx, szy, szz) + (3,), np.ubyte)
    for s in range(szx):
        for t in range(szy):
            for r in range(szz):
                image[r, t, s, 0] = np.ubyte(255)
                image[r, t, s, 1] = 0#np.ubyte(t * 17)
                image[r, t, s, 2] = 0#np.ubyte(r * 17)
    hr=szz/2
    ht=szy/2
    hs=szx/2
    #image[hr - w : hr + w, ht - w : ht + w, hs - w : hs + w] = (0, 0, 255)
    image[hr, ht, hs] = (0, 0, 255)
    return image


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
    #"""
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
    szx = 16#128#30
    szy = 16#64#20
    szz = 16#4
    #data = (255*np.random.rand(sz, sz, sz, 3)).astype(np.ubyte)
    #data[:] = 255
    #data = (np.zeros((szx, szy, szz)+(3,))).astype(np.ubyte)
    #data[:, :, :] = (0, 0, 255)
    data = make_red_bible_image(szx, szy, szz, szz/16)
    #data[szx - w : szx + w, szy - w : szy + w] = (100, 0, 0)
    print data.shape
    print data.dtype
    print data.min(), data.max()
    """
	
    #volume = data
    tex = Texture3D('Buzz', volume, affine)
    w, h, d = volume.shape[:-1]
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
