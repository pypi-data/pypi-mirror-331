import numpy as np
import math
from math import pi,log10
import warnings

SIG_FIGURES = 10
FLOAT_EPS = 1 / (10 ** SIG_FIGURES)
def set_eps(eps = 1e-10):
    global FLOAT_EPS,SIG_FIGURES
    FLOAT_EPS = eps
    SIG_FIGURES = round(log10(1 / eps))

def get_eps():
    global FLOAT_EPS
    return FLOAT_EPS

def get_sig_figures():
    global SIG_FIGURES
    return SIG_FIGURES

def set_sig_figures(sig_figures = 10):
    global FLOAT_EPS,SIG_FIGURES
    SIG_FIGURES = sig_figures
    FLOAT_EPS = 1 / (10 ** SIG_FIGURES)


warnings.simplefilter(action='ignore', category=FutureWarning)

"""
    1) Functions for single arrays each in the form of np.array(N) 
         They are element-based operations
"""

def Round(x):
    return np.round(x, get_sig_figures())

def Round2(v):
    v[np.where(np.abs(v) <= get_eps())]=0
    return v

def Array2Tuple(v):
    return array_to_tuple(v)

def array_to_tuple(array): # two dimensional tuple
    return tuple([tuple(e) for e in Round(array)])

def Array(u):
    return Round(np.asarray(u))

def Matrix(u):
    return Round(np.matrix(u))
    
def Cross(u,v):
    return Round(np.cross(u,v))

def Dot(u,v):
    if max([u.ndim,v.ndim]) > 1 :
        return Round(np.sum(u*v,axis=1))
    else :
        return Round(np.dot(u,v))

def Sqrt(u):
    return np.sqrt(u)


def Mask(u,bSelected):
    """
    It returns an array made of elements selected ( bSelected == True ).
    """
    P = Array(u)
    return P[bSelected]

# To check whether the two vectors are equal.
def AllPositive(u):
    return np.all(Round(u) > get_eps())

def AllZero(u):
    return np.all(Round(np.abs(u))<=get_eps())

def AllNegative(u):
    return np.all(Round(u) < get_eps())

# return Vector(a) == Vector(b) 
def Equal(a,b):
    return np.all(Round(a)==Round(b))


# return aij == bij  
# def ElementEqual(a,b):
#     return ScalarEqual(a,b)

# # return aij == 0 
# def ElementZero(u):
#     return ScalarZero(u)

def ScalarEqual(a,b):
    return Round(abs(a-b))<=get_eps()

def ScalarZero(u):
    return ScalarEqual(u,get_eps())

def AngleBetween(A,B):
    # Angle between two lines
    u,v = Array(A), Array(B)
    a,b = Magnitude(u), Magnitude(v)
    rad = np.arccos( Dot(u,v)/(a*b) )%np.pi
    deg = np.degrees(rad)%180
    return rad, deg

def AngleBetween2(A,B):
    # Angle between two lines
    u,v = Array(A), Array(B)
    a,b = Magnitude(u), Magnitude(v)
    rad = np.arccos( Dot(u,v)/(a*b) )
    deg = np.degrees(rad)
    return rad, deg

"""
    1) Functions for single arrays each in the form of np.array(N) 
         They are element-based operations
"""

"""
    2) Functions for a group of array in the specific form of np.array(N,3) 

          N  rows, 
          3  one row is (x,y,z), a vector
    
       They are array-based operation, and np.operation( rows, axis = 1)

"""
#
#  functions analog to matlab ones
#
def Repmat(M,m,n):          # matlab alternative to broadcasting of Python
    return np.tile(Round(M),(m,n)) 

def MatlabSize(u):
    ret = u.shape
    n = len(u)
    if len(ret) == 1:
        ret = (1,n)
    return ret

def Inv(M):
    return Round(np.linalg.inv(M))

def Det(M):
    return Round(np.linalg.det(M))

#  Magnitude for vector 
def Magnitude(u):
    return Round(np.linalg.norm(u, axis=-1, keepdims=True))


def UnitVector(u): 
    return Round(u/Magnitude(u))   

