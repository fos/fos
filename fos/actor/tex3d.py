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
from nibabel.affines import from_matvec


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
        volume = np.zeros(3 * (vol_dim,) + data.shape[-1])
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

def ijktoras(ijk, data_shape, affine, container_shape, vol_viz = True):
    """
    Parameters
    ----------
    ijk : array, shape (N, 3)
    data : array, shape (X, Y, Z)
    container : array, shape (X'>X, Y'>Y, Z'>Z)
    vol_viz : bool

    Examples
    --------
    >>> ijktoras(np.array([[90., 126, 72.],[91., 109., 91.]]).T, data, affine, np.zeros(3*(256,)), False)
    array([[  0.,  -1.],
        [  0., -17.],
        [  0.,  19.],
        [  1.,   1.]])

    """

    ijk = ijk.T

    ijk1 = np.vstack((ijk, np.ones(ijk.shape[1])))
    
    if vol_viz:

        KJI = from_matvec(np.flipud(np.eye(3)), [0, 0, 0])
        
        di, dj, dk = data_shape[:3]
        ci, cj, ck = container_shape[:3]

        CON = from_matvec(np.eye(3), [ci / 2 - di / 2, 
                                      cj / 2 - dj / 2, 
                                      ck / 2 - dk / 2])

        xyz1 = np.dot(affine, np.dot(KJI, np.dot(CON, ijk1)))
        ras2las = np.eye(4)
        ras2las[0, 0] = -1
        xyz1 = np.dot(ras2las, xyz1)
        xyz = xyz1[:-1, :]
        tex1 = np.dot(KJI, np.dot(CON, ijk1))
        tex = tex1[:-1, :] / container_shape[0]
        return xyz.T, tex.T

    else:

        xyz1 = np.dot(affine, ijk1)
        #ras2las = np.eye(4)
        #ras2las[0, 0] = -1
        #xyz1 = np.dot(ras2las, xyz1)
        xyz = xyz1[:-1, :]
        tex = None
        return xyz.T, tex

if __name__=='__main__':

    import numpy as np
    import nibabel as nib
    from fos import Window, Scene
    from fos.actor import Axes, Text3D
    
    #dname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/'
    #fname = dname + 'T1_flirt_out.nii.gz'
    dname = '/home/eg309/Data/111104/subj_05/'
    fname = dname + '101_32/DTI/fa.nii.gz'
    dname = '/usr/share/fsl/data/standard/'
    fname = dname + 'FMRIB58_FA_1mm.nii.gz'
    img=nib.load(fname)
    data = img.get_data()
    data[np.isnan(data)] = 0
    data = np.interp(data, [data.min(), data.max()], [0, 255])
    data = data.astype(np.ubyte)
    affine = img.get_affine() 
    print data.shape
    #affine = None

    #volume = prepare_volume(data)
    I, J, K = data.shape[:3]
	
    window = Window(caption='[F]OS',bgcolor = (0, 0, 0.6))
    scene = Scene(activate_aabb = False)
    
    texi = Texture3D('i', data, affine=None, interp='linear')
    texj = Texture3D('j', data, affine=None, interp='linear')
    texk = Texture3D('k', data, affine=None, interp='linear')

    container_size = texi.container.shape[0]

    centershift, _ = ijktoras(np.array([[I/2., J/2., K/2.]]), data.shape,
                            affine, 3 * (container_size,), True)

    i = I / 2.
    imgcoords = np.array([[i, 0, 0], 
                          [i, 0, K], 
                          [i, J, K], 
                          [i, J, 0]], dtype='f8')
    vertcoords, texcoords = ijktoras(imgcoords, data.shape, 
                                        affine, 3 * (container_size,), True)
    
    vertcoords = vertcoords - centershift
    texi.update_quad(texcoords, vertcoords)
    
    j = J / 2.
    imgcoords = np.array([[0, j, 0], 
                          [0, j, K], 
                          [I, j, K], 
                          [I, j, 0]], dtype='f8')
    
    vertcoords, texcoords = ijktoras(imgcoords, data.shape, 
                                        affine, 3 * (container_size,), True)
    
    vertcoords = vertcoords - centershift
    texj.update_quad(texcoords, vertcoords)

    k = K / 2.
    imgcoords = np.array([[0, 0, k], 
                          [0, J, k], 
                          [I, J, k], 
                          [I, 0, k]], dtype='f8')

    vertcoords, texcoords = ijktoras(imgcoords, data.shape, 
                                        affine, 3 * (container_size,), True)
    
    vertcoords = vertcoords - centershift
    texk.update_quad(texcoords, vertcoords)

    #ax = Axes(name="3 axes", scale=200, linewidth=2.0)

    scene.add_actor(texi)
    scene.add_actor(texj)
    scene.add_actor(texk)
    #scene.add_actor(ax)
    window.add_scene(scene)
    window.refocus_camera()


