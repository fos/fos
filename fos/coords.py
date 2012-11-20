import numpy as np
#from fos.actor.tex3d import Texture3D
#from fos import Scene, Window, Init, Run


def rotation_matrix(axis, theta_degree):
    """ Create rotation matrix for angle theta along axis

    Parameters
    ----------
    axis : array, shape (3, )
            rotation axis
    theta_degree : float,
            rotation angle in degrees

    Returns
    -------
    mat : array, shape (3, 3)

    """
    theta = 1. * theta_degree * np.pi / 180.
    axis = 1. * axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2)
    b, c, d = - axis * np.sin(theta / 2)
    mat = np.array([[a*a + b*b - c*c - d*d, 2*(b*c - a*d), 2*(b*d + a*c)],
                     [2*(b*c + a*d), a*a + c*c - b*b - d*d, 2*(c*d - a*b)],
                     [2*(b*d - a*c), 2*(c*d + a*b), a*a + d*d - b*b - c*c]])
    return mat


def from_matvec(matrix, vector=None):
    """ Combine a matrix and vector into an homogeneous affine

    Combine a rotation / scaling / shearing matrix and translation vector 
    into a transform in homogeneous coordinates.

    Parameters
    ----------
    matrix : array-like
        An NxM array representing the the linear part of the transform.
        A transform from an M-dimensional space to an N-dimensional space.
    vector : None or array-like, optional
        None or an (N,) array representing the translation. None corresponds to
        an (N,) array of zeros.

    Returns
    -------
    xform : array
        An (N+1, M+1) homogenous transform matrix.


    Examples
    --------
    >>> from_matvec(np.diag([2, 3, 4]), [9, 10, 11])
    array([[ 2,  0,  0,  9],
           [ 0,  3,  0, 10],
           [ 0,  0,  4, 11],
           [ 0,  0,  0,  1]])

    The `vector` argument is optional:

    >>> from_matvec(np.diag([2, 3, 4]))
    array([[2, 0, 0, 0],
           [0, 3, 0, 0],
           [0, 0, 4, 0],
           [0, 0, 0, 1]])
    """
    matrix = np.asarray(matrix)
    nin, nout = matrix.shape
    t = np.zeros((nin+1,nout+1), matrix.dtype)
    t[0:nin, 0:nout] = matrix
    t[nin, nout] = 1.
    if not vector is None:
        t[0:nin, nout] = vector
    return t


def img_to_ras_coords(ijk, affine):
    """ Image coordinates to world (RAS) coordinates

    Parameters
    ----------
    ijk : array, shape (N, 3)
        image coordinates
    affine : array, shape (4, 4)
        transformation matrix 

    Returns
    -------
    xyz : array, shape (N, 3)
        world coordinates in RAS (Neurological Convention)

    """

    ijk = ijk.T
    ijk1 = np.vstack((ijk, np.ones(ijk.shape[1])))
    xyz1 = np.dot(affine, ijk1)
    xyz = xyz1[:-1, :]
    return xyz.T


def img_to_ras_coords_container(ijk, data_shape, affine):
    """ Image coordinates to world (RAS) coordinates

    Data are assumed inserted in a container volume with shape made of powers
    of two which is the standard for 3D textures. 
    """
    ijk = ijk.T

    ijk1 = np.vstack((ijk, np.ones(ijk.shape[1])))
    
    KJI = from_matvec(np.flipud(np.eye(3)), [0, 0, 0])
    
    di, dj, dk = data_shape[:3]

    max_dimension = max(data_shape)
    pow2 = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024])
    vol_dim = pow2[np.where(pow2 >= max_dimension)[0][0]]

    container_shape = 3 * (vol_dim,) 
    
    ci, cj, ck = container_shape[:3]

    CON = from_matvec(np.eye(3), [ci / 2 - di / 2, 
                                  cj / 2 - dj / 2, 
                                  ck / 2 - dk / 2])

    xyz1 = np.dot(affine, np.dot(KJI, np.dot(CON, ijk1)))
    return xyz1[:-1, :].T


def ras_to_las_coords(xyz):
    """ From RAS (neurological) to LAS (radiological) coordinates

    Parameters
    ----------
    xyz : array, shape (N, 3)
            RAS coordinates

    Returns
    -------
    xyzlas : array, shape (N, 3)
            LAS coordinates
    """
    
    xyz = xyz.T

    xyz1 = np.vstack((xyz, np.ones(xyz.shape[1])))

    ras2las = np.eye(4)
    ras2las[0, 0] = -1
    
    xyz1las = np.dot(ras2las, xyz1)
    xyzlas = xyz1las[:-1, :]
    return xyzlas.T


