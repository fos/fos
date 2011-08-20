import numpy as np
from pyglet.gl import *
from .base import Actor

from fos.external.freetype import *

from fos.data import get_font

class Text3D(Actor):

    def __init__(self, name, location, normal, text):
        """ A Text3D actor
        """
        super(Text3D, self).__init__( name )

        self.vertices = location
        self.normal = normal
        self.text = text

        # create freetype bitmap
        print get_font( 'Vera' )
        #face = freetype.Face('Vera.ttf') # TODO: into ../data
        #face.set_char_size( 48*64 )
        #face.load_char('S')
        #bitmap = face.glyph.bitmap
        #print bitmap.buffer

        # create dummy data array for texture
        self.data = np.array( [ [10, 250],
                                [110,  10] ], dtype = np.ubyte )

        self.data = np.random.random_integers( 0, 255, (400, 400)).astype( np.ubyte )

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
        # target, level, internalformat, width, border, format, type, pixels
        #glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE32F_ARB, self.data.shape[1], self.data.shape[0], 0, \
        #             GL_LUMINANCE, GL_FLOAT, self.data_ptr)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.data.shape[1], self.data.shape[0], 0, \
                     GL_ALPHA, GL_UNSIGNED_BYTE, self.data_ptr)

        glBindTexture(GL_TEXTURE_2D, 0)


    def draw(self):

        glEnable( GL_BLEND )
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)

        glBindTexture (GL_TEXTURE_2D, self.tex_ptr)
        
        glBegin (GL_QUADS)
        glTexCoord2f (0.0, 0.0)
        glVertex3f (0.0, 0.0, 0.0)

        glTexCoord2f (1.0, 0.0)
        glVertex3f (10.0, 0.0, 0.0)

        glTexCoord2f (1.0, 1.0)
        glVertex3f (10.0, 10.0, 0.0)

        glTexCoord2f (0.0, 1.0)
        glVertex3f (0.0, 10.0, 0.0)

        glEnd ()
        
        glDisable(GL_TEXTURE_2D)
