''' A type of -*- python -*- file

Collision detection utilities for Fos


'''
# cython: profile=True
# cython: embedsignature=True

cimport cython

import numpy as np
import time
cimport numpy as cnp


cdef extern from "math.h" nogil:
    double floor(double x)
    float sqrt(float x)
    float fabs(float x)
    double log2(double x)
    float acos(float x )    
    bint isnan(double x) 
    
#cdef extern from "stdio.h":
#	void printf ( const char * format, ... )
    
cdef extern from "stdlib.h" nogil:
    ctypedef unsigned long size_t
    void free(void *ptr)
    void *malloc(size_t size)
    void *calloc(size_t nelem, size_t elsize)
    void *realloc (void *ptr, size_t size)
    void *memcpy(void *str1, void *str2, size_t n)

#@cython.boundscheck(False)
#@cython.wraparound(False)


cdef inline cnp.ndarray[cnp.float32_t, ndim=1] as_float_3vec(object vec):
    ''' Utility function to convert object to 3D float vector '''
    return np.squeeze(np.asarray(vec, dtype=np.float32))


cdef inline float* asfp(cnp.ndarray pt):
    return <float *>pt.data


def normalized_3vec(vec):
    ''' Return normalized 3D vector

    Vector divided by Euclidean (L2) norm

    Parameters
    ----------
    vec : array-like shape (3,)

    Returns
    -------
    vec_out : array shape (3,)
    '''
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_in = as_float_3vec(vec)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_out = np.zeros((3,), np.float32)
    cnormalized_3vec(<float *>vec_in.data, <float*>vec_out.data)
    return vec_out


def norm_3vec(vec):
    ''' Euclidean (L2) norm of length 3 vector

    Parameters
    ----------
    vec : array-like shape (3,)

    Returns
    -------
    norm : float
       Euclidean norm
    '''
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_in = as_float_3vec(vec)
    return cnorm_3vec(<float *>vec_in.data)


cdef inline float cnorm_3vec(float *vec):
    ''' Calculate Euclidean norm of input vector

    Parameters
    ----------
    vec : float *
       length 3 float vector

    Returns
    -------
    norm : float
       Euclidean norm
    '''
    cdef float v0, v1, v2
    v0 = vec[0]
    v1 = vec[1]
    v2 = vec[2]
    return sqrt(v0 * v0 + v1*v1 + v2*v2)


cdef inline void cnormalized_3vec(float *vec_in, float *vec_out):
    ''' Calculate and fill normalized 3D vector 

    Parameters
    ----------
    vec_in : float *
       Length 3 vector to normalize
    vec_out : float *
       Memory into which to write normalized length 3 vector

    Returns
    -------
    void
    '''
    cdef float norm = cnorm_3vec(vec_in)
    cdef int i
    for i in range(3):
        vec_out[i] = vec_in[i] / norm
        

def inner_3vecs(vec1, vec2):
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec1 = as_float_3vec(vec1)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec2 = as_float_3vec(vec2)
    return cinner_3vecs(<float *>fvec1.data, <float*>fvec2.data)


cdef inline float cinner_3vecs(float *vec1, float *vec2):
    cdef int i
    cdef float ip = 0
    for i in range(3):
        ip += vec1[i]*vec2[i]
    return ip


def sub_3vecs(vec1, vec2):
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec1 = as_float_3vec(vec1)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec2 = as_float_3vec(vec2)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_out = np.zeros((3,), np.float32)    
    csub_3vecs(<float *>fvec1.data, <float*>fvec2.data, <float *>vec_out.data)
    return vec_out


cdef inline void csub_3vecs(float *vec1, float *vec2, float *vec_out):
    cdef int i
    for i in range(3):
        vec_out[i] = vec1[i]-vec2[i]


def add_3vecs(vec1, vec2):
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec1 = as_float_3vec(vec1)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec2 = as_float_3vec(vec2)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_out = np.zeros((3,), np.float32)    
    cadd_3vecs(<float *>fvec1.data, <float*>fvec2.data, <float *>vec_out.data)
    return vec_out