def Projection(rows, n):
    if rows.ndim == 1 and n.ndim == 1:
        return Dot(rows,n)

    if rows.ndim == 2 and n.ndim==1 :
        m,_ = MatlabSize(rows)
        U = Repmat(n,m,1)
        return np.sum(rows*U,axis=1)

    if rows.ndim == 1 and n.ndim == 2:
        m,_ = MatlabSize(n)
        U = RepMat(rows,m,1)
        return np.sum(U*n,axis=1)

    if rows.shape == n.shape :
        return np.sum(rows*n, axis=1)

    raise ValueError(f" dimension mismatch : ({rows.shape} ~ {n.shape})")

"""
   matrix 
"""

### degree-based triangles
def sind(angle): return np.sin(np.radians(angle))
def cosd(angle): return np.cos(np.radians(angle))
def tand(angle): return np.tan(np.radians(angle))
def arcsind(value): return np.degrees(np.arcsin(value))
def arccosd(value): return np.degrees(np.arccos(value))
def arctand(value): return np.degrees(np.arctan(value))

# Vertices 
# def Vertices(x):
#     return Array(x)

class Vector2D:
    """A two-dimensional vector with Cartesian coordinates."""

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        """Human-readable string representation of the vector."""
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def __repr__(self):
        """Unambiguous string representation of the vector."""
        return repr((self.x, self.y))

    def dot(self, other):
        """The scalar (dot) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector2D):
            raise TypeError('Can only take dot product of two Vector2D objects')
        return self.x * other.x + self.y * other.y
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = dot

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vector2D(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply Vector2D by a scalar')

    def __rmul__(self, scalar):
        """Reflected multiplication so vector * scalar also works."""
        return self.__mul__(scalar)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return Vector2D(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector2D(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        """One way to implement modulus operation: for each component."""
        return Vector2D(self.x % scalar, self.y % scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)

    def to_polar(self):
        """Return the vector's components in polar coordinates."""
        return self.__abs__(), math.atan2(self.y, self.x)

class Vector():
    def __init__(self,*args):
        super().__init__()
        self.x, self.y, self.z = 0,0,0
        self._set_vector(*args)

    def _set_vector(self, *args):
        m = len(args) 
        _class_ = self.__class__

        if m == 0 :
            return

        if m == 1:
            P = args[0]
            if isinstance(P,_class_) :
                self.x, self.y, self.z = P.x, P.y, P.z

            else :
                if len(P)==3 :
                    self.x, self.y, self.z = P[0],P[1],P[2]
                
                elif len(P)==2 :
                    self.x, self.y, self.z = P[0],P[1],0.0
                
                else:
                    name = self.__class__.__name__
                    raise ValueError("{name} needs 2 or 3 values")
        
        else : # 2 or 3 scalar numbers
            self.x,self.y = args[0],args[1]

            if len(args) == 3 :
                self.z = args[2]
            else :
                self.z = 0
        
        
        
    def __str__(self):
        name = self.__class__.__name__
        return f"{name}{self.x,self.y,self.z}"    
    

    # operators 
    def __add__(self, v):
        return self.__class__(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v):
        return self.__class__(self.x - v.x, self.y - v.y, self.z - v.z)

    def __rmul__(self, c):
        return self.__class__(c * self.x, c * self.y, c * self.z)

    def __mul__(self, c):
        return self.__rmul__(c)

    def __getitem__(self, item):
        """return one of x,y,z"""
        return (self.x, self.y, self.z)[item]

    def __setitem__(self, item, value):
        """set one of x,y,z of a Point"""
        setattr(self, "xyz"[item], value)

    def dot(self,v):
        u = self
        return u.x * v.x + u.y * v.y + u.z * v.z
      
    def cross(self, v):
        u = self
        return self.__class__(u.y * v.z - u.z * v.y, u.z * v.x - u.x * v.z, u.x * v.y - u.y * v.x)

    def rotated_by(self,M):  # Matrix * vector
        u = self 
        x = u.x * M[0][0] + u.y * M[0][1] + u.z * M[0][2] 
        y = u.x * M[1][0] + u.y * M[1][1] + u.z * M[1][2] 
        z = u.x * M[2][0] + u.y * M[2][1] + u.z * M[2][2] 
        return self.__class__(x,y,z)
    
    def Magnitude(self):
        x,y,z = self.x, self.y, self.z
        return np.sqrt(x * x + y * y + z * z)

    def unit(self):
        L = self.Magnitude()
        x,y,z = self.x, self.y, self.z
        if L > 0 :
            inv_L = 1/L
            x, y, z = x*inv_L,y*inv_L,z*inv_L
        return Vector(x,y,z) 
    
    def as_list(self):
        return [self.x,self.y,self.z]

    def as_tuple(self):
        return (self.x,self.y,self.z)

    def as_dict(self):
        return {"x":self.x, "y":self.y, "z":self.z}

    def as_array(self):
        return np.array([self.x,self.y,self.z])
    
    #  logical operant : == 
    def __eq__(self, v):
        #return self.x == v.x and self.y == v.y and self.z == v.z
        return isinstance(v, type(self)) and self.equal_to(v)
    
    def equal_to(self, v):
        return self.deviation_from(v) < get_eps()

    def deviation_from(self, v):
        dx = self.x - v.x
        dy = self.y - v.y
        dz = self.z - v.z
        return np.sqrt(dx * dx + dy * dy + dz * dz)

