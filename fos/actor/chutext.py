import numpy as np
from pyglet.gl import *
from fos.actor.base import Actor
from fos.vsml import vsml
from fos.external.freetype import *
from fos.data import get_font
''' For writting many text at many position at the same time
'''


class ChuText3D(Actor):

    def __init__(self, name, location, text, fontcolor):
        
        """ A ChuText3D actor
           
        Parameters
        -----------
        name : str, 
                name of an instant of actor        
        location : array, (N, 3), dtype float32
                N positions of N texts
        text : sequence, str 
                text be displayed, len(text) == N         
        fontcolor : array, (N, 3), dtype float32                     
        """
        super(ChuText3D, self).__init__(name)      
        
        self.numofchu = len(text)        
        self.vertices = location
        self.width = np.zeros(self.numofchu,dtype=np.int32) 
        self.height = np.zeros(self.numofchu,dtype=np.int32)    
                
        self.fontcolor = fontcolor

        self.data =[]
        self.data_ptr =[]
        self.tex_ptr=[]        
        self.text = text         
                          
        self.setup()        
        
    def setup(self):        

        for i in range(0,self.numofchu):
        # create freetype bitmap
            txt = self.text[i]
            dataAlpha = self.make_bitmap(txt)
            temp = np.ones( (dataAlpha.shape[0], dataAlpha.shape[1], 4), dtype = np.ubyte)            
            temp [:,:,0] *= int(255 * self.fontcolor[i][0])
            temp[:,:,1] *= int(255 * self.fontcolor[i][1])
            temp[:,:,2] *= int(255 * self.fontcolor[i][2])
            temp[:,:,3] = dataAlpha             
            self.data.append(temp)
            t = dataAlpha.shape           
            self.height[i] = t[0]/64. #(96,64) - (w,h) is the size of one character in the normal Vera font
            self.width[i] = t[1]/90#96.            
   
            # create 2d texture
            self.data_ptr.append( self.data[i].ctypes.data)
            self.tex_ptr.append(GLuint(0))

            glGenTextures(1, self.tex_ptr[i])
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glBindTexture(GL_TEXTURE_2D, self.tex_ptr[i])
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)      
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.data[i].shape[1], 
                             self.data[i].shape[0], 0, GL_RGBA, 
                            GL_UNSIGNED_BYTE, self.data_ptr[i])
            glBindTexture(GL_TEXTURE_2D, 0)
  
    
    def make_bitmap(self, text):
        """ create a bit map of a text
        
        Parameters
        ----------
        text : str
        
        Returns
        -------
        bitmap : array, shape (height, width)
        """
        face = Face(get_font( 'Vera' ))
        face.set_char_size(96 * 64) #48*64 )
        slot = face.glyph
        # First pass to compute bbox
        width, height, baseline = 0, 0, 0
        previous = 0
        for i,c in enumerate(text):            
            face.load_char(c)
            bitmap = slot.bitmap
            height = max(height, bitmap.rows + max(0,-(slot.bitmap_top-bitmap.rows))) + 1            

            baseline = max(baseline, max(0, - (slot.bitmap_top - bitmap.rows)))
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
        
        for i in range(self.numofchu):    
            
            glEnable( GL_BLEND )
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
            glDisable(GL_DEPTH_TEST)
            glActiveTexture(GL_TEXTURE0)
            glEnable(GL_TEXTURE_2D)                       
                     
            glDisable(GL_LIGHTING)
            
            glBindTexture(GL_TEXTURE_2D, self.tex_ptr[i])                  
            
            if hasattr( vsml, 'camera'):
                # follow with the camera                                       
                ri = vsml.camera.get_right()
                up = vsml.camera.get_yup()                        

                lb = (self.vertices[i,0], self.vertices[i,1], self.vertices[i,2])
                rb = (self.vertices[i,0]+self.width[i]*ri[0],
                      self.vertices[i,1]+self.width[i]*ri[1],
                      self.vertices[i,2]+self.width[i]*ri[2])
                rt = (self.vertices[i,0]+self.width[i]*ri[0]+self.height[i]*up[0],
                      self.vertices[i,1]+self.width[i]*ri[1]+self.height[i]*up[1],
                      self.vertices[i,2]+self.width[i]*ri[2]+self.height[i]*up[2])
                lt = (self.vertices[i,0]+self.height[i]*up[0],
                      self.vertices[i,1]+self.height[i]*up[1],
                      self.vertices[i,2]+self.height[i]*up[2])
            else:               

                lb = (self.vertices[i,0], self.vertices[i,1], self.vertices[i,2])
                rb = (self.vertices[i,0]+self.width, self.vertices[i,1], self.vertices[i,2])
                rt = (self.vertices[i,0]+self.width, self.vertices[i,1]+self.height, self.vertices[i,0,2])
                lt = (self.vertices[i,0], self.vertices[i,1]+self.height, self.vertices[i,2])
    
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
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_BLEND)
           
