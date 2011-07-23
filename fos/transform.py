import numpy as np

# http://download.oracle.com/docs/cd/E17802_01/j2se/javase/technologies/desktop/java3d/forDevelopers/J3D_1_3_API/j3dapi/javax/media/j3d/Transform3D.html

class Transform3D(object):
    """ A 3D transformation with rotation, scale, shear and translation
    Can return different types of objects with the transformation.
    Uses underlying NumPy array
    """
    def __init__(self):
        pass


class IdentityTranform(Transform3D):

    def __init__(self):
        super(IdentityTranform, self).__init__()
        self.matrix = np.eye(4)