class Matrix3():
    '''
      https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/matrices
    '''
    def __init__(self, *args):
        # initialize with the identity matrix of 4x4 
        self.m = np.array([[1,0,0],[0,1,0],[0,0,1]])
        if len(args) > 0 :
            self._set_matrix(*args)

    def __str__(self):
        name = self.__class__.__name__
        return f"{name}({self.m})"

    def __rmul__(self, c):
        if type(c) is int or type(c) is float:
            return Matrix3(c * self.m)

        elif isinstance(c,Vector):
            return Vector(self.m @ c.as_array())

        elif type(c) is np.ndarray and len(c) >= 3 :
            v = c[0:3]
            return Vector(self.m @ v)

        elif type(c) is type(self):
            A = c.get_m()
            B = self.get_m()
            return self.__class__(A @ B)

    def __mul__(self, c):
        return self.__rmul__(c)

    # two help functions
    def _set_matrix(self, *args):
        import copy
        if len(args) == 1:   #   Matrix(M)
            
            first_input= args[0]
            if type(first_input) is self.__class__ :
                self.m = copy.deepcopy(first_input.m)

            else :  #  Matrix([[1,2,3],[5,6,7],[9,10,11]])  
                self._set_m(*first_input)
        
        else : #  Matrix([1,2,3],[5,6,7],[9,10,11])
            self._set_m(*args)

    def _set_m(self,*args):
        m = len(args) 
        for i in range(m) :
            n = len(args[i])
            for j in range(n):
                x = args[i][j]
                if type(x) is not str:
                    self.m[i,j] = x 
    
    # three functions to manipulate the matrix
    def get_m(self):
        m,n = np.shape(self.m)
        M = np.eye(m)
        for i in range(m):
            for j in range(m):
                M[i,j] = self.m[i,j]
        return M

    def transpose(self):
        return np.transpose(self.m)

    def inverse(self):
        return np.linalg.inv(self.m)

### Help functions
'''
https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/
geometry/spherical-coordinates-and-trigonometric-functions
'''
_clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

'''
    The following works for a vector of unit Magnitude, v
'''
def cosTheta(v):
    return v.y 

def sinTheta2(v):
    return max(0,1 - cosTheta*cosTheta )
def sinTheta(v):
    return math.sqrt(sinTheta2)

def cosPhi(v):
    sin_theta = sinTheta(v)
    if sin_theta == 0 :
        return 1
    return _clamp(v.x/sin_theta, -1, 1)

def sinPhi(v):
    sin_theta = sinTheta(v)
    if sin_theta == 0 :
        return 1
    return _clamp(v.y/sin_theta, -1, 1)

