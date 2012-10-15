import numpy as np
from fos import Actor, Region, Window
from fos.actor.tex3d import Texture3D
from fos.actor.axes import Axes
from pyglet.gl import *

class Slicer(Actor):
    def __init__(self, name, data, affine=None):

        self.name = name
        self.data = data
        self.affine = affine 
        self.tex = Texture3D('Buzz', self.data, self.affine, 
                                type=GL_RGBA, interp=GL_LINEAR)
        self.vertices = self.tex.vertices
        self.visible = True
        i, j, k = self.data.shape[:3]
        self.texcoords_i, self.vertcoords_i = self.tex.slice_i(i/2) 
        self.texcoords_j, self.vertcoords_j = self.tex.slice_j(j/2) 
        self.texcoords_k, self.vertcoords_k = self.tex.slice_k(k/2) 
        #tex.update_quad(texcoords, vertcoords)

    def draw(self):
        
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
        glPushMatrix()
        glRotatef(90, 0., 0., 1.)
        self.tex.update_quad(self.texcoords_j, self.vertcoords_j)
        self.tex.set_state()
        self.tex.draw()
        self.tex.unset_state()
        glPopMatrix()

        #k Slice
        glPushMatrix()
        glRotatef(90, 1., 0, 0.)
        glRotatef(90, 0., 0., 1)
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

    window = Window(caption="BuzzTex with Free on Shades", 
                        bgcolor=(0.4, 0.4, 0.9))
    region = Region(activate_aabb=False)

    slicer = Slicer('BuzzTex', data)
    region.add_actor(slicer)
    window.add_region(region)

    
    #ax = Axes(name="3 axes", scale=200, linewidth=10.0)
    #region.add_actor(ax)
    



    