cdef inline void cadd_3vecs(float *vec1, float *vec2, float *vec_out):
    cdef int i
    for i in range(3):
        vec_out[i] = vec1[i]+vec2[i]

def mul_3vecs(vec1, vec2):
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec1 = as_float_3vec(vec1)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec2 = as_float_3vec(vec2)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_out = np.zeros((3,), np.float32)    
    cmul_3vecs(<float *>fvec1.data, <float*>fvec2.data, <float *>vec_out.data)
    return vec_out

cdef inline void cmul_3vecs(float *vec1, float *vec2, float *vec_out):
    cdef int i
    for i in range(3):
        vec_out[i] = vec1[i]*vec2[i]

def mul_3vec(a, vec):
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec = as_float_3vec(vec)    
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_out = np.zeros((3,), np.float32)    
    cmul_3vec(a,<float *>fvec.data, <float *>vec_out.data)
    return vec_out        

cdef inline void cmul_3vec(float a, float *vec, float *vec_out):
    cdef int i
    for i in range(3):
        vec_out[i] = a*vec[i]
        
def div_3vec(a, vec):
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fvec = as_float_3vec(vec)    
    cdef cnp.ndarray[cnp.float32_t, ndim=1] vec_out = np.zeros((3,), np.float32)    
    cdiv_3vec(a,<float *>fvec.data, <float *>vec_out.data)
    return vec_out        

cdef inline void cdiv_3vec(float a, float *vec, float *vec_out):
    cdef int i
    for i in range(3):
        vec_out[i] = vec[i]/a

        

def cross_3vecs(a,b):
    
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fa = as_float_3vec(a)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fb = as_float_3vec(b)    
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fc = np.zeros((3,),np.float32)
    
    ccross_3vecs(<float *>fa.data,<float *>fb.data, <float *>fc.data)

cdef inline void ccross_3vecs(float *a, float *b, float *c):

    cdef int i
    
    c[0] = a[1] * b[2] - b[1] * a[2]
    c[1] = a[2] * b[0] - b[2] * a[0]    
    c[2] = a[0] * b[1] - b[0] * a[1]
    
        

# float 32 dtype for casting
cdef cnp.dtype f32_dt = np.dtype(np.float32)
# int 32
cdef cnp.dtype int_dt = np.dtype(np.int)


DEF biggest_double = 1.79769e+308

DEF EPSILON = 5.96e-08

def intersect_segment_plane(a,b,p1,p2,p3):

    ''' Find intersection point between segment ab and plane defined by
    three points p1,p2,p3. Have in mind that 3 points are sufficient to
    define a plane.

    Parameters:
    ----------
    a: sequence (3,), float
     first point of the segment ab
    b: sequence (3,), float
     second point of the segment ab
    p1: sequence (3,)
     point 1 of plane
    p2: sequence (3,)
     point 2 of plane
    p3: sequence (3,)
     point 3 of plane

    Returns:
    --------
    success: True( there is a hit) or False (nope we missed the plane)   
    
    t: float, at which persentage of the segment intersection took
    place?
    p: sequence (3,), intersection point
    

    Examples:
    ---------

    >>> from fos.core import collision as cll
    >>> cll.intersect_segment_plane([0,0,0],[0,0,1], [2,0,0.5], [0,-2,0.5], [0,0,0.5])

    

    '''
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fa =as_float_3vec(a)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fb =as_float_3vec(b)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp1=as_float_3vec(p1)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp2=as_float_3vec(p2)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp3=as_float_3vec(p3)

    cdef float p[3],t[1],res

    

    res=cintersect_segment_plane(<float *>fa.data,<float *>fb.data,
                             <float *>fp1.data, <float *>fp2.data, <float *>fp3.data,
                                  <float *>t, <float *>p)

    if res==1.:

        return True, t[0],np.array([p[0],p[1],p[2]],np.float32)

    else:

        return False, None, None

