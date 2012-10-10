import numpy as np
from ctypes import *
from pyglet.gl import *
from fos import Actor


class Texture3D(Actor):

    def __init__(self, name, data, affine):
        """ creates a slicer object
        
        Parameters
        -----------
        affine : array, shape (4,4), image affine
                
        data : array, shape (X,Y,Z), data volume
        
        Notes
        ---------                
        http://content.gpwiki.org/index.php/OpenGL:Tutorials:3D_Textures
        
        """
        self.name = name
        super(Texture3D, self).__init__(self.name)
        self.shape = data.shape
        self.data = data
        self.affine = affine
        #volume center coordinates
        self.vertices = np.array([[-130, -130, -130], 
                                  [130, 130, 130]])
        self.setup_texture(self.data)
        #pic=255*np.ones((100, 100),dtype=np.uint8)
        #self.buzz=self.create_texture(pic,100,100)

    def setup_texture(self, volume):
        WIDTH,HEIGHT,DEPTH = volume.shape[:-1]
        #print WIDTH,HEIGHT,DEPTH
        glActiveTexture(GL_TEXTURE0)
        self.texture_index = c_uint(0)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glGenTextures(1, byref(self.texture_index))
        glBindTexture(GL_TEXTURE_3D, self.texture_index.value)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage3D(GL_TEXTURE_3D, 0, GL_RGB, 
                     WIDTH, HEIGHT, DEPTH, 0, 
                     GL_RGB, GL_UNSIGNED_BYTE, 
                     volume.ctypes.data)

        #glBindTexture(GL_TEXTURE_3D, texture_index.value)

        """
        list_index = glGenLists(1)
        glNewList(list_index, GL_COMPILE) 
        glEnable(GL_TEXTURE_3D)
        #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glBindTexture(GL_TEXTURE_3D, texture_index.value)
        glBegin(GL_QUADS)
        
        dep = (0.5 + self.index) / np.float(DEPTH)

        w = WIDTH
        h = HEIGHT

        depth, height, width = (dep, 0., 0.)
        glTexCoord3d(depth, height, width)
        glVertex3d(-w/2., -h/2., 0.0)

        depth, height, width = (dep, 0., 1.)
        glTexCoord3d(depth, height, width)
        glVertex3d(-w/2., h/2., 0.0)

        depth, height, width = (dep, 1., 1.)
        glTexCoord3d(depth, height, width)
        glVertex3f(w/2., h/2., 0.0)

        depth, height, width = (dep, 1., 0)
        glTexCoord3d(depth, height, width)
        glVertex3d(w/2., -h/2., 0.0)
        
        glEnd()
        glDisable(GL_TEXTURE_3D)
        glEndList()
        self.buzz=list_index
        """
    def update_quad(self, texcoords, vertcoords):
        self.texcoords = texcoords
        self.vertcoords = vertcoords

        
    def draw(self):
        #print 'in draw'
        self.set_state() 
        glPushMatrix()
        glBegin
        glEnable(GL_TEXTURE_3D)
        glBindTexture(GL_TEXTURE_3D, self.texture_index.value)
        glBegin(GL_QUADS)        
        for i in range(4):
            glTexCoord3d(*tuple(self.texcoords[i]))
            glVertex3d(*tuple(self.vertcoords[i]))
        glEnd()
        glPopMatrix()
        #self.draw_cube()            
        self.unset_state()
    
    def set_state(self):
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def unset_state(self):
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)


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
    vert2 = np.array([[10.0,10.0,0.0]], dtype = np.float32)
    ptr2 = np.array([[.2,.2,.2]], dtype = np.float32)

    #tex2 = Text3D("Text3D2", vert, "Differ", 10, 2)

    """
    def process_pickray(self,near,far):
        pass
    
    def process_mouse_motion(self,x,y,dx,dy):
        self.mouse_x=x
        self.mouse_y=y
    

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
    region.add_actor(ax)
    region.add_actor(bz)
    region.add_actor(tex)
    #region.add_actor(tex2)
    #region.add_actor(me)
    #w.screenshot( 'red.png' )
    w.add_region(region)
    w.refocus_camera()

