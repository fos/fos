import numpy as np
from fos import Actor, Region, Window
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

        Notes
        ------
        Coordinate Systems
        http://www.grahamwideman.com/gw/brain/orientation/orientterms.htm
        http://www.slicer.org/slicerWiki/index.php/Coordinate_systems
        """

        self.name = name
        self.data = data
        self.affine = affine 
        self.tex = Texture3D('Buzz', self.data, self.affine, 
                                type=GL_RGBA, interp=GL_LINEAR)
        self.vertices = self.tex.vertices
        self.visible = True
        self.I, self.J, self.K = self.data.shape[:3]
        self.i, self.j, self.k = self.I/2, self.J/2, self.K/3
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
            glRotatef(90, 0., 1., 0)
            glRotatef(90, 0., 0., 1.)
            self.tex.update_quad(self.texcoords_i, self.vertcoords_i)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()
        
        #j Slice
        if self.show_j:
            glPushMatrix()
            glRotatef(180, 0., 1., 0) # added for fsl convention
            glRotatef(90, 0., 0., 1.)
            self.tex.update_quad(self.texcoords_j, self.vertcoords_j)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()

        if self.show_k:
            #k Slice
            glPushMatrix()
            glRotatef(90, 1., 0, 0.)
            glRotatef(90, 0., 0., 1)
            glRotatef(180, 1., 0., 0.) # added for fsl
            self.tex.update_quad(self.texcoords_k, self.vertcoords_k)
            self.tex.set_state()
            self.tex.draw()
            self.tex.unset_state()
            glPopMatrix()
        

if __name__ == '__main__':

    import nibabel as nib    
    dname = '/usr/share/fsl/data/standard/'
    fname = dname + 'FMRIB58_FA_1mm.nii.gz'
    img=nib.load(fname)
    data = img.get_data()
    data = np.interp(data, [data.min(), data.max()], [0, 255])
    #data = np.ones((156, 122, 96), dtype=np.ubyte)
    #data = 255*data
    #data[70:100, 70:90, 70:80 ] = 140
    window = Window(caption="Interactive Slicer", 
                        bgcolor=(0.4, 0.4, 0.9))
    region = Region(activate_aabb=False)
    slicer = Slicer('VolumeSlicer', data)
    region.add_actor(slicer)
    window.add_region(region)
    window.refocus_camera()
    
    #ax = Axes(name="3 axes", scale=200, linewidth=10.0)
    #region.add_actor(ax)
    



    

