import numpy as np
from fos import Actor, Scene, Window
from fos.actor.tex3d import Texture3D
from pyglet.gl import *
from fos.coords import (img_to_ras_coords_container, 
                        ras_to_las_coords,
                        img_to_tex_coords)


class Slicer(Actor):
    def __init__(self, name, data, affine):
        """ Volume Slicer

        Parameters
        ----------
        name : str
        data : array, (X, Y, Z) or (X, Y, Z, 3) or (X, Y, Z, 4)
        affine : array, shape (4, 4)

        """

        self.name = name
        self.data = data
        self.affine = affine 
        self.tex = Texture3D('Buzz', self.data, self.affine, interp='linear')
        self.vertices = self.tex.vertices
        self.visible = True
        self.I, self.J, self.K = self.data.shape[:3]
        self.i, self.j, self.k = self.I/2, self.J/2, self.K/2
        centershift = img_to_ras_coords_container(
                        np.array([[self.I/2., self.J/2., self.K/2.]]), 
                        data.shape, 
                        affine)
        self.centershift = ras_to_las_coords(centershift)
        self.texcoords_i, self.vertcoords_i = self.slicecoords_i()
        self.texcoords_j, self.vertcoords_j = self.slicecoords_j()
        self.texcoords_k, self.vertcoords_k = self.slicecoords_k()
        self.show_i = True
        self.show_j = True
        self.show_k = True

    def img_to_tex_vert_coords(self, imgcoords):
        vertcoords = img_to_ras_coords_container(imgcoords, 
                                                self.data.shape, 
                                                self.affine)
        vertcoords = ras_to_las_coords(vertcoords)
        texcoords = img_to_tex_coords(imgcoords, self.data.shape)

        vertcoords = vertcoords - self.centershift
        return texcoords, vertcoords

    def slicecoords_i(self):
        imgcoords = np.array([[self.i, 0, 0], 
                              [self.i, 0, self.K], 
                              [self.i, self.J, self.K], 
                              [self.i, self.J, 0]], dtype='f8')
        
        texcoords, vertcoords = self.img_to_tex_vert_coords(imgcoords)
        return texcoords, vertcoords

    def slicecoords_j(self):        
        imgcoords = np.array([[0, self.j, 0], 
                              [0, self.j, self.K], 
                              [self.I, self.j, self.K], 
                              [self.I, self.j, 0]], dtype='f8')
        
        texcoords, vertcoords = self.img_to_tex_vert_coords(imgcoords)
        return texcoords, vertcoords

    def slicecoords_k(self):
        imgcoords = np.array([[0, 0, self.k], 
                              [0, self.J, self.k], 
                              [self.I, self.J, self.k], 
                              [self.I, 0, self.k]], dtype='f8')

        texcoords, vertcoords = self.img_to_tex_vert_coords(imgcoords)
        return texcoords, vertcoords 

    def slice_i(self, i):
        self.i = i
        self.texcoords_i, self.vertcoords_i = self.texcoords_i(i)
        self.draw()

    def slice_j(self, j):
        self.j = j
        self.texcoords_j, self.vertcoords_j = self.texcoords_j(j) 
        self.draw()

    def slice_k(self, k):
        self.k = k
        self.texcoords_k, self.vertcoords_k = self.texcoords_k(k)
        self.draw()

    def draw(self):
        
        if self.show_i: 
            glPushMatrix()
            self.tex.update_quad(self.texcoords_i, self.vertcoords_i)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()
        
        if self.show_j:
            glPushMatrix()
            self.tex.update_quad(self.texcoords_j, self.vertcoords_j)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()

        if self.show_k:
            glPushMatrix()
            self.tex.update_quad(self.texcoords_k, self.vertcoords_k)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()
        

if __name__ == '__main__':
    import nibabel as nib
    from fos import Window, Scene, Init, Run
    
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
	
    Init()

    window = Window(caption='[F]OS',bgcolor = (0, 0, 0.6))
    scene = Scene(activate_aabb = False)
    
    sli = Slicer('Volume Slicer', data, affine)

    scene.add_actor(sli)
    window.add_scene(scene)
    window.refocus_camera()

    Run()


