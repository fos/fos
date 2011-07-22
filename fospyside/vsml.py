# A port of VSML
# http://www.lighthouse3d.com/very-simple-libs/vsml/vsml-in-action/
# to support matrix operations

# Singleton class from
# http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern

# also see http://sourceforge.net/projects/libmymath/files/libmymath%20v1.3.1/

from fos.lib.pyglet.gl import *
import numpy as np
from ctypes import *

DEBUG = False

def normalize(vectarr):
    return vectarr / np.linalg.norm( vectarr )


class VSML(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VSML, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    class MatrixTypes(object):
        MODELVIEW = 0
        PROJECTION = 1

    def __init__(self):
        self.projection = np.eye(4)
        self.modelview = np.eye(4)

        # setting up the stacks
        self.mMatrixStack = {}

        # use list as stack
        self.mMatrixStack[self.MatrixTypes.MODELVIEW] = []
        self.mMatrixStack[self.MatrixTypes.PROJECTION] = []

    def loadIdentity(self, aType):
        """
        /** Similar to glLoadIdentity.
          *
          * \param aType either MODELVIEW or PROJECTION
        */
        void loadIdentity(MatrixTypes aType);
        """
        if aType == self.MatrixTypes.PROJECTION:
            self.projection = np.eye(4, dtype = np.float32 )
        elif aType == self.MatrixTypes.MODELVIEW:
            self.modelview = np.eye(4, dtype = np.float32 )
        else:
            print "pushMatrix: wrong matrix type"

    def pushMatrix(self, aType):
        """
        /** Similar to glPushMatrix
          *
          * \param aType either MODELVIEW or PROJECTION
        */
        void pushMatrix(MatrixTypes aType);
        """
        # todo: do we need copy?
        if aType == self.MatrixTypes.PROJECTION:
            self.mMatrixStack[aType].append(self.projection.copy())
        elif aType == self.MatrixTypes.MODELVIEW:
            self.mMatrixStack[aType].append(self.modelview.copy() )
        else:
            print "pushMatrix: wrong matrix type"

    def popMatrix(self, aType):
        """
        /** Similar to glPopMatrix
          *
          * \param aType either MODELVIEW or PROJECTION
        */
        void popMatrix(MatrixTypes aType);
        """
        if aType == self.MatrixTypes.PROJECTION:
            self.projection = self.mMatrixStack[aType].pop()
        elif aType == self.MatrixTypes.MODELVIEW:
            self.modelview = self.mMatrixStack[aType].pop()
        else:
            print "popMatrix: wrong matrix type"

    def multMatrix(self, aType, aMatrix):
        """
        /** Similar to glMultMatrix.
          *
          * \param aType either MODELVIEW or PROJECTION
          * \param aMatrix matrix in column major order data, float[16]
        */
        void multMatrix(MatrixTypes aType, float *aMatrix);
        """
        if DEBUG:
            print "multiply matrix"
        if aType == self.MatrixTypes.PROJECTION:
            if DEBUG:
                print "projection was", self.projection
            self.projection = np.dot(self.projection, aMatrix)
            if DEBUG:
                print "projection is", self.projection
        elif aType == self.MatrixTypes.MODELVIEW:
            if DEBUG:
                print "modelview was", self.modelview
            self.modelview = np.dot(self.modelview, aMatrix)
            if DEBUG:
                print "modelview is", self.modelview
        else:
            print "multMatrix: wrong matrix type"

    def get_modelview_matrix(self, array_type=c_float, glGetMethod=glGetFloatv):
        """Returns the built-in modelview matrix."""
        m = (array_type*16)()
        glGetMethod(GL_MODELVIEW_MATRIX, m)
        return np.array( m )

    def get_projection_matrix(self, array_type=c_float, glGetMethod=glGetFloatv):
        """Returns the current modelview matrix."""
        m = (array_type*16)()
        glGetMethod(GL_PROJECTION_MATRIX, m)
        return np.array( m )

    def get_viewport(self):
        """
        Returns the current viewport.
        """
        m = (c_int*4)()
        glGetIntegerv(GL_VIEWPORT, m)
        return np.array( m )

    def get_projection(self):
        return (c_float*16)(*self.projection.T.ravel().tolist())

    def get_modelview(self):
        return (c_float*16)(*self.modelview.T.ravel().tolist())

    def initUniformLocs(sefl, modelviewLoc, projLoc):
        """
        /** Call this function to init the library for a particular
          * program shader if using uniform variables
          *
          * \param modelviewLoc location of the uniform variable
          * for the modelview matrix
          *
          * \param projLoc location of the uniform variable
          * for the projection matrix
        */
        void initUniformLocs(GLuint modelviewLoc, GLuint projLoc);
        """
        pass

    def initUniformBlock(self, buf, modelviewOffset, projOffset):
        """
        /** Call this function to init the library for a particular
          * program shader if using uniform blocks
          *
          * \param buffer index of the uniform buffer
          * \param modelviewOffset offset within the buffer of
          * the modelview matrix
          * \param projOffset offset within the buffer of
          * the projection matrix
        */
        void initUniformBlock(GLuint buffer, GLuint modelviewOffset, GLuint projOffset);
        """
        pass

    def translate(self, x, y, z, aType = MatrixTypes.MODELVIEW ):
        """
        /** Similar to glTranslate*. Applied to MODELVIEW only.
          *
          * \param x,y,z vector to perform the translation
        */
        void translate(float x, float y, float z);
        """
        mat = np.eye(4, dtype = np.float32 )
        mat[0,3] = x
        mat[1,3] = y
        mat[2,3] = z

        if aType == self.MatrixTypes.MODELVIEW:
            self.multMatrix(self.MatrixTypes.MODELVIEW, mat)
        elif aType == self.MatrixTypes.PROJECTION:
            self.multMatrix(self.MatrixTypes.PROJECTION, mat)

    def scale(self, x, y, z, aType = MatrixTypes.MODELVIEW ):
        """
        /** Similar to glScale*. Can be applied to both MODELVIEW
          * and PROJECTION matrices.
          *
          * \param aType either MODELVIEW or PROJECTION
          * \param x,y,z scale factors
        */
        void scale(MatrixTypes aType, float x, float y, float z);
        """
        mat = np.zeros( (4,4), dtype = np.float32)

        mat[0,0] = x
        mat[2,2] = y
        mat[3,3] = z

        if aType == self.MatrixTypes.MODELVIEW:
            self.multMatrix(self.MatrixTypes.MODELVIEW, mat)
        elif aType == self.MatrixTypes.PROJECTION:
            self.multMatrix(self.MatrixTypes.PROJECTION, mat)


    def rotate(self, angle, x, y, z, aType = MatrixTypes.MODELVIEW ):
        """
        /** Similar to glRotate*. Can be applied to both MODELVIEW
          * and PROJECTION matrices.
          *
          * \param aType either MODELVIEW or PROJECTION
          * \param angle rotation angle in degrees
          * \param x,y,z rotation axis in degrees
        */
        void rotate(MatrixTypes aType, float angle, float x, float y, float z);
        """
        mat = np.zeros( (4,4), dtype = np.float32)

        radAngle = np.deg2rad(angle)
        co = np.cos(radAngle)
        si = np.sin(radAngle)
        x2 = x*x
        y2 = y*y
        z2 = z*z

        mat[0,0] = x2 + (y2 + z2) * co
        mat[0,1] = x * y * (1 - co) - z * si
        mat[0,2] = x * z * (1 - co) + y * si
        mat[0,3]= 0.0

        mat[1,0] = x * y * (1 - co) + z * si
        mat[1,1] = y2 + (x2 + z2) * co
        mat[1,2] = y * z * (1 - co) - x * si
        mat[1,3]= 0.0

        mat[2,0] = x * z * (1 - co) - y * si
        mat[2,1] = y * z * (1 - co) + x * si
        mat[2,2]= z2 + (x2 + y2) * co
        mat[2,3]= 0.0

        mat[3,0] = 0.0
        mat[3,1] = 0.0
        mat[3,2]= 0.0
        mat[3,3]= 1.0

        if aType == self.MatrixTypes.MODELVIEW:
            self.multMatrix(self.MatrixTypes.MODELVIEW, mat)
        elif aType == self.MatrixTypes.PROJECTION:
            self.multMatrix(self.MatrixTypes.PROJECTION, mat)


    def loadMatrix(self, aType, aMatrix):
        """
        /** Similar to gLoadMatrix.
          *
          * \param aType either MODELVIEW or PROJECTION
          * \param aMatrix matrix in column major order data, float[16]
        */
        void loadMatrix(MatrixTypes aType, float *aMatrix);
        """
        pass


    def lookAt(self, xPos, yPos, zPos, xLook, yLook, zLook, xUp, yUp, zUp):
        """
        /** Similar to gluLookAt
          *
          * \param xPos, yPos, zPos camera position
          * \param xLook, yLook, zLook point to aim the camera at
          * \param xUp, yUp, zUp camera's up vector
        */
        void lookAt(float xPos, float yPos, float zPos,
                    float xLook, float yLook, float zLook,
                    float xUp, float yUp, float zUp);
        """

        dir = np.array( [xLook - xPos, yLook - yPos, zLook - zPos], dtype = np.float32)
        dir = normalize(dir)

        up = np.array( [xUp, yUp, zUp], dtype = np.float32 )

        right = np.cross(dir, up)
        right = normalize(right)

        up = np.cross(right,dir)
        up = normalize(up)

        # build the matrix
        out = np.zeros( (4,4), dtype = np.float32 )
        out[0,:3] = right
        out[1,:3] = up
        out[2,:3] = -dir

        out[0,3] = -xPos
        out[1,3] = -yPos
        out[2,3] = -zPos
        out[3,3] = 1.0

        # mulitply on the matrix stack
        # self.modelview = np.dot(out, self.modelview)
        # self.modelview = out
        self.multMatrix(self.MatrixTypes.MODELVIEW, out)

        if DEBUG:
            print "lookat: modelview vsml", np.array( vsml.get_modelview() )
        #print "modelview orig", self.get_modelview_matrix()

        # self.modelview = gletools.Mat4(*out.T.ravel().tolist())
    

    def perspective(self, fov, ratio, nearp, farp):
        """
        /** Similar to gluPerspective
          *
          * \param fov vertical field of view
          * \param ratio aspect ratio of the viewport or window
          * \param nearp,farp distance to the near and far planes
        */
        void perspective(float fov, float ratio, float nearp, float farp);
        """
        out = np.eye( 4, dtype = np.float32 )

        f = 1.0 / np.tan (fov * (np.pi / 360.0) )

        out[0,0] = f / ratio
        out[1,1] = f
        out[2,2] = (farp + nearp) / (nearp - farp)
        out[2,3] = (2.0 * farp * nearp) / (nearp - farp)
        out[3,2] = -1.0
        out[3,3] = 0.0

        self.multMatrix(self.MatrixTypes.PROJECTION, out)
        
        if DEBUG:
            print "perspective: new projection vsml", self.projection, np.array( vsml.get_projection() )
    
    def ortho(self, left, right, bottom, top, nearp=-1.0, farp=1.0):
        """
        /** Similar to glOrtho and gluOrtho2D (just leave the last two params blank).
          *
          * \param left,right coordinates for the left and right vertical clipping planes
          * \param bottom,top coordinates for the bottom and top horizontal clipping planes
          * \param nearp,farp distance to the near and far planes
        */
        void ortho(float left, float right, float bottom, float top, float nearp=-1.0f, float farp=1.0f);
        """
        mat = np.eye( 4, dtype = np.float32 )

        mat[0,0] = 2 / (right - left)
        mat[1,1] = 2 / (top - bottom)
        mat[2,2] = -2 / (farp - nearp)
        mat[0,3] = -(right + left) / (right - left)
        mat[1,3] = -(top + bottom) / (top - bottom)
        mat[2,3] = -(farp + nearp) / (farp - nearp)

        self.multMatrix(self.MatrixTypes.PROJECTION, mat)


    def frustum(self, left, right, bottom, top, nearp, farp):
        """
        /** Similar to glFrustum
          *
          * \param left,right coordinates for the left and right vertical clipping planes
          * \param bottom,top coordinates for the bottom and top horizontal clipping planes
          * \param nearp,farp distance to the near and far planes
        */
        void frustum(float left, float right, float bottom, float top, float nearp, float farp);
        """
        mat = np.eye( 4, dtype = np.float32 )

        mat[0,0] = 2 * nearp / (right-left)
        mat[1,1] = 2 * nearp / (top - bottom)
        mat[0,2] = (right + left) / (right - left)
        mat[1,2] = (top + bottom) / (top - bottom)
        mat[2,2] = - (farp + nearp) / (farp - nearp)
        mat[3,2] = -1.0
        mat[2,3] = - 2 * farp * nearp / (farp-nearp)
        mat[3,3] = 0.0

        self.multMatrix(self.MatrixTypes.PROJECTION, mat)


    def matrixToBuffer(self, aType):
        """
        /** Updates the uniform buffer data
          *
          * \param aType  either MODELVIEW or PROJECTION
        */
        void matrixToBuffer(MatrixTypes aType);
        """
        pass

    def matrixToUniform(self, aType):
        """
        /** Updates the uniform variables
          *
          * \param aType  either MODELVIEW or PROJECTION
        */
        void matrixToUniform(MatrixTypes aType);
        """
        pass

    def matrixToGL(self, aType):
        """
        /** Updates either the buffer or the uniform variables
          * based on which init* function was called last
          *
          * \param aType  either MODELVIEW or PROJECTION
        */
        void matrixToGL(MatrixTypes aType);
        """
        pass

    # protected:

    #    /// Has an init* function been called?
    #    bool mInit;
    mInit = False

    #    /// Using uniform blocks?
    #    bool mBlocks;
    mBlocks = False

    #    ///brief Matrix stacks for modelview and projection matrices
    #    std::vector<float *> mMatrixStack[2];
    # mMatrixStack = []

    #    /// Storage for the uniform locations
    #    GLuint mUniformLoc[2];
    mUniformLoc = []

    #    /// Storage for the buffer index
    #    GLuint mBuffer;
    mBuffer = None

    #    /// Storage for the offsets within the buffer
    #    GLuint mOffset[2];
    mOffset = []


# the global vsml instance
vsml = VSML()
