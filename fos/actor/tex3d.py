import pyglet
import numpy as np
from ctypes import *
from pyglet.gl import *
from fos import Actor


class Texture3D(Actor):

    def __init__(self, name, data, affine, 
                    interp='nearest', mode='clamp'):
        """ creates a 3D Texture
        
        Parameters
        ----------
        name : str
        affine : array, shape (4, 4), image affine                
        data : array, dtype ubyte,
                shape (X, Y, Z), grayscale
                or shape (X, Y, Z, 3), rgb
                or shape (X, Y, Z, 4), rgba
        interp : str,
                nearest or linear
        mode : str,
                clamp
        
        Notes
        ------                
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

        if data.ndim == 3:
            self.type = GL_LUMINANCE
        if data.ndim == 4:
            if data.shape[-1] == 3:
                self.type = GL_RGB
            if data.shape[-1] == 4:
                self.type = GL_RGBA
        if interp == 'linear':
            self.interp = GL_LINEAR
        if interp == 'nearest':
            self.interp = GL_NEAREST
        if mode == 'clamp':
            self.mode = GL_CLAMP

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
        #enable full colour for the texture
        glColor4f(1., 1., 1, 1.)
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
        di = i
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

        if self.affine is None:
            vertcoords = np.array([ [-O/2., -N/2., di - M/2],
                                    [-O/2., N/2., di - M/2],
                                    [O/2., N/2., di - M/2],
                                    [O/2, -N/2., di - M/2] ])
        
            return texcoords, vertcoords

    def slice_j(self, j):
        I, J, K = self.container.shape[:3]
        M, N, O = self.data.shape[:3]
        dj = j
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
        if self.affine is None:
            vertcoords = np.array([ [-O/2., -M/2., dj - N/2],
                                    [-O/2., M/2., dj - N/2],
                                    [O/2., M/2., dj - N/2],
                                    [O/2, -M/2., dj - N/2] ])
        
            return texcoords, vertcoords    

    def slice_k(self, k):
        I, J, K = self.container.shape[:3]
        M, N, O = self.data.shape[:3]
        dk = k
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

        if self.affine is None:
            vertcoords = np.array([ [-N/2., -M/2., dk - O/2],
                                    [-N/2., M/2., dk - O/2],
                                    [N/2., M/2., dk - O/2],
                                    [N/2, -M/2., dk - O/2] ])
            
            return texcoords, vertcoords    


def prepare_volume(data, fill=None):
    """ add data in a container of size power of 2
    """

    if fill == None:
        if data.ndim == 4:
            if data.shape[-1] == 3:
                fill = (0, 0, 0)
            if data.shape[-1] == 4:
                fill = (0, 0, 0, 255)
        if data.ndim == 3:
            fill = 0

    max_dimension = max(data.shape)
    pow2 = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024])
    vol_dim = pow2[np.where(pow2 >= max_dimension)[0][0]]
    
    if data.ndim == 4:
        volume = np.zeros(3 * (vol_dim,) + (data.shape[-1],))
    if data.ndim == 3:
        volume = np.zeros(3 * (vol_dim,))

    volume = volume.astype(np.ubyte)
    
    if data.ndim >= 3:
        volume[..., :] = fill 

    i, j, k = volume.shape[:3]
    ci, cj, ck = (i/2, j/2, k/2)
    di, dj, dk = data.shape[:3]
    
    if data.ndim >= 3:
        volume[ ci - di/2 : ci + di - di/2, \
                cj - dj/2 : cj + dj - dj/2, \
                ck - dk/2 : ck + dk - dk/2] = data.copy()

    return volume


if __name__=='__main__':
    pass
