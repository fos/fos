import numpy as np
import nibabel as nib
from ctypes import *
from pyglet.gl import *
from fos import Actor

class BuzzTex(Actor):

    def __init__(self, name, data, affine):
        """ creates a slicer object
        
        Parameters
        ----------
        data : array, shape (X,Y,Z), data volume
        
        affine : array, shape (4,4), image affine
        
        Notes
        -----               
        http://content.gpwiki.org/index.php/OpenGL:Tutorials:3D_Textures
        
        """
        super(BuzzTex, self).__init__(name)
        self.name=name
        self.shape=data.shape
        self.data=data
        self.affine=affine
        #volume center coordinates
        self.vertices=np.array([[-130,-130,-130],[130,130,130]])
        #self.make_aabb(margin=0)
        #self.show_aabb=True
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
        glTexImage2D(GL_TEXTURE_2D, 0, 1, w, h, 0, 
                     GL_LUMINANCE, GL_UNSIGNED_BYTE, pic)        
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
        #print 'in draw'
        self.set_state()            
        glPushMatrix()
        #print self.buzz
        glCallList(self.buzz)                
        glPopMatrix()
        #self.draw_cube()            
        self.unset_state()

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
    from fos import Window, Region
    from fos.actor import Text3D

    #fname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/T1_flirt_out.nii.gz'
    #img=nib.load(fname)
    #data = img.get_data()
    #affine = img.get_affine()
    affine=None
    data=(255*np.random.rand(256,256,256)).astype(np.uint8)
    bz=BuzzTex('Buzz', data, affine)

    title='The invisible BuzzTex'
    w = Window(caption = title, 
                width = 1200, 
                height = 800, 
                bgcolor = (0.,0.,0.2))

    region = Region(regionname = 'Main',
                        extent_min = np.array([-5.0, -5, -5]),
                        extent_max = np.array([5, 5 ,5]))
    
    ax = Axes(name="3 axes", linewidth=2.0)
    vert = np.array([[2.0,3.0,0.0]], dtype = np.float32)
    ptr = np.array([[.2,.2,.2]], dtype = np.float32)
    tex = Text3D("Text3D", vert, "Reg", 10, 2, ptr)

    """
    from fos import Mesh
    from dipy.data import get_sphere
    vertices,faces=get_sphere('symmetric724')       
    from fos.compgeom.gen_normals import normals_from_vertices_faces
    normals=normals_from_vertices_faces(vertices,faces)
    me=Mesh('sphere',
            vertices.astype('f4'),
            faces.astype(np.uint32),
            vertices_normals=normals.astype('f4'))
    """
    #region.add_actor(ax)
    region.add_actor(bz)
    #region.add_actor(me)
    #w.screenshot( 'red.png' )
    w.add_region(region)
    w.refocus_camera()


