import sys
from fos import *
from pyglet.lib import load_library
glib=load_library('GL')
from PySide.QtGui import QApplication
from PySide import QtCore, QtGui, QtOpenGL
from ctypes import *
from fos.actor import Actor

class Line(Actor):
    ''' Lines, curves, tracks actor

    '''

    def __init__(self,name,tracks,colors=None, line_width=2.,affine=None):
	
        super(Line, self).__init__(name)
        #if affine==None:
        #   self.affine=np.eye(4)
	#else: self.affine=affine
	self.tracks_no=len(tracks)
	self.tracks_len=[len(t) for t in tracks]
	self.tracks=tracks
        self.vertices = np.ascontiguousarray(np.concatenate(self.tracks).astype('f4'))        
	if colors==None:
        	self.colors = np.ascontiguousarray(np.ones((len(self.vertices),4)).astype('f4'))
	else:		
        	self.colors = np.ascontiguousarray(colors.astype('f4'))	
        self.vptr=self.vertices.ctypes.data
        self.cptr=self.colors.ctypes.data        
        self.count=np.array(self.tracks_len, dtype=np.int32)
        self.first=np.r_[0,np.cumsum(self.count)[:-1]].astype(np.int32)
        self.firstptr=self.first.ctypes.data
        self.countptr=self.count.ctypes.data
        #print self.firstptr
        #print self.countptr
        #self.firstptr=pointer(c_int(self.firstptr))
        #self.countptr=pointer(c_int(self.countptr))
        self.line_width=line_width
        self.items=self.tracks_no
        mn=self.vertices.min()
	mx=self.vertices.max()
    
    #def update(self, dt):
    #    pass

    def pick(self, x,y):
        print x,y

    def draw(self):
	
	glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)        
	glEnable(GL_LINE_SMOOTH)
	glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)	
        glLineWidth(self.line_width)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3,GL_FLOAT,0,self.vptr)
        glColorPointer(4,GL_FLOAT,0,self.cptr)
        glPushMatrix()
        glib.glMultiDrawArrays(GL_LINE_STRIP,\
                self.firstptr, \
                self.countptr, \
                self.items)
        glPopMatrix()
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)      
        glLineWidth(1.)
	glDisable(GL_LINE_SMOOTH)
	glDisable(GL_BLEND)
	glDisable(GL_DEPTH_TEST)




if __name__ == '__main__':    

    #"""
    tracks=[100*np.random.rand(100,3),100*np.random.rand(20,3)]
    colors=np.ones((120,4))
    colors[0:100,:3]=np.array([1,0,0.])
    colors[100:120,:3]=np.array([0,1,0])

    import nibabel as nib
    from os import path as op
    a=nib.trackvis.read( op.join(op.dirname(__file__),\
            "data",\
            "tracks300.trk") )
    g=np.array(a[0], dtype=np.object)
    tracks = [tr[0] for tr in a[0]]
    #tracks = tracks-np.concatenate(tracks,axis=0)
    lentra = [len(t) for t in tracks]
    colors = np.random.rand(np.sum(lentra),4)
    #colors[:,3]=0.9
    #"""

    streamlines = Line('fornix',tracks,colors,line_width=2)
    from fos.actor.axes import Axes
    from fos.actor.text import Text3D

    title='Bundle Picker'
    w = Window(caption = title, 
                width = 1200, 
                height = 800, 
                bgcolor = (0.,0.,0.2) )
    region = Region( regionname = 'Main',
                        extent_min = np.array([-5.0, -5, -5]),
                        extent_max = np.array([5, 5 ,5]))
    
    ax = Axes(name = "3 axes", linewidth=2.0)

    vert = np.array( [[2.0,3.0,0.0]], dtype = np.float32 )
    ptr = np.array( [[.2,.2,.2]], dtype = np.float32 )
    tex = Text3D( "Text3D", vert, "Reg", 10, 2, ptr)

    region.add_actor(ax)
    region.add_actor(tex)
    region.add_actor(streamlines)
    #w.screenshot( 'red.png' )
    w.add_region(region)
    w.refocus_camera()