cdef inline int cintersect_segment_plane(float *a,float *b, float *p1, float *p2, float *p3, float *t, float *p):


    cdef float n[3]
    cdef float d
    cdef float tmp[3]
    cdef float tmp2[3]
    cdef float ab[3]
    
    #change plane representation to normal n and d form

    csub_3vecs(p2,p1,tmp)
    
    csub_3vecs(p3,p2,tmp2)
    
    ccross_3vecs(tmp,tmp2,n)

    #print(n[0],n[1],n[2])
    
    d=cinner_3vecs(n,p1)    
    
    csub_3vecs(b,a,ab)

    t[0]=(d-cinner_3vecs(n,a))/cinner_3vecs(n,ab)
    
    if t[0]>=0. and t[0]<= 1.:

       cmul_3vec(t[0],ab,tmp)

       cadd_3vecs(a,tmp,p)

       return 1

    return 0     
       

       


def intersect_segment_cylinder(sa,sb,p,q,r):
    '''
    Intersect Segment S(t) = sa +t(sb-sa), 0 <=t<= 1 against cylinder specified by p,q and r    
    
    Look p.197 from Real Time Collision Detection C. Ericson
    
    Examples
    --------
    >>> # Define cylinder using a segment defined by 
    >>> p=np.array([0,0,0],dtype=float32)
    >>> q=np.array([1,0,0],dtype=float32)
    >>> r=0.5
    >>> # Define segment
    >>> sa=np.array([0.5,1 ,0],dtype=float32)
    >>> sb=np.array([0.5,-1,0],dtype=float32)
    >>> from fos.core import performance as pf
    >>> 
    '''
    cdef:
        float *csa,*csb,*cp,*cq
        float cr
        float ct[2]
        
                
    csa = asfp(sa)
    csb = asfp(sb)
    cp = asfp(p)
    cq = asfp(q)
    cr=r
    ct[0]=-100
    ct[1]=-100
    
    tmp= cintersect_segment_cylinder(csa,csb,cp, cq, cr, ct)

    return tmp,ct[0],ct[1]


    
cdef float cintersect_segment_cylinder(float *sa,float *sb,float *p, float *q, float r, float *t):
    ''' Intersect Segment S(t) = sa +t(sb-sa), 0 <=t<= 1 against cylinder specified by p,q and r    
    
    Look p.197 from Real Time Collision Detection C. Ericson
    
    0 no intersection
    1 intersection   
            
    '''
    cdef:
        float d[3],m[3],n[3]
        float md,nd,dd, nn, mn, a, k, c,b, discr
        
        float epsilon_float=5.96e-08
    
    csub_3vecs(q,p,d)
    csub_3vecs(sa,p,m)
    csub_3vecs(sb,sa,n)
    
    md=cinner_3vecs(m,d)
    nd=cinner_3vecs(n,d)
    dd=cinner_3vecs(d,d)
    
    #test if segment fully outside either endcap of cylinder
    if md < 0. and md + nd < 0.:  return 0 #segment outside p side
    
    if md > dd and md + nd > dd:  return 0 #segment outside q side

    nn=cinner_3vecs(n,n)
    mn=cinner_3vecs(m,n)
    
    a=dd*nn-nd*nd
    k=cinner_3vecs(m,m) -r*r
    c=dd*k-md*md

    if fabs(a) < epsilon_float:
        #segment runs parallel to cylinder axis 
        if c>0.:  return 0. # segment lies outside cylinder
        
        if md < 0.: 
            t[0]=-mn/nn # intersect against p endcap
        elif md > dd : 
            t[0]=(nd-mn)/nn # intersect against q endcap
        else: 
            t[0]=0. # lies inside cylinder
        return 1
        
    b=dd*mn -nd*md
    discr=b*b-a*c
    if discr < 0.: return 0. # no real roots ; no intersection
    
    t[0]=(-b-sqrt(discr))/a
    t[1]=(-b+sqrt(discr))/a
    if t[0]<0. or t[0] > 1. : return 0. # intersection lies outside segment
    
    if md + t[0]* nd < 0.:
        #intersection outside cylinder on 'p' side
        if nd <= 0. : return 0. # segment pointing away from endcap
        
        t[0]=-md/nd
        #keep intersection if Dot(S(t)-p,S(t)-p) <= r^2
        if k+2*t[0]*(mn+t[0]*nn) <=0.:
            return 1.
    
    elif md+t[0]*nd > dd :
        #intersection outside cylinder on 'q' side
        if nd >= 0.: return 0. # segment pointing away from endcap
        t[0]= (dd-md)/nd
        #keep intersection if Dot(S(t)-q,S(t)-q) <= r^2
        if k+dd-2*md+t[0]*(2*(mn-nd)+t[0]*nn) <= 0.:
            return 1.
    
    # segment intersects cylinder between the endcaps; t is correct
    return 1.
    

