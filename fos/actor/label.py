#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Subpixel rendering AND positioning using OpenGL and shaders.

'''
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from fos.external.freetype.texture_font import TextureFont, TextureAtlas

from shader import Shader

import numpy as np
from pyglet.gl import *
from .base import Actor
from ..vsml import vsml
from fos.external.freetype import *
from fos.data import get_font
from fos.shader.lib import *

from PySide.QtGui import QMatrix4x4

class Label(Actor):

    def __init__(self, name, text, color=(1.0, 1.0, 1.0, 0.0),  x=0, y=0,
                 width=None, height=None, anchor_x='left', anchor_y='baseline'):

        super(Label, self).__init__( name )

        self.atlas = TextureAtlas(512,512,3)
        font = TextureFont(self.atlas, get_font('Vera'), 9)
        self.atlas.upload()
        
        self.text = text
        self.vertices = np.zeros((len(text)*4,3), dtype=np.float32)
        self.indices  = np.zeros((len(text)*6, ), dtype=np.uint)
        self.colors   = np.zeros((len(text)*4,4), dtype=np.float32)
        self.texcoords= np.zeros((len(text)*4,2), dtype=np.float32)
        self.attrib   = np.zeros((len(text)*4,1), dtype=np.float32)
        pen = [x,y]
        prev = None

        for i,charcode in enumerate(text):
            glyph = font[charcode]
            kerning = glyph.get_kerning(prev)/64.0
            x0 = pen[0] + glyph.offset[0] + kerning
            dx = x0-int(x0)
            x0 = int(x0)
            y0 = pen[1] + glyph.offset[1]
            x1 = x0 + glyph.size[0]
            y1 = y0 - glyph.size[1]
            u0 = glyph.texcoords[0]
            v0 = glyph.texcoords[1]
            u1 = glyph.texcoords[2]
            v1 = glyph.texcoords[3]

            index     = i*4
            indices   = [index, index+1, index+2, index, index+2, index+3]
            vertices  = [[x0,y0,1],[x0,y1,1],[x1,y1,1], [x1,y0,1]]
            texcoords = [[u0,v0],[u0,v1],[u1,v1], [u1,v0]]
            colors    = [color,]*4

            self.vertices[i*4:i*4+4] = vertices
            self.indices[i*6:i*6+6] = indices
            self.texcoords[i*4:i*4+4] = texcoords
            self.colors[i*4:i*4+4] = colors
            self.attrib[i*4:i*4+4] = dx
            pen[0] = pen[0]+glyph.advance[0]/64.0 + kerning
            pen[1] = pen[1]+glyph.advance[1]/64.0
            prev = charcode

        width = pen[0]-glyph.advance[0]/64.0+glyph.size[0]

        if anchor_y == 'top':
            dy = -round(font.ascender)
        elif anchor_y == 'center':
            dy = +round(-font.height/2-font.descender)
        elif anchor_y == 'bottom':
            dy = -round(font.descender)
        else:
            dy = 0

        if anchor_x == 'right':
            dx = -width/1.0
        elif anchor_x == 'center':
            dx = -width/2.0
        else:
            dx = 0
        self.vertices += (round(dx), round(dy), 0)

        self.vertices_ptr = self.vertices.ctypes.data
        self.colors_ptr = self.colors.ctypes.data
        self.texcoords_ptr = self.texcoords.ctypes.data
        self.indices_ptr = self.indices.ctypes.data

        print self.vertices, self.colors, self.texcoords, self.indices
        self._setup_shader()

    def _setup_shader(self):
        self.program = get_shader_program( "font", "120" )

        self.aPosition = self.program.attributeLocation("aPosition")
        print "pos", self.aPosition
        self.aColor = self.program.attributeLocation("bColor")

        self.projMatrix = self.program.uniformLocation("projMatrix")
        print "proj", self.projMatrix
        self.modelviewMatrix = self.program.uniformLocation("modelviewMatrix")
        print "modelview", self.modelviewMatrix

        self.texture = self.program.uniformLocation("texture")
        print "texture", self.texture

        self.pixel = self.program.uniformLocation("pixel")
        print "pixel", self.pixel


    def draw(self):
        print("draw labels")

        #glClearColor(1,1,1,1)
        #glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        glBindTexture( GL_TEXTURE_2D, self.atlas.texid )

        glEnable( GL_TEXTURE_2D )
        glDisable( GL_DEPTH_TEST )

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glEnableClientState(GL_VERTEX_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, self.vertices_ptr)
        glColorPointer(4, GL_FLOAT, 0, self.colors_ptr)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcoords_ptr)

        alpha = 1
        glEnable( GL_COLOR_MATERIAL )
        glBlendFunc( GL_CONSTANT_COLOR_EXT, GL_ONE_MINUS_SRC_COLOR )
        glEnable( GL_BLEND )
        glColor3f( alpha, alpha, alpha )
        glBlendColor( 1-alpha, 1-alpha, 1-alpha, 1 )

        self.program.bind()

        self.program.setUniformValueArray( self.projMatrix,
            QMatrix4x4( tuple(vsml.projection.ravel().tolist()) ),
            16 )

        self.program.setUniformValueArray( self.modelviewMatrix,
            QMatrix4x4( tuple(vsml.modelview.ravel().tolist()) ),
            16 )

        #glEnableVertexAttribArray( 1 )
        #glVertexAttribPointer( 1, 1, GL_FLOAT, GL_FALSE, 0, self.attrib)

        #self.program.enableAttributeArray( self.aPosition )
        #glVertexAttribPointer(self.aPosition, 1, GL_FLOAT, GL_FALSE, 0, 0)

        # shader.bind()
        #shader.uniformi('texture', 0)
        self.program.setUniformValue( self.texture, 0 )
        #shader.uniformf('pixel', 1.0/512, 1.0/512)
        self.program.setUniformValue( self.pixel, 1.0/512, 1.0/512 )
        
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, self.indices_ptr)
        
        #shader.unbind()

        self.program.disableAttributeArray( self.aPosition )
        # self.program.disableAttributeArray( self.aColor )

        self.program.release()
        # glDisableVertexAttribArray( 1 )

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisable( GL_TEXTURE_2D )
        glDisable( GL_BLEND )




if __name__ == '__main__':
    import sys

    atlas = TextureAtlas(512,512,3)

    def on_display( ):
        gl.glClearColor(1,1,1,1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glBindTexture( gl.GL_TEXTURE_2D, atlas.texid )
        for label in labels: label.draw()
        gl.glColor(0,0,0,1)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2i(15,0)
        gl.glVertex2i(15, 330)
        gl.glVertex2i(225, 0)
        gl.glVertex2i(225, 330)
        gl.glEnd()
        glut.glutSwapBuffers( )

    def on_reshape( width, height ):
        gl.glViewport( 0, 0, width, height )
        gl.glMatrixMode( gl.GL_PROJECTION )
        gl.glLoadIdentity( )
        gl.glOrtho( 0, width, 0, height, -1, 1 )
        gl.glMatrixMode( gl.GL_MODELVIEW )
        gl.glLoadIdentity( )

    def on_keyboard( key, x, y ):
        if key == '\033':
            sys.exit( )

    glut.glutInit( sys.argv )
    glut.glutInitDisplayMode( glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH )
    glut.glutCreateWindow( "Freetype OpenGL" )
    glut.glutReshapeWindow( 240, 330 )
    glut.glutDisplayFunc( on_display )
    glut.glutReshapeFunc( on_reshape )
    glut.glutKeyboardFunc( on_keyboard )


    text = "|... A Quick Brown Fox Jumps Over The Lazy Dog"
    labels = []
    x,y = 20,310
    for i in range(30):
        labels.append(Label(text=text, font=font, x=x, y=y))
        x += 0.1000000000001
        y -= 10
    atlas.upload()
    shader = Shader(vert,frag)
    glut.glutMainLoop( )