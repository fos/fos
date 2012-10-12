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
                +   +
                |  /
          T     | / R (depth)
       (height) |/
                -------- +
                    S (width)

        Data Coordinates
        data[r, t, s] (reverse order)        

        World Coordinates
                +  
                |
              y |
                |                 
                ---------- +
               /     x
            z /
             /
            +
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
        WIDTH, HEIGHT, DEPTH = volume.shape[:3]
        #HEIGHT, WIDTH, DEPTH = volume.shape[:3]
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
        self.set_state() 
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
        glDisable(GL_TEXTURE_3D)
        self.unset_state()
    
    def set_state(self):
        glShadeModel(GL_FLAT)
        glDisable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def unset_state(self):
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

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

def prepare_volume(data, fill=(255, 255, 255, 255)):
    vol_shape = (256, 256, 256, 4) 
    volume = texture_volume(vol_shape, fill) 
    i, j, k = volume.shape[:3]
    ci, cj, ck = (i/2, j/2, k/2)
    di, dj, dk = data.shape    
    for i in range(3):
        volume[ ci - di/2 : ci + di/2, \
                cj - dj/2 : cj + dj/2, \
                ck - dk/2 : ck + dk/2, i] = data.copy()
    return volume


def texture_volume(shape, fill):
    volume = np.zeros(shape)
    volume = volume.astype(np.ubyte)    
    volume[..., :] = fill #(255, 255 , 255, 255)
    #w, h, d = volume.shape[:3]
    #volume[w/2 - 80 : w/2 + 80, h/2 - 20 : h/2 + 20, d/2 - 10 : d/2 + 10, :] = (255, 0, 0, 255)
    #print volume.shape, volume.min(), volume.max()
    return volume

def slice_i(i, shape):
    I, J, K = shape[:3]
    i = (i + 0.5) / np.float(I)
    texcoords = np.array([  [0, 0, i], 
                            [ 0, 1, i], 
                            [ 1, 1, i],
                            [1, 0, i] ])
    vertcoords = np.array([ [-J/2., -K/2., 0.],
                            [-J/2., K/2., 0.],
                            [J/2., K/2., 0.],
                            [J/2, -K/2., 0] ])
    return texcoords, vertcoords    


def slice_j(j, shape):
    I, J, K = shape[:3]
    j = (j + 0.5) / np.float(J)
    texcoords = np.array([  [0, j, 0], 
                            [ 0, j, 1], 
                            [ 1, j, 1],
                            [1, j, 0] ])
    vertcoords = np.array([ [-I/2., -K/2., 0.],
                            [-I/2., K/2., 0.],
                            [I/2., K/2., 0.],
                            [I/2, -K/2., 0] ])
    return texcoords, vertcoords    


def slice_k(k, shape):
    I, J, K = shape[:3]
    k = (k + 0.5) / np.float(K)
    texcoords = np.array([  [k, 0, 0], 
                            [k, 0, 1], 
                            [k, 1, 1],
                            [k, 1, 0] ])
    vertcoords = np.array([ [-I/2., -J/2., 0.],
                            [-I/2., J/2., 0.],
                            [I/2., J/2., 0.],
                            [I/2, -J/2., 0] ])
    return texcoords, vertcoords    
    


if __name__=='__main__':

    import numpy as np
    import nibabel as nib
    from fos import Window, Region
    from fos.actor import Axes, Text3D
    
    #dname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/'
    #fname = dname + 'T1_flirt_out.nii.gz'
    dname = '/usr/share/fsl/data/standard/'
    fname = dname + 'FMRIB58_FA_1mm.nii.gz'
    img=nib.load(fname)
    data = img.get_data()
    data = np.interp(data, [data.min(), data.max()], [0, 255])
    #affine = img.get_affine()  
    affine = None

    volume = prepare_volume(data)
    i, j, k = volume.shape[:3]
	
    window = Window()
    region = Region()
    
    #volume = np.ascontiguousarray(np.swapaxes(volume, 1, 0))
    
    tex = Texture3D('Buzz', volume, affine, type=GL_RGBA, interp=GL_LINEAR)

    #texcoords, vertcoords = slice_i(i/2, volume.shape) 
    #texcoords, vertcoords = slice_j(j/2, volume.shape) 
    texcoords, vertcoords = slice_k(k/2, volume.shape) 

    tex.update_quad(texcoords, vertcoords)

    ax = Axes(name="3 axes", linewidth=2.0)
    vert = np.array([[2.0,3.0,0.0]], dtype = np.float32)
    ptr = np.array([[.2,.2,.2]], dtype = np.float32)
    #text = Text3D("Text3D", vert, "Reg", 20, 6, ptr)

    region.add_actor(tex)
    #region.add_actor(ax)
    #region.add_actor(text)
    window.add_region(region)
    window.refocus_camera()