def point_segment_sq_distance(a,b,c):
    ''' Calculate the squared distance from a point c to a finite line segment ab.
 
    Examples
    --------
    >>> from fos.core import collision as cll
    >>> a=np.array([0,0,0],dtype=float32)
    >>> b=np.array([1,0,0],dtype=float32)
    >>> c=np.array([0,1,0],dtype=float32)    
    >>> cll.point_segment_sq_distance(a,b,c)
    >>> 1.0
    >>> c=np.array([0,3,0],dtype=float32)
    >>> cll.point_segment_sq_distance(a,b,c)
    >>> 9.0 
    >>> c=np.array([-1,1,0],dtype=float32)
    >>> cll.point_segment_sq_distance(a,b,c)
    >>> 2.0
    

    '''
    cdef:
        float *ca,*cb,*cc
        float cr
        float ct[2]
        
                
    ca = asfp(a)
    cb = asfp(b)
    cc = asfp(c)
    
    return cpoint_segment_sq_dist(ca, cb, cc)
    
cdef inline float cpoint_segment_sq_dist(float * a, float * b, float * c):
    ''' Calculate the squared distance from a point c to a line segment ab.
    
    '''
    cdef:
        float ab[3],ac[3],bc[3]
        float e,f

    csub_3vecs(b,a,ab)
    csub_3vecs(c,a,ac)
    csub_3vecs(c,b,bc)
    
    e = cinner_3vecs(ac, ab)
    #Handle cases where c projects outside ab
    if e <= 0.:  return cinner_3vecs(ac, ac)
    f = cinner_3vecs(ab, ab)
    if e >= f : return cinner_3vecs(bc, bc)
    #Handle case where c projects onto ab
    return cinner_3vecs(ac, ac) - e * e / f

    



def closest_points_2segments(p1,q1, p2, q2):
    
    ''' Computes closest points C1 and C2 of S1(s)=P1+s*(Q1-P1) and
    S2(t)=P2+t*(Q2-P2), returning s and t. Function result is squared
    distance between between S1(s) and S2(t)

    '''

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp1 = as_float_3vec(p1)

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fq1 = as_float_3vec(q1)

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp2 = as_float_3vec(p2)

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fq2 = as_float_3vec(q2)    

    cdef float fs[1]

    cdef float ft[1]

    cdef float d

    d=cclosest_points_2segments(<float *> fp1.data, <float *>fq1.data, <float *> fp2.data, <float *>fq2.data,  fs, ft)

        
    return d, fs[0], ft[0]



