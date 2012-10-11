import numpy as np
from pyglet.gl import *
from .base import Actor
from ..vsml import vsml
from fos.external.freetype import *

from fos.data import get_font

class Text3D(Actor):

    def __init__(self, name, location, text, width, height, targetpoint = None, linewidth = 3.0, \
                 fontcolor = (1,1,1),  pointercolor = (1,1,1)):
        """ A Text3D actor
        """
        super(Text3D, self).__init__(name)
        self.vertices = location
        self.width = width
        self.height = height
        self.text = text
        self.targetpoint = targetpoint
        self.linewidth = linewidth
        self.fontcolor = fontcolor
        self.pointercolor = pointercolor

        # create freetype bitmap
        dataAlpha = self.make_bitmap(self.text)
        self.data = np.ones( (dataAlpha.shape[0], dataAlpha.shape[1], 4), dtype = np.ubyte)
        self.data[:,:,0] *= int(255 * self.fontcolor[0])
        self.data[:,:,1] *= int(255 * self.fontcolor[1])
        self.data[:,:,2] *= int(255 * self.fontcolor[2])
        self.data[:,:,3] = dataAlpha

        # create 2d texture
        self.data_ptr = self.data.ctypes.data
        self.tex_ptr = GLuint(0)
        glGenTextures(1, self.tex_ptr)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.tex_ptr)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)      
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.data.shape[1], 
                        self.data.shape[0], 0, GL_RGBA, 
                        GL_UNSIGNED_BYTE, self.data_ptr)
        glBindTexture(GL_TEXTURE_2D, 0)

    def make_bitmap(self, text):
        face = Face(get_font( 'Vera' ))
        face.set_char_size( 96*64 ) #48*64 )
        slot = face.glyph
        # First pass to compute bbox
        width, height, baseline = 0, 0, 0
        previous = 0
        for i,c in enumerate(text):
            face.load_char(c)
            bitmap = slot.bitmap
            height = max(height,
                         bitmap.rows + max(0,-(slot.bitmap_top-bitmap.rows)))
            baseline = max(baseline, max(0,-(slot.bitmap_top-bitmap.rows)))
            kerning = face.get_kerning(previous, c)
            width += (slot.advance.x >> 6) + (kerning.x >> 6)
            previous = c

        Z = np.zeros((height,width), dtype=np.ubyte)

        # Second pass for actual rendering
        x, y = 0, 0
        previous = 0
        for c in text:
            face.load_char(c)
            bitmap = slot.bitmap
            top = slot.bitmap_top
            left = slot.bitmap_left
            w,h = bitmap.width, bitmap.rows
            y = height-baseline-top
            kerning = face.get_kerning(previous, c)
            x += (kerning.x >> 6)
            Z[y:y+h,x:x+w] |= np.array(bitmap.buffer).reshape(h,w)
            x += (slot.advance.x >> 6) # for the last one, use bitmap.width
            previous = c

        return Z

    def draw(self):

        glEnable( GL_BLEND )
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)

        glBindTexture (GL_TEXTURE_2D, self.tex_ptr)

        if hasattr( vsml, 'camera'):
            # follow with the camera
            ri = vsml.camera.get_right()
            up = vsml.camera.get_yup()
            lb = (self.vertices[0,0], self.vertices[0,1], self.vertices[0,2])
            rb = (self.vertices[0,0]+self.width*ri[0],
                  self.vertices[0,1]+self.width*ri[1],
                  self.vertices[0,2]+self.width*ri[2])
            rt = (self.vertices[0,0]+self.width*ri[0]+self.height*up[0],
                  self.vertices[0,1]+self.width*ri[1]+self.height*up[1],
                  self.vertices[0,2]+self.width*ri[2]+self.height*up[2])
            lt = (self.vertices[0,0]+self.height*up[0],
                  self.vertices[0,1]+self.height*up[1],
                  self.vertices[0,2]+self.height*up[2])
        else:
            lb = (self.vertices[0,0], self.vertices[0,1], self.vertices[0,2])
            rb = (self.vertices[0,0]+self.width, self.vertices[0,1], self.vertices[0,2])
            rt = (self.vertices[0,0]+self.width, self.vertices[0,1]+self.height, self.vertices[0,2])
            lt = (self.vertices[0,0], self.vertices[0,1]+self.height, self.vertices[0,2])

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(*lb)

        glTexCoord2f(1.0, 1.0)
        glVertex3f(*rb)

        glTexCoord2f(1.0, 0.0)
        glVertex3f(*rt)

        glTexCoord2f(0.0, 0.0)
        glVertex3f(*lt)

        glEnd()
        
        glDisable(GL_TEXTURE_2D)

        # draw line
        if not self.targetpoint is None:
            glLineWidth(self.linewidth)
            glBegin(GL_LINES)
            glColor3f(*self.pointercolor)
            glVertex3f (self.vertices[0,0], self.vertices[0,1], self.vertices[0,2])
            glVertex3f (self.targetpoint[0,0], self.targetpoint[0,1], self.targetpoint[0,2])
            glEnd()
