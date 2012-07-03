import numpy as np

def normals_from_vertices_faces(vertices,faces):
    ''' Given vertices, faces generate normals using the cross product
    
    Parameters
    -----------
    vertices: array, shape (N,3), float32
    faces: array, shape (M,3), uint32
    
    Returns
    --------
    normals: array, shape (N,3), float32
    
    '''
    
    normals=np.zeros((len(vertices),3))
    trinormals=np.cross(vertices[faces[:,0]]-vertices[faces[:,1]],\
                                vertices[faces[:,1]]-vertices[faces[:,2]],\
                                axisa=1,axisb=1)
    for (i,face) in enumerate(faces):
        normals[face]+=trinormals[i]            
        
    div=np.sqrt(np.sum(normals**2,axis=1))     
    div=div.reshape(len(div),1)
    normals=(normals/div)
            
    return normals.astype(np.float32)