cdef float cclosest_points_2segments(float* p1, float *q1, float *p2, float *q2,
                              float *ss, float *tt):

    ''' Computes closest points C1 and C2 of S1(s)=P1+s*(Q1-P1) and
    S2(t)=P2+t*(Q2-P2), returning s and t. Function result is squared
    distance between between S1(s) and S2(t). Look page 147 of Real Time
    Collision Detection by Christer Ericson for some ideas of how we
    implemented this.

    Returns:
    --------
    distance: float,
     >0 squared distance,
     -1 parallel segments,   
     -3 both segments degenerate to points
     -4 first segment degenerates to point
     -5 second segment degenerates to point    

    '''

        
    #Vector d1 = q1 - p1; // Direction vector of segment S1

    cdef float d1[3]

    d1[0]=q1[0]-p1[0]
    d1[1]=q1[1]-p1[1]
    d1[2]=q1[2]-p1[2]
    
    #Vector d2 = q2 - p2; // Direction vector of segment S2

    cdef float d2[3]

    d2[0]=q2[0]-p2[0]
    d2[1]=q2[1]-p2[1]
    d2[2]=q2[2]-p2[2]
    
    #Vector r = p1 - p2; // Interconnecting vector segments S1 S2

    cdef float r[3]

    r[0] = p1[0] - p2[0]
    r[1] = p1[1] - p2[1]
    r[2] = p1[2] - p2[2]

    cdef float u[3]

    u[0] = p2[0] - q1[0]
    u[1] = p2[1] - q1[1]
    u[2] = p2[2] - q1[2]    

    cdef float a,b,c,e,f,s,t,d,tmp,tmp3[3]

    cdef float c1[3],c2[3]

    cdef float d1s[3], d2s[3],c1c2[3]

    
    a=cinner_3vecs(d1,d1)

    b=cinner_3vecs(d1,d2)

    c=cinner_3vecs(d1,r)

    e=cinner_3vecs(d2,d2)

    f=cinner_3vecs(d2,r)

    d=a*e-b*b

    #print('d',d)

    if a<EPSILON and e<EPSILON:
        
        print('Error - Both Segments have infinite small length')
        
        ss[0]=0.

        tt[0]=0.

        return -3

    if a<EPSILON:

        print('Error - First Segment has infinite small length')        

        ss[0]=0.

        tt[0]=0.

        return -4

    if e<EPSILON:

        print('Error - Second Segment has infinite small length')   
        
        ss[0]=0.

        tt[0]=0.

        return -5
        
        

    if d<EPSILON :

        '''
        #use the cross product to check if the two segments are aligned

        ccross_3vecs(r,u,tmp3)
        
        #if the cross product is [0,0,0] +- epsilon then please say

          return -1
      
        '''
                
        print('Error - Segments are parallel')

        ss[0]=0.

        tt[0]=0.   

        return -1                  

    else:

        #print('Segments not parallel')

        s=(b*f-c*e)/d

        t=(a*f-b*c)/d

    if s < 0. : s=0.

    if t < 0. : t=0.

    if s > 1. : s=1.

    if t > 1. : t=1.

    #find c1    
    cmul_3vec(s,d1,d1s)    

    cadd_3vecs(p1,d1s,c1)
    
    #find c2
    cmul_3vec(t,d2,d2s)

    cadd_3vecs(p2,d2s,c2)
    
    #calculate the vector connecting the closest points
    csub_3vecs(c1,c2,c1c2)
    
    ss[0]=s

    tt[0]=t

    return cinner_3vecs(c1c2,c1c2)



def mindistance_segment2track(p1,q1,xyz):
    ''' Return minimum distance between segment and track of
    interconnecting segments
    
    Parameters
    ------------------
    p1: sequence, shape(3,),first point

    p2: sequence, shape(3,),second point
    
    xyz: array(N,3) 
        initial trajectory
    
    Returns
    -------
    md : minimum distance
    
    '''
    cdef :

        cnp.ndarray[cnp.float32_t, ndim=2] track 
        float *fvec0,*fvec1,*fvec2
        object characteristic_points
        size_t t_len
        int index
        float fs[1]
        float ft[1]
        float d
        float min
        

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp1 = as_float_3vec(p1)

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fq1 = as_float_3vec(q1)
    
    track = np.ascontiguousarray(xyz, dtype=f32_dt)

    #cdef cnp.ndarray[cnp.float32_t, ndim=1] distances = np.zeros(len(track),np.float32)
        
    t_len=len(track)
    
    index = 1

    min = 3*10**38
        
    while index < t_len:
        
        
        fvec0 = asfp(track[index-1])
        fvec1 = asfp(track[index])
        
        d=cclosest_points_2segments(<float *> fp1.data, <float *>fq1.data, \
                                         fvec0, fvec1,  fs, ft)

        #distances[index-1]=d

        if d>= 0.:

            if min > d :

                min=d

                
       

        index+=1

    
    #distances
    #return np.array(distances).min()#, np.array(distances).argmin()

    return min