'''
    conversion of coordinates
'''
def _Cartesian_2_Spherical_Coordinates(v):  # (x,y,z) ->(theta, phi)
    theta = _clamp(math.acos(v.z),-1,1)
    phi = math.atan2(v.y,v.x) 
    if phi < 0:
        phi = phi + 2* math.pi
        '''
            atan2 returns a value in the range [−π:π], 
            We remap the value in the range [0:2π].
        '''
    return theta,phi

def _Spherical_2_Cartesian_Coordinates(theta, phi):
    return Vector(math.cos(phi) * math.sin(theta), 
                  math.sin(phi) * math.sin(theta), 
                  math.cos(theta))


# validation function for intersection
'''
     https://math.stackexchange.com/questions/27388/intersection-of-2-lines-in-2d-via-general-form-linear-equations?noredirect=1
''' 
# ----------------------
# generic math functions

def add_v3v3(v0, v1):
    return (
        v0[0] + v1[0],
        v0[1] + v1[1],
        v0[2] + v1[2],
        )

def sub_v3v3(v0, v1):
    return (
        v0[0] - v1[0],
        v0[1] - v1[1],
        v0[2] - v1[2],
        )

def dot_v3v3(v0, v1):
    return (
        (v0[0] * v1[0]) +
        (v0[1] * v1[1]) +
        (v0[2] * v1[2])
        )

def len_squared_v3(v0):
    return dot_v3v3(v0, v0)

def mul_v3_fl(v0, f):
    return (
        v0[0] * f,
        v0[1] * f,
        v0[2] * f,
        )

def isect_line_plane_v3(p0, p1, p_co, p_no, epsilon=1e-6):
    """
    p0, p1     : a line from p0 to p1.
    p_co, p_no : a plane 
                p_co, a point on the plane (plane coordinate).
                p_no, a normal vector defining the plane direction;
                      (does not need to be normalized).

    Return a Vector or None (when the intersection can't be found).
    """

    u = sub_v3v3(p1, p0)
    dot = dot_v3v3(p_no, u)

    if abs(dot) > epsilon:
        # The factor of the point between p0 -> p1 (0 - 1)
        # if 'fac' is between (0 - 1) the point intersects with the segment.
        # Otherwise:
        #  < 0.0: behind p0.
        #  > 1.0: in front of p1.
        w = sub_v3v3(p0, p_co)
        fac = -dot_v3v3(p_no, w) / dot
        u = mul_v3_fl(u, fac)
        return add_v3v3(p0, u)
    else:
        # The segment is parallel to plane.
        return None

# ----------------------


def main():
    v1 = Vector(1,2,3)
    print(f" v = {v1}")
    print(f" v = {v1.as_array()}")
    print(f" v = {v1.as_list()}")
    print(v1.cross(v1))
    v2 = Vector(v1)
    print(type(v2))

    m = Matrix3([1,2,3],[5,6,7],[9,10,11])

    print(f" m = {m}")
    print(m.transpose())

    v2 = m * v1
    print(f" m * v = {v2}")
    v3 = v1 * m
    print(f" v * m = {v3}")

    m2 = m * m 
    print(f" m * m = {m2}")

def test_vector2D_only():
    v1 = Vector2D(2, 5/3)
    v2 = Vector2D(3, -1.5)
    print('v1 = ', v1)
    print('repr(v2) = ', repr(v2))
    print('v1 + v2 = ', v1 + v2)
    print('v1 - v2 = ', v1 - v2)
    print('abs(v2 - v1) = ', abs(v2 - v1))
    print('-v2 = ', -v2)
    print('v1 * 3 = ', v1 * 3)
    print('7 * v2 = ', 7 * v1)
    print('v2 / 2.5 = ', v2 / 2.5)
    print('v1 % 1 = ', v1 % 1)
    print('v1.dot(v2) = v1 @ v2 = ', v1 @ v2)
    print('v1.distance_to(v2) = ',v1.distance_to(v2))
    print('v1 as polar vector, (r, theta) =', v1.to_polar())

if __name__ == '__main__':
    main()