def img_to_tex_coords(ijk, data_shape):
    """ Image coordinates to texture3D coordinates

    Parameters
    ----------
    ijk : array, shape (N, 3)
            image coordinates (native space)
    data_shape : tuple,
            volume shape

    Returns
    -------
    ijktex : array, shape (N, 3)
            texture3D coordinates (texture space)

    """
    ijk = ijk.T

    ijk1 = np.vstack((ijk, np.ones(ijk.shape[1])))
    
    KJI = from_matvec(np.flipud(np.eye(3)), [0, 0, 0])
    
    di, dj, dk = data_shape[:3]
    
    max_dimension = max(data_shape)
    pow2 = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024])
    vol_dim = pow2[np.where(pow2 >= max_dimension)[0][0]]

    container_shape = 3 * (vol_dim,) 
    ci, cj, ck = container_shape[:3]

    CON = from_matvec(np.eye(3), [ci / 2 - di / 2, 
                                  cj / 2 - dj / 2, 
                                  ck / 2 - dk / 2])

    tex1 = np.dot(KJI, np.dot(CON, ijk1))
    tex = tex1[:-1, :] / container_shape[0]
    return tex.T


if __name__=='__main__':

    import numpy as np
    import nibabel as nib
    from fos import Window, Scene
    from fos.actor import Axes, Text3D
    from fos.actor.tex3d import Texture3D
    
    #dname='/home/eg309/Data/trento_processed/subj_03/MPRAGE_32/'
    #fname = dname + 'T1_flirt_out.nii.gz'
    dname = '/home/eg309/Data/111104/subj_05/'
    fname = dname + '101_32/DTI/fa.nii.gz'
    #dname = '/usr/share/fsl/data/standard/'
    #fname = dname + 'FMRIB58_FA_1mm.nii.gz'
    img=nib.load(fname)
    data = img.get_data()
    data[np.isnan(data)] = 0
    data = np.interp(data, [data.min(), data.max()], [0, 255])
    data = data.astype(np.ubyte)
    affine = img.get_affine() 
    print data.shape

    I, J, K = data.shape[:3]
	
    window = Window(caption='[F]OS',bgcolor = (0, 0, 0.6))
    scene = Scene(activate_aabb = False)
    
    texi = Texture3D('i', data, affine=None, interp='linear')
    texj = Texture3D('j', data, affine=None, interp='linear')
    texk = Texture3D('k', data, affine=None, interp='linear')

    container_size = texi.container.shape[0]

    #centershift, _ = ijktoras(np.array([[I/2., J/2., K/2.]]), data.shape,
    #                        affine, 3 * (container_size,), True)

    #print centershift
    centershift = img_to_ras_coords_container(np.array([[I/2., J/2., K/2.]]), 
                    data.shape, affine)

    centershift = ras_to_las_coords(centershift)

    i = I / 2.
    imgcoords = np.array([[i, 0, 0], 
                          [i, 0, K], 
                          [i, J, K], 
                          [i, J, 0]], dtype='f8')
    #vertcoords, texcoords = ijktoras(imgcoords, data.shape, 
    #                                    affine, 3 * (container_size,), True)
    
    vertcoords = img_to_ras_coords_container(imgcoords, data.shape, affine)
    vertcoords = ras_to_las_coords(vertcoords)
    texcoords = img_to_tex_coords(imgcoords, data.shape)

    vertcoords = vertcoords - centershift
    texi.update_quad(texcoords, vertcoords)
    
    j = J / 2.
    imgcoords = np.array([[0, j, 0], 
                          [0, j, K], 
                          [I, j, K], 
                          [I, j, 0]], dtype='f8')
    
    vertcoords = img_to_ras_coords_container(imgcoords, data.shape, affine)
    vertcoords = ras_to_las_coords(vertcoords)
    texcoords = img_to_tex_coords(imgcoords, data.shape)
    
    vertcoords = vertcoords - centershift
    texj.update_quad(texcoords, vertcoords)

    k = K / 2.
    imgcoords = np.array([[0, 0, k], 
                          [0, J, k], 
                          [I, J, k], 
                          [I, 0, k]], dtype='f8')

    vertcoords = img_to_ras_coords_container(imgcoords, data.shape, affine)
    vertcoords = ras_to_las_coords(vertcoords)
    texcoords = img_to_tex_coords(imgcoords, data.shape)
    
    vertcoords = vertcoords - centershift
    texk.update_quad(texcoords, vertcoords)

    scene.add_actor(texi)
    scene.add_actor(texj)
    scene.add_actor(texk)
    window.add_scene(scene)
    window.refocus_camera()

