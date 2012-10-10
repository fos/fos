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
import numpy as np
from ctypes import *
from pyglet.gl import *
from fos import Actor


class Texture3D(Actor):

    def __init__(self, name, data, affine, 
                    type=GL_RGB, interp=GL_NEAREST, mode=GL_CLAMP):
        """ creates a 3D Texture
        
        Parameters
        ----------
        name : str
        affine : array, shape (4,4), image affine                
        data : array, shape (X,Y,Z), data volume
        
        Notes
        ---------                
        http://content.gpwiki.org/index.php/OpenGL:Tutorials:3D_Textures
        CULLFACE is disabled here otherwise the texture needs to be drawn twice on for GL_FRONT and one for GL_BACK

        Texture Coordinates  

                |  /
          T     | / R (depth)
       (height) |/
                -------- 
                    S (width)

        Data Coordinates
        data[r, t, s] (reverse order)        

        World Coordinates

                |
              y |
                |                 
                ----------
               /     x
            z /
             /

        """
        self.name = name
        super(Texture3D, self).__init__(self.name)
        self.shape = data.shape
        self.data = data
        self.affine = affine
        self.type = type
        self.interp = interp
        self.mode = mode
        #volume center coordinates
        self.vertices = np.array([[-130, -130, -130], 
                                  [130, 130, 130]])
        self.setup_texture(self.data)
        #pic=255*np.ones((100, 100),dtype=np.uint8)
        #self.buzz=self.create_texture(pic,100,100)

    def setup_texture(self, volume):
        WIDTH,HEIGHT,DEPTH = volume.shape[:3]
        #print WIDTH,HEIGHT,DEPTH
        #glActiveTexture(GL_TEXTURE0)
        self.texture_index = c_uint(0)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glGenTextures(1, byref(self.texture_index))
        glBindTexture(GL_TEXTURE_3D, self.texture_index.value)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, self.mode)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, self.mode)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, self.mode)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, self.interp)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, self.interp)
        glTexImage3D(GL_TEXTURE_3D, 0, self.type, 
                     WIDTH, HEIGHT, DEPTH, 0, 
                     self.type, GL_UNSIGNED_BYTE, 
                     volume.ctypes.data)
    
    def update_quad(self, texcoords, vertcoords):
        self.texcoords = texcoords
        self.vertcoords = vertcoords
        
    def draw(self):
        #print 'in draw'
        self.set_state() 
        #glPushMatrix()
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_3D)
        glBindTexture(GL_TEXTURE_3D, self.texture_index.value)
        glBegin(GL_QUADS)        
        glTexCoord3d(*tuple(self.texcoords[0]))
        glVertex3d(*tuple(self.vertcoords[0]))
        glTexCoord3d(*tuple(self.texcoords[1]))
        glVertex3d(*tuple(self.vertcoords[1]))
        glTexCoord3d(*tuple(self.texcoords[2]))
        glVertex3d(*tuple(self.vertcoords[2]))
        glTexCoord3d(*tuple(self.texcoords[3]))
        glVertex3d(*tuple(self.vertcoords[3]))
        glEnd()
        #glPopMatrix()
        #self.draw_cube()            
        self.unset_state()
    
    def set_state(self):
        #glShadeModel(GL_FLAT)
        glDisable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def unset_state(self):
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)


if __name__=='__main__':

    from fos.actor.axes import Axes
    from fos import Window, Region
    from fos.actor import Text3D

    #fname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/T1_flirt_out.nii.gz'
    #img=nib.load(fname)
    #data = img.get_data()
    #affine = img.get_affine()
    affine=None
    data=(255*np.random.rand(256,256,256)).astype(np.uint8)
    data[:]=255
    volume = np.zeros(data.shape+(3,))
    volume[...,0] = data.copy()
    volume[...,1] = data.copy()
    volume[...,2] = data.copy()
    volume = volume.astype(np.ubyte)
    bz=Texture3D('Buzz', volume, affine)
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
 
    bz.update_quad(texcoords, vertcoords)
    

    title='Texture3D'
    w = Window(caption = title, 
                width = 1200, 
                height = 800, 
                bgcolor = (0.,0.,0.2))

    region = Region(regionname = 'Main',
                        extent_min = np.array([-5.0, -5, -5]),
                        extent_max = np.array([5, 5 ,5]),
                        activate_aabb = True)
    
    #ax = Axes(name="3 axes", linewidth=2.0)
    vert = np.array([[2.0,3.0,0.0]], dtype = np.float32)
    ptr = np.array([[.2,.2,.2]], dtype = np.float32)
    #tex = Text3D("Text3D", vert, "Reg", 10, 2, ptr)
    #vert2 = np.array([[10.0,10.0,0.0]], dtype = np.float32)
    #ptr2 = np.array([[.2,.2,.2]], dtype = np.float32)

    #region.add_actor(ax)
    region.add_actor(bz)
    #region.add_actor(tex)
    #region.add_actor(tex2)
    #region.add_actor(me)
    #w.screenshot( 'red.png' )
    w.add_region(region)
    w.refocus_camera()

