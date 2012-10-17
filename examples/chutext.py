import sys
import numpy as np
from fos.actor.chutext import ChuText3D
from fos import *
import string
import random


w = Window( bgcolor = (0,0,0) )

region = Region( regionname = "Main",
                 extent_min = np.array( [-5.0, -5, -5] ),
                 extent_max = np.array( [5, 5, 5] ) )





#number = 10
#vert = np.zeros((number,3),dtype = np.float32)
#fontcolor = np.zeros((number,3), dtype=np.float)
#
#radius = 5
#for i in np.arange(number):
#    angle_x = np.random.rand()*360
#    angle_y = np.random.rand()*360
#    angle_z = np.random.rand()*360
#    vert[i] = [np.sin(angle_x)*radius,np.sin(angle_y)*radius,np.sin(angle_z)*radius]
#
#for  i in np.arange(number):
#    fontcolor[i] = [np.random.rand(),np.random.rand(),np.random.rand()]
    
'''
chu = []
for  i in np.arange(number):
    temp = ''.join( [random.choice(string.letters[:26]) for j in xrange(np.random.randint(3,8))])
    chu.append(temp)
    
chu[5]='BA0'
'''
#chu=[]
#for i in range(100):
    #chu.append('00'+str(i))

#tex = ChuText3D("ChuText3D",number, vert, chu, fontcolor) 

vert = np.array( [[-5.0,0.0,2.0],[5.0,0.0,2.0],
                  [0.0,5.0,5.0],[0.0,-5.0,-3.0],
                  [0.0,3.0,5.0],[0.0,-3.0,5.0]
                ],dtype = np.float32 )
fontcolor = [(0,1,0),(0,1,0),(1,0,0),(1,0,0),(0,0,1),(0,0,1)]

tex = ChuText3D("ChuText3D",6, vert, ["Left", "Right","Superior","Interior","Anterior", "Posterior"],fontcolor)

#, pointercolor)#,ptr)

region.add_actor( Axes( name = "3 axes", linewidth = 2.0) )
region.add_actor( tex )

w.add_region (region)
w.refocus_camera()
