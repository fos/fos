""" Not to be used yet
 
"""


import numpy as np
import nibabel as nib
from ctypes import *
import pyglet as pyglet
from pyglet.gl import *
from pyglet.window import key

from fos import Actor
from fos.modelmat import screen_to_model
import fos.interact.collision as cll



class BuzzTex(Actor):

    def __init__(self,affine,data):
        """ creates a slicer object
        
        Parameters
        -----------
        affine : array, shape (4,4), image affine
                
        data : array, shape (X,Y,Z), data volume
        
        Notes
        ---------                
        http://content.gpwiki.org/index.php/OpenGL:Tutorials:3D_Textures
        
        """

        self.shape=data.shape
        self.data=data
        self.affine=affine
        #volume center coordinates
        self.vertices=np.array([[-100,-100,-100],[100,100,100]])
        self.make_aabb(margin=0)
        self.show_aabb=True
        #masking
        
        self.setup_texture(self.data)

    def setup_texture(self,volume):
        
        WIDTH,HEIGHT,DEPTH=volume.shape
        print WIDTH,HEIGHT,DEPTH
        texture_index = c_uint(0)
        glGenTextures(1,byref(texture_index))
        glBindTexture(GL_TEXTURE_3D, texture_index.value)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_REPEAT)
        
        
        glTexImage3D(GL_TEXTURE_3D, 0, 1, 
                     WIDTH,HEIGHT, DEPTH, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, 
                     volume.ctypes.data)
        

        w=255
        h=255

        

        list_index = glGenLists(1)
        glNewList(list_index,GL_COMPILE)               
        glEnable(GL_TEXTURE_3D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE,GL_REPLACE)
        glBindTexture(GL_TEXTURE_3D, texture_index.value)
        glBegin(GL_QUADS)
        glTexCoord3d(0,0,0)
        glVertex3f(-w/2., -h/2., 0.0)
        glTexCoord3d(255,0,0)
        glVertex3f(-w/2., h/2., 0.0)
        glTexCoord3d(255, 255,0)
        glVertex3f(w/2., h/2., 0.0)
        glTexCoord3d(255, 0,0)
        glVertex3f(w/2., -h/2., 0.0)
        glEnd()
        glDisable(GL_TEXTURE_3D)
        glEndList()
        self.buzz=list_index
        



    def create_texture(self,pic,w,h):        
        texture_index = c_uint(0)        
        glGenTextures(1,byref(texture_index))
        glBindTexture(GL_TEXTURE_2D, texture_index.value)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)       
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, 1, w, h, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, pic)        
        list_index = glGenLists(1)  
        glNewList(list_index,GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE,GL_REPLACE)
        glBindTexture(GL_TEXTURE_2D, texture_index.value)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-w/2., -h/2., 0.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-w/2., h/2., 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(w/2., h/2., 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(w/2., -h/2., 0.0)
        glEnd()
        glFlush()
        glDisable(GL_TEXTURE_2D)
        glEndList()
        return list_index
        
    def draw(self):
        self.set_state()            
        glPushMatrix()
        glCallList(self.buzz)                
        self.draw_aabb()
        glPopMatrix()
        #self.draw_cube()            
        self.unset_state()
    
    def process_pickray(self,near,far):
        pass
    
    def process_mouse_motion(self,x,y,dx,dy):
        self.mouse_x=x
        self.mouse_y=y
    
    def process_keys(self,symbol,modifiers):        
        if modifiers & key.MOD_SHIFT:            
            print 'Shift'
        if symbol == key.UP:
            print 'Up'
        if symbol == key.DOWN:
            print 'Down'            
        if symbol == key.LEFT:
            print 'Left'
        if symbol == key.RIGHT:
            print 'Right'
        if symbol == key.PAGEUP:
            print 'PgUp'
        if symbol == key.PAGEDOWN:
            print 'PgDown'
        #HIDE SLICES
        if symbol == key._0:
            print('0')
        if symbol == key._1:
            print('1')
            self.show_slices[0]= not self.show_slices[0]            
        if symbol == key._2:
            print('2')
            self.show_slices[1]= not self.show_slices[1]            
        if symbol == key._3:
            print('3')
        if symbol == key.ENTER:
            print('Enter - Store ROI in mask')
        if symbol == key.QUESTION:
            print "?"
                          
        return None            

    def save_mask(self,fname,mask):               
        img_mask=nib.Nifti1Image(mask,self.affine)
        nib.save(img_mask,fname)

    def set_state(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def unset_state(self):
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
   
    def update(self,dt):
        pass



if __name__=='__main__':

    from fos.actor.axes import Axes
    from fos import World, Window, WindowManager
    from fos.actor.buzztex import BuzzTex

    fname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/T1_flirt_out.nii.gz'
    img=nib.load(fname)
    data = img.get_data()
    affine = img.get_affine()
    
    data=(255*np.random.rand(256,256,256)).astype(np.uint8)
    
    #stop
    
    ax=Axes(100)
    bz=BuzzTex(affine,data)

    w=World()
    w.add(ax)
    w.add(bz)

    wi=Window(caption="BuzzTex",bgcolor=(0.,0.1,0.3,1.))
    wi.attach(w)

    wm=WindowManager()
    wm.add(wi)
    wm.run()