def mindistance_segment2track_info(p1,q1,xyz):
    ''' Return minimum distance between segment and track of
    interconnecting segments
    
    Parameters
    ------------------
    p1: sequence, shape(3,),first point

    p2: sequence, shape(3,),second point
    
    xyz: array(N,3) 
        initial trajectory
    
    Returns
    -------
    md : minimum distance

    ms : how close to the near plane.
    
    '''
    cdef :

        cnp.ndarray[cnp.float32_t, ndim=2] track 
        float *fvec0,*fvec1,*fvec2
        object characteristic_points
        size_t t_len
        int index
        float fs[1]
        float ft[1]
        float d
        float min,mins
        

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fp1 = as_float_3vec(p1)

    cdef cnp.ndarray[cnp.float32_t, ndim=1] fq1 = as_float_3vec(q1)
    
    track = np.ascontiguousarray(xyz, dtype=f32_dt)

    #cdef cnp.ndarray[cnp.float32_t, ndim=1] distances = np.zeros(len(track),np.float32)
        
    t_len=len(track)
    
    index = 1

    min = 3*10**38
        
    while index < t_len:
        
        
        fvec0 = asfp(track[index-1])
        fvec1 = asfp(track[index])
        
        d=cclosest_points_2segments(<float *> fp1.data, <float *>fq1.data, fvec0, fvec1,  fs, ft)

        #distances[index-1]=d

        if d>= 0.:

            if min > d :

                min = d

                mins = fs[0]
       

        index+=1

    
    #distances
    #return np.array(distances).min()#, np.array(distances).argmin()

    return min, mins


def calculate_triangle_normals(vertices,triangles):

    ''' Deprecated - Very slow to be removed or further optimized properly

    '''



    cdef :

        cnp.ndarray[cnp.float32_t, ndim=2] pts

        cnp.ndarray[cnp.int_t, ndim=2] tri

        cnp.ndarray[cnp.float32_t, ndim=2] normals
        
        size_t tri_len

        int i,j

        float c1[3], c2[3], cs[3], p1[3], p2[3], p3[3]

        float normal[3],ncs

        
       
    pts = np.ascontiguousarray(vertices, dtype=f32_dt)

    tri = np.ascontiguousarray(triangles, dtype=int_dt)
    
    normals = np.ascontiguousarray(np.zeros((len(vertices),3),dtype=np.float32), dtype=f32_dt)
    
    tri_len = len(tri)

    t1=time.clock()
   
    for i in range(tri_len):

        for j in range(3):

            p1[j]=pts[tri[i][0]][j]

            p2[j]=pts[tri[i][1]][j]

            p3[j]=pts[tri[i][2]][j]


        csub_3vecs(p1,p2,c1)

        csub_3vecs(p2,p3,c2)

        ccross_3vecs(c1,c2,cs)

        ncs=cnorm_3vec(cs)

        cdiv_3vec(ncs,cs,normal)

        for j in range(3):

            normals[tri[i][0]][j] += normal[j]

            normals[tri[i][1]][j] += normal[j]

            normals[tri[i][2]][j] += normal[j]


    print(time.clock()-t1)    

    Normals=np.array(normals,np.float32)

    div=np.sqrt(np.sum(Normals**2,axis=1))
        
    div=div.reshape(len(div),1)

    print('yo',time.clock()-t1)

    return (Normals/div).astype(np.float32)

        



        

        
