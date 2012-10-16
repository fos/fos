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

        S T R
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

        Use imshow(data[/2, :, :, 0], cmap='gray', origin='lower') to see the correspondence.
        """
        self.name = name
        super(Texture3D, self).__init__(self.name)
        container = prepare_volume(data)
        self.data = data
        self.container = container
        self.affine = affine
        self.type = type
        self.interp = interp
        self.mode = mode
        if self.affine is not None:
            raise NotImplementedError()

        #volume center coordinates
        self.vertices = np.array([[-130, -130, -130], 
                                  [130, 130, 130]])
        self.setup_texture(self.container)

    def setup_texture(self, volume):
        WIDTH, HEIGHT, DEPTH = volume.shape[:3]
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
        glBindTexture(GL_TEXTURE_3D, 0)
    
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
        glBindTexture(GL_TEXTURE_3D, 0)
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

    def slice_i(self, i):
        I, J, K = self.container.shape[:3]
        M, N, O = self.data.shape[:3] 
        i = i + I/2 - M/2 
        i = (i + 0.5) / np.float(I)
        j = (J / 2.) / np.float(J)
        k = (K / 2.) / np.float(K)
        n = (np.float(N)/2.) / np.float(J) 
        o = (np.float(O)/2.) / np.float(K)
        texcoords = np.array([  [k-o, j-n, i], 
                                [k-o, j+n, i], 
                                [k+o, j+n, i],
                                [k+o, j-n, i] ])
        vertcoords = np.array([ [-O/2., -N/2., 0.],
                                [-O/2., N/2., 0.],
                                [O/2., N/2., 0.],
                                [O/2, -N/2., 0] ])
        return texcoords, vertcoords    

    def slice_j(self, j):
        I, J, K = self.container.shape[:3]
        M, N, O = self.data.shape[:3]
        j = j + J/2 - N/2 
        j = (j + 0.5) / np.float(J)
        i = (I / 2.) / np.float(I)
        k = (K / 2.) / np.float(K)
        m = (np.float(M) /2.) / np.float(I)
        o = (np.float(O) /2.) / np.float(K)
        
        texcoords = np.array([  [k-o, j, i-m], 
                                [k-o, j, i+m], 
                                [k+o, j, i+m],
                                [k+o, j, i-m] ])
        vertcoords = np.array([ [-O/2., -M/2., 0.],
                                [-O/2., M/2., 0.],
                                [O/2., M/2., 0.],
                                [O/2, -M/2., 0] ])
        return texcoords, vertcoords    


    def slice_k(self, k):
        I, J, K = self.container.shape[:3]
        M, N, O = self.data.shape[:3]
        k = k + K/2 - O/2
        k = (k + 0.5) / np.float(K)
        i = (I / 2.) / np.float(I)
        j = (K / 2.) / np.float(J)
        m = (np.float(M) /2.) / np.float(I)
        n = (np.float(N) /2.) / np.float(J)
     
        texcoords = np.array([  [k, j-n, i-m], 
                                [k, j-n, i+m], 
                                [k, j+n, i+m],
                                [k, j+n, i-m] ])
        vertcoords = np.array([ [-N/2., -M/2., 0.],
                                [-N/2., M/2., 0.],
                                [N/2., M/2., 0.],
                                [N/2, -M/2., 0] ])
        return texcoords, vertcoords    


def prepare_volume(data, fill=(0, 0, 0, 255)):
    max_dimension = max(data.shape)
    pow2 = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024])
    vol_dim = pow2[np.where(pow2>=max_dimension)[0][0]]
    vol_shape = 3*(vol_dim,) + (4,) 
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
    return volume



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

    #volume = prepare_volume(data)
    i, j, k = data.shape[:3]
	
    window = Window(bgcolor=(0, 0, 0.6))
    region = Region()
    
    tex = Texture3D('Buzz', data, affine, type=GL_RGBA, interp=GL_LINEAR)

    #texcoords, vertcoords = tex.slice_i(i/2) 
    #texcoords, vertcoords = tex.slice_j(j/2) 
    texcoords, vertcoords = tex.slice_k(k/2 - 5) 

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



