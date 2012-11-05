import numpy as np
from fos import Actor, Scene, Window
from fos.actor.tex3d import Texture3D
from fos.actor.axes import Axes
from pyglet.gl import *


class Slicer(Actor):
    def __init__(self, name, data, affine=None):
        """ Volume Slicer

        Parameters
        ----------
        name : str
        data : array, (X, Y, Z) or (X, Y, Z, 3) or (X, Y, Z, 4)
        affine : not implemented (default None)

        """

        self.name = name
        self.data = data
        self.affine = affine 
        self.tex = Texture3D('Buzz', self.data, self.affine, interp='linear')
        self.vertices = self.tex.vertices
        self.visible = True
        self.I, self.J, self.K = self.data.shape[:3]
        self.i, self.j, self.k = self.I/2, self.J/2, self.K/2
        self.texcoords_i, self.vertcoords_i = self.tex.slice_i(self.i) 
        self.texcoords_j, self.vertcoords_j = self.tex.slice_j(self.j) 
        self.texcoords_k, self.vertcoords_k = self.tex.slice_k(self.k) 

        self.show_i = True
        self.show_j = True
        self.show_k = True

    def slice_i(self, i):
        self.i = i
        self.texcoords_i, self.vertcoords_i = self.tex.slice_i(i)
        self.draw()

    def slice_j(self, j):
        self.j = j
        self.texcoords_j, self.vertcoords_j = self.tex.slice_j(j) 
        self.draw()

    def slice_k(self, k):
        self.k = k
        self.texcoords_k, self.vertcoords_k = self.tex.slice_k(k)
        self.draw()

    def draw(self):
        
        if self.show_i: 
            #i Slice
            glPushMatrix()
            #glRotatef(90, 0., 1., 0)
            #glRotatef(90, 0., 0., 1.)
            self.tex.update_quad(self.texcoords_i, self.vertcoords_i)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()
        
        #j Slice
        if self.show_j:
            glPushMatrix()
            #glRotatef(180, 0., 1., 0) # added for fsl convention
            #glRotatef(90, 0., 0., 1.)
            self.tex.update_quad(self.texcoords_j, self.vertcoords_j)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()

        if self.show_k:
            #k Slice
            glPushMatrix()
            #glRotatef(90, 1., 0, 0.)
            #glRotatef(90, 0., 0., 1)
            #glRotatef(180, 1., 0., 0.) # added for fsl
            self.tex.update_quad(self.texcoords_k, self.vertcoords_k)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()
        

def rotation_matrix(axis, theta_degree):
    theta = 1. * theta_degree * np.pi / 180.
    axis = 1. * axis / np.sqrt(np.dot(axis,axis))
    a = np.cos(theta / 2)
    b, c, d = - axis * np.sin(theta / 2)
    return np.array([[a*a + b*b - c*c - d*d, 2*(b*c - a*d), 2*(b*d + a*c)],
                     [2*(b*c + a*d), a*a + c*c - b*b - d*d, 2*(c*d - a*b)],
                     [2*(b*d - a*c), 2*(c*d + a*b), a*a + d*d - b*b - c*c]])


if __name__ == '__main__':

    import nibabel as nib    
    
    dname = '/usr/share/fsl/data/standard/'
    fname = dname + 'FMRIB58_FA_1mm.nii.gz'

    #dname = '/home/eg309/Data/111104/subj_05/'
    #fname = dname + '101_32/DTI/fa.nii.gz'
 
    img=nib.load(fname)
    data = img.get_data()
    affine = img.get_affine()
    data[np.isnan(data)] = 0

    data = np.interp(data, [data.min(), data.max()], [0, 255])
    data = data.astype(np.ubyte)
    #data = np.ones((156, 122, 96), dtype=np.ubyte)
    #data = 255*data
    #data[70:100, 70:90, 70:80 ] = 140
    window = Window(caption="Interactive Slicer", 
                        bgcolor=(0.4, 0.4, 0.9))
    scene = Scene(activate_aabb=False)

    from nibabel.orientations import aff2axcodes

    np.set_printoptions(2, suppress = True)
    if aff2axcodes(affine) == ('L', 'A', 'S'):
        print affine
        las2ras = np.eye(4)
        las2ras[0, 0] = -1
        affine[:3, 3] = 0
        print affine
        affine = np.dot(las2ras, affine)
        print affine
        #affine[0, 0] = 1
        #affine[1, 1] = 1
        #affine[2, 2] = 1
        #affine[:3, 3] = - np.array([27.5, 48., 48.]) * 2.5 
        affine[:3, 3] = - (np.array(data.shape[:3][::-1]) / 2.) * np.diag(affine)[:3][::-1]
        print affine
        #affine[0, 3] += 2.5
        #print affine
        #assert aff2axcodes(affine) == ('R', 'A', 'S')
        A = np.eye(4)
        A[:3, :3] = rotation_matrix(np.array([1, 0., 0.]), -90)
        B = np.eye(4)
        B[:3, :3] = rotation_matrix(np.array([0, 0, 1.]), -90)
        affine = np.dot(B, np.dot(A, affine))
        print affine

    from fos.actor.axes import Axes
    slicer = Slicer('VolumeSlicer', data, affine=None)
    scene.add_actor(slicer)
    #scene.add_actor(Axes('GL Axes', 200))
    window.add_scene(scene)
    window.refocus_camera()
    
    #ax = Axes(name="3 axes", scale=200, linewidth=10.0)
    #scene.add_actor(ax)
    



    

