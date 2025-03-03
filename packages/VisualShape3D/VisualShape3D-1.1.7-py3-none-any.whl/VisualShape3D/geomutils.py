# from __future__ import absolute_import
from matplotlib import path 
import numpy as np
import math
from .mathutils import *

### Computation on the intersection of 3D Lines and 3D Polygons
'''
    All vertices follow the form of numpy.array(N,3)
'''

# 3D Line  

'''
     https://math.stackexchange.com/questions/27388/intersection-of-2-lines-in-2d-via-general-form-linear-equations?noredirect=1
''' 
# intersection functions


# 3D Plane, Polygons and Line
'''
   Core concern : intersection. 
   That is, a line of slop (L) from a point (P0) is intercepted with a Polygon.
   The process is decoupled into two steps :
        (1) the line cross a plane;
        (2) their intersection point falls in the polygon, including the border.

           P0 =np.array((x0,y0,z0))
           L  = np.array((dx,dy,dz))
           Polygon = np.array([                 # N x 3 array
                                [x1 y1 z1]
                                [x2 y2 z2]
                                ...
                                [xm ym zm]
                                ])
'''
def LineXLine(P1,L1,P2,L2):
    '''
         Intersection of two 3D Lines decribed as (P,L) .
         It returns,  
         (1)     P     , the intersection point;
         (2) 'parallel', they are in parallel; 
         (3) 'colinear', they are one; 
         (4) 'skrew' they are skrew in 3D space.
    '''
    # Normalize them
    A,B = Array(L1), Array(L2)
    C,D = Array(P1), Array(P2)
    CD = D - C

    E = UnitVector(A)
    F = UnitVector(B)

    X = Cross(F,CD)
    Y = Cross(F, E)

    # To check if they are zeros
    if(np.linalg.norm(X) <= get_eps() and np.linalg.norm(Y)  <= get_eps()):
        return 'colinear'

    else:
        if((np.linalg.norm(Y)) <= get_eps() ):
            return 'parallel'
        else  :
            Z = Dot(X,Y)
            sign = 1 if Z>0 else -1
            M = C + sign * Magnitude(X)/Magnitude(Y) * E
            if PointInLine(M,P1,L1) == False or PointInLine(M,P2,L2) == False:
                return 'skrew'
            else:
                return tuple(M)

def LineXPlane(P0,L,R0,n):
    '''
           Intersection of a 3D line with a 3D plane
           It returns
           (1)  P1       : P1 is a Python tuple
           (2) 'parallel':  the line is parallel to the plane
           (3) 'coplane' :  the line is on the plane (coplane)
    '''
    
    P0 = Array(P0)
    L  = Array(L)
    R0 = Array(R0)
    n  = Array(n)

    L = UnitVector(L) 
    n_dot_L = Dot(n,L)  
    dP = R0 - P0                         # [dx,dy,dz]

    if ScalarZero(n_dot_L):
        if ScalarZero(Dot(dP,dP)) or ScalarZero(Dot(dP,n)):
            return 'parallel'
        else:
            return 'coplane'

    x  = Dot(n,dP)/n_dot_L
    P  = P0 + x*L                         # [x,y,z]

    return tuple(P)   
    # return np.array 

def SegmentXPolygon(P1,P2,polygon):
    # Intersection of a segment (P1,P2) with a polygon
    polygon = Array(polygon)
    points, path2d = D3ToD2(np.vstack([P1,P2]),polygon)

    if AllPositive(points[:,2]) or AllNegative(points[:,2]) :
        return None

    elif AllZero(points[:,2]):
        return [P1,P2]

    # Partial positive and negative
    L  = UnitVector(Array(P2) - Array(P1))
    P0 = P1

    Point = LineXPolygon(P0,L,polygon)

    if type(Point) is str:
        return None

    elif type(Point) is tuple : # single point
        if PointInSegment(Array(Point),P1,P2):
           return Point
        else :
           return None

    else :
        V1,V2 = Point
        if PointInSegment(Array(V1),P1,P2) and PointInSegment(Array(V2),P1,P2) :
            return [V1,V2]
        
        elif PointInSegment(Array(V1),P1,P2) :
            return V1

        elif PointInSegment(Array(V2),P1,P2) :
            return V2

        else :
            return None
 
def LineXSegment2D(P0,L,x1,y1,x2,y2):
    '''
        Intersection of a segment (x1,y1),(x2,y2) with a 2D line.
        It returns :
        (1) True, P, intersecting point, list;
        (2) False, None, No intersection;
        (3) True, ‘colinear’, the segment if part of the line
    '''
    P1,L1,P2 = (x1,y1), (x1-x2,y1-y2), (x2,y2)
    L1  = UnitVector(Array(L1))

    if np.linalg.norm(L1) <= get_eps():
        return False, None

    else:
        P = LineXLine(P0,L,P1,L1) 

        if P == 'parallel':
            return False, None

        elif P == 'colinear':
            return True, 'colinear'

        else:
            P = Array(P)
            if PointInSegment(P, P1, P2): 
                return True, tuple(P)
            else:
                return False,'beyond segment'

def LineXPolygon2D(P0,L,Polygon):
    '''
         Intersection of line with polygon in 2D space.
         It returns a pair of values as follow,
            (1) P1，None   : one intersection point
            (2) None，None : no intersection
            (3)  P1，   P2 : two intersection points
    '''
    L = UnitVector(L) 
    n = len(Polygon)
    IS = 0
    P1 = None
    P2 = None
    for i in range(n):
        x1,y1 = Polygon[i]
        x2,y2 = Polygon[(i+1)%n]

        ret, P = LineXSegment2D(P0,L,x1,y1,x2,y2)  
        # to check its intersection with each edge of the polygon
        if ret is False :
            pass
        
        elif P == 'colinear':           # the edge is part of line
            P1,P2 = (x1,y1),(x2,y2)
            return P1,P2
        
        else:
            if P1 is None:
                P1 = P
            elif np.linalg.norm(Array(P)-Array(P1)) <= get_eps():
                pass 

            else:
                P2 = P
                return P1,P2

    if P1 is None :
        return None, None
    else:
        return P1, None

def LineXPolygon(P0,L,Polygon):
    '''
    In 3D space, intersection of a line with a polygon.
    It returns the intersection point as tuple : P1 
       or 
          (1) a list of two tuples, [P1,P2],  for two intersection points;
                         plus a console warning : 
                         there are two points of intersection
          (2) string message 
               a) 'Intersection point beyond the polygon' 
               b) 'The line beyond the 2D plogon'
          
    '''
    n  = GetNormal(Polygon)      # [dx,dy,dz] 
    R0 = Array(Polygon[0,:])         # [x,y,z]
    U  = GetU(Polygon)
    R = LineXPlane(P0,L,R0,n)  # intersection of line with plane
    # print(f" In LineXPolygon() :\n R = LineXPlane(P0,L,R0,n)\n result = {R}")
    # print(f" Polygon :\n{Polygon}")

    if type(R) == str :
        if R == 'parallel':
            return 'parallel'

        if R == 'coplane':  # The line lies in the plane, so it reduces to 2D space
            PL = P0 + L
            P03D,Polygon3D = D3ToD2(P0,Polygon)                      ##从三维矩阵变成二维
            PL3D,Polygon3D = D3ToD2(PL,Polygon)
            Polygon2D = Polygon3D[:,0:2]
            L3D  = P03D-PL3D
            P02D = P03D[0:2]
            L2D  = L3D[0:2]
            P1,P2 = LineXPolygon2D(P02D,L2D,Polygon2D)

            if P1 is None : # and Points is None:
                return 'The line beyond the 2D plogon'

            elif type(P1) is tuple :  # single point
                R1 = Array(P1)
                P1 = D2toD3Point(R1,U,R0)
                return tuple(P1)

            else: # two points
                R1,R2 = P1
                P1 = D2toD3Point(Array(R1),U,R0)
                P2 = D2toD3Point(Array(R2),U,R0)
                print('intesection leaves a segment of ',
                    np.around(P1, decimals=3, out=None),
                    np.around(P2, decimals=3, out=None))
                return [tuple(P1), tuple(P2)]
    
    else :

        if PointInPolygon(R,Polygon) :
            return tuple(R)
        else :
            return 'Intersection point beyond the polygon'

######## lines ######################
def LinesXPlane(P0,L,R0,n):
    '''
           Intersection of 3D lines with a 3D plane
           It returns intesected points and a logical matrix indicting which are connected
    '''
    P0 = Array(P0)
    L  = Array(L)
    R0 = Array(R0)
    n  = Array(n)

    L = UnitVector(L) 
    n_dot_L = Dot(n,L)
    invalidate = (n_dot_L < get_eps() )
    validate = ~invalidate 

    n_dot_L = n_dot_L[validate]
    if n_dot_L.size == 0:
        return None, validate

    L = L[validate]
    dP = R0 - P0                         # [dx,dy,dz]
    n_dot_dP = Dot(n,dP)
    x  = n_dot_dP/n_dot_L
    P  = P0 + x[:,None]*L                # [x,y,z]

    return Round(P), validate 

def LinesXPolygon(P0,L,Polygon):
    '''
    In 3D space, it checks which lines cross the polygon.
    It returns the logic array and an array of intersection'
    '''
    n  = GetNormal(Polygon)     # [dx,dy,dz] 
    R0 = Array(Polygon[0,:])    # [x,y,z]
    R, intersect1 = LinesXPlane(P0,L,R0,n)  # intersection of line with plane

    if R is None:
        return None

    intersect2 = PointsInPolygon(R,Polygon) 

    # set it unitary
    if R.ndim == 1:
        return R

    if np.all(intersect2 == False):
        return None

    return intersect, R[intersect]

# To check if many points lie in a polygon, True/False
def PointsInPolygon(Points,Polygon):

    Points = Array(Points)

    # set it unitary
    if Points.ndim == 1:
        return PointInPolygon(Points,Polygon)

    elif Points.ndim ==2 :
        a,b = Points.shape
        if a == 1 :
            index = PointInPolygon(Points[0],Polygon)
            return [index]

    # A matrix of (x,y,z) Points
    vertices, original_shape = Flatten(Points)
    xyz, path2d = D3ToD2(vertices,Polygon)
    xq,yq,zq = xyz[:,0], xyz[:,1],xyz[:,2]

    ret = (zq == 0.0)
    xv,yv = path2d[:,0],path2d[:,1]

    # ret = ret*PointsInPolygon2D(xy, poly2d)

    ret = ret*in_polygon_2d(xq, yq, xv, yv)

    return ret.reshape(original_shape)

######## lines ######################

###
#         coordinate system
#
def LocalCoordinate(Line1,Line2):
    # Create a local coordinate system.
    a = Array(Line1)
    b = Array(Line2)
    c = Cross(a, b)
    b = Cross(c, a)

    i = UnitVector(a)
    j = UnitVector(b)
    k = UnitVector(c)
    return i,j,k
#
def GetU(polygon):
    """
        Get a matrix from its 3D to 2D
            U = GetU(polygon)
        Parameter :
            polygon : vertices of np.array(M,3)
    """

    v = polygon
    if type(v) != np.ndarray :
        v = Array(v) 

    a = v[1,:] - v[0,:]
    b = v[2,:] - v[1,:]

    i,j,k = LocalCoordinate(a,b)

    # show("i",i)
    # show("j",j)
    # show("k",k)

    U = np.vstack((i,j,k))

    # show('U',U)

    return U
#
def GetArea(polygon):
    xy, U = to_2d(polygon)
    return GetArea2D(xy)
#
def GetArea2D(xy):
    x,y = xy[:,0], xy[:,1]
    m = len(x)
    s = x[m-1]*y[0] - x[0]*y[m-1]
    for i in range(m-1):
        s += x[i]*y[i+1] - y[i]*x[i+1]
    area = Round(0.5*s)
    return area
#
def GetNormal(polygon):
    """
       get a unitary vector normal to the polygon 
       parameter : polygon
                     np.array(M,3)
    """
    v = polygon
    #
    #   C = A x B 
    #
    A = v[1,:] - v[0,:]
    B = v[2,:] - v[1,:]
    C = Cross(A,B)
    
    return UnitVector(C)

#  From 3D to 2D
def to_2d(Polygon):
    U  = GetU(Polygon)
    R  = Array(Polygon)
    R0 = Array(Polygon[0,:])
    r  = U@(R - R0).T  # @ is for vector times matrix
    vertices2D = r.T[:,0:2]
    return Round(vertices2D), U

def D3ToD2(Points,Polygon):
    U  = GetU(Polygon)
    R  = Array(Polygon)
    R0 = Array(Polygon[0,:])
    P  = Array(Points)
    r  = U@(R - R0).T  # @ is for vector times matrix
    p  = U@(P - R0).T
    xyz = p.T
    path3D = r.T
    path2D = r.T[:,0:2]
    return Round(xyz),Round(path2D)

# From 2D to 3D :
def D2toD3(Points,U,R0):
    r = Points.T        # to (3,m)
    A = np.mat(U)
    B = np.array(A.I)   #  inverse, .I only works for np.matrix
    R = (B@r).T + R0    # .T works for both matrxi and array
    return Round(R)     #  to let R is np.array

def D2toD3_xy(x,y,U,R0):
    z = [0 for _ in range(len(x))]
    Points = np.vstack((x,y,z)).T
    return D2toD3(Points,U,R0)

# To check if a  point lies in a polygon, True/False
def PointInPolygon(Point,Polygon):
    # print(f" In PointInPolygon(), Polygon =\n{Polygon}")
    xyz, path2d = D3ToD2(Point,Polygon)
    # print(f" xyz=\n{xyz}")
    z = xyz[2]
    xy = xyz[0:2]      # first two columns 
    
    if ScalarZero(z) : # z = 0 , the point is in the plane 
        return PointInPolygon2D(xy[0], xy[1], path2d)
    else :
        return False

def NormalToLine(P0,P,L):
    '''
        return a line from P0 and perpendicular to (P,L) 
        a vertical plane (R0, n) to the line (P,L)
        return the direction of line from P0 to R
            R intersection point
    '''
    R0 = Array(P0)
    n  = Array(L)

    R, selected = LineXPlane(P,L,R0,n)

    if R is None :
        return None, None

    if type(R) is np.ndarray :
        dR = R - R0
        return UnitVector(dR),R
    else :
        return None,None

def PointInLine(P0,P,L):
    # To check if the point P0 is on the 3D line(P,L), Ture/False
    V0 = Array(P0)
    V  = Array(P)

    if Equal(V0,V) :
        return True

    L1 = UnitVector( V0 - V )
    Lx = UnitVector(Array(L))
    if Equal(L1, Lx) or Equal(L1, (-1)*Lx):
        return True
    else:
        return False

def PointInSegment(P,P1,P2):
    # To check if P is inside a segment(P1,P2), Ture/False

    pos = np.vstack((P1, P2))
    pos = np.array([np.min(pos[ :, :], axis=0),
                    np.max(pos[ :, :], axis=0)])

    if type(P) is not np.ndarray:
        P = Array(P)
        
    return np.all(P>=pos[0,:]) & np.all(P<=pos[1,:])



def Flatten(Point_Matrix):
    from functools import reduce
    from operator import mul

    # Multiple Points : matrix to array of (x,y,z)
    shape = np.shape(Point_Matrix)     #  0,...,n-1
    shape_matrix = shape[0:-1]         #  0,...,n-2, excluding shape[-1]
    n = reduce(mul, shape_matrix, 1)   #  how many points
    Point_Array = Point_Matrix.reshape(n,shape[-1])  # 1D array of (x,y,z).
    return Point_Array,shape_matrix
# 
# 2D points inside a 2D polygon, it returns True/False accordingly
#
def in_polygon_2d(xq, yq, xv, yv):
    """
    reimplement inpolygon in matlab
    :type xq: np.ndarray
    :type yq: np.ndarray
    :type xv: np.ndarray
    :type yv: np.ndarray
    """
    # 合并xv和yv为顶点数组
    vertices = np.vstack((xv, yv)).T
    
    # 定义Path对象
    my_path = path.Path(vertices)
    
    old_shape = np.shape(xq)
    # 把xq和yq合并为test_points
    test_points = np.hstack([xq.reshape(xq.size, -1), yq.reshape(yq.size, -1)])
    
    # 得到一个test_points是否严格在path内的mask，是bool值数组
    _inside = my_path.contains_points(test_points)
    
    # 得到一个test_points是否在path内部或者在路径上的mask
    _inside_on_edge = my_path.contains_points(test_points, radius=1e-10)
    
    # 得到一个test_points是否在path路径上的mask
    _on = _inside ^ _inside_on_edge
    
    return _inside_on_edge.reshape(old_shape)

def PointInPolygon2D(x0,y0,Polygon):
    """
       return value :
         True,  (XO,YO) IS LOCATED BOTH IN Polygon and ON EDGE
         False, (XO,YO) FAILS TO DO SO
    """
    if type(x0) is np.ndarray or type(y0) is np.ndarray :
        raise ValueError(f"PointInPolygon2D(x0,y0,Polygon)\n"
            "x0 or y0 need be a scalar value, but be given array.")

    n = len(Polygon)
    IS = 0
    for i in range(n):
        # print(f" Polygon[i] is of {type(Polygon[i])},\n{Polygon[i]}")
        x1,y1 = Polygon[i]
        x2,y2 = Polygon[(i+1)%n]
        I = PointInSegment2D(x0,y0,x1,y1,x2,y2)
        # print(f" {loc[I]} of line = ({x1,y1}) - ({x2,y2})  ")
        if I == 1 :    
            IS += 1    #  x0 < x_predicted
        elif I == 2 :  # on edge
            return True
        
    ret = IS%2
    if ret == 1 :
        return True
    else:
        return False

    """
    Starting from a point P0, a ray goes to the right.
        INTERSECTION ?
            ret=O  NO  ( no any intersection with edges )
            ret=1  YES ( There is one intersection point, P0 is internal.) 
            ret=2  YES ( P0 is ON EDGE ) 
    """
    # ymin < y0 < ymax 
#
# 
# 2D points inside a 2D polygon, it return True/False
#
#
# multiple points in a polygon : 2D only
def PointsInPolygon2D(Points,Polygon,method='Custom'):
    Vertices = Points
    if type(Points) is not np.array:
        Vertices = Array(Points)

    # A)Single Point
    # 1) input as np.array([7,8]), shape =(2,)
    if len(Vertices.shape) == 1 :
        x0 = Vertices[0]
        y0 = Vertices[1]
        ##print(x0,y0,Polygon)
        ret = PointInPolygon2D(x0,y0,Polygon) 
        return ret

    # 2) input as np.array([(7,8)]), shape = (1,2)
    elif (len(Vertices.shape) == 2 and Vertices.shape[0] == 1) : 
        x0 = Vertices[0][0]
        y0 = Vertices[0][1]
        ret = PointInPolygon2D(x0,y0,Polygon)
        return ret

    # B) A matrix of (x,y) Points
    vertices, original_shape = Flatten(Points)
    key_str = method.lower()
    if key_str == 'custom':
        ret = _PointsInPolygon2D_Custom(vertices,Polygon)
    elif key_str == 'matplotlib':
        ret = _PointsInPolygon2D_Matplotlib(vertices, Polygon)

    return ret.reshape(original_shape)

# help functions 
def _PointsInPolygon2D_Custom(Points,Polygon):
    n = len(Points)
    ret = Array(list(False for i in range(n)))
    for i in range(n):
        x0,y0  = Points[i]
        ret[i] = PointInPolygon2D(x0,y0,Polygon)   
    return ret

def _PointsInPolygon2D_Matplotlib(Points,Polygon):
    row = len(Polygon)   # row = N, Polygon = N x 2   
    
    # Inside
    edge = path.Path([(Polygon[i,0],Polygon[i,1]) for i in range(row)])
    ret  = edge.contains_points(Points)    
    
    # print(ret)
    # On edge
    if not all(ret) :        
        n = len(Points)
        for i in range(0,row):
            j = (i+1)%row 
            x1,y1 = Polygon[i]
            x2,y2 = Polygon[j]
            dy = y2-y1
            dx = x2-x1
           
            for k in range(n):
                if ret[k] :
                    continue          
                
                x0,y0 = Points[k]
                if not ScalarZero(dy):
                    if min(y1,y2) <= y0 and y0 <= max(y1,y2) :                        
                        x = x1 + (y0-y1)*dx/dy   # any slant line, including vertical line
                        if ScalarEqual(x,x0) :
                            ret[k] = True
                            
                elif not ScalarZero(dx):    # horizontal line
                    if min(x1,x2) <= x0 and x0 <= max(x1,x2) :
                        if ScalarEqual(y1,y0):
                            ret[k] = True
                                     
    # inside + on Edge
    return ret

# multiple points in a polygon : variant method 0
def PointsInPolygon0(Points,Polygon):
    Points = np.array(Points)
    ret=[]
    if Points.ndim ==2:
        for i,point in enumerate(Points):
            ret.append(PointInPolygon(point,Polygon))
        ret=np.array(ret)
        return ret
    elif Points.ndim ==3:
        for i,points in enumerate(Points):
            for j,point in enumerate(points):
                ret.append(PointInPolygon(point,Polygon))
        ret=np.array(ret)
        ret = ret.reshape(i+1,j+1)
        return ret
    else:
        return None

# multiple points in a polygon : variant method 1
def PointsInPolygon1(Points,Polygon):
    Points = np.array(Points)
    if Points.ndim ==2:
        n=len(Points)
        ret = np.array(list(False for i in range(n)))
        for i,point in enumerate(Points):
            ret[i]=(PointInPolygon(point,Polygon))
        return ret
    elif Points.ndim ==3:
        n=len(Points)
        m=len(Points[0])
        ret = np.array(list(False for i in range(n*m)))
        ret = ret.reshape(n,m)
        for i,points in enumerate(Points):
            for j,point in enumerate(points):
                ret[i,j]=(PointInPolygon(point,Polygon))
        return ret
    else:
        return None

def PointInSegment2D_old(x0,y0,x1,y1,x2,y2):
    if ScalarEqual(max(y1,y2),y0) or ScalarEqual(min(y1,y2),y0) or ((max(y1,y2)>y0) & ( y0>min(y1,y2))):   
    #    if (max(y1,y2)>=y0) & ( y0>=min(y1,y2)) in the condition that all intersection occurs by the right
        if not ScalarEqual(y1 , y2) :   # y1 != y2 :
            if not ScalarEqual(x1, x2) : # x1 != x2 :
                x=x1+(y0-y1)*(x2-x1)/(y2-y1)   # predicted point
                if  ScalarEqual(x0, x) :  # x0 == x :
                    return 2
                
                if x0 < x :
                    if ScalarEqual(min(y1,y2) , y0):
                        return 0
                    else:
                        return 1            
                return 0
            
            else:        # vertical line
                if ScalarEqual(x0,x1) :
                    return 2
                
                elif x0 < x1 :
                    if ScalarEqual(min(y1,y2) , y0):
                        return 0
                    else:
                        return 1            

                else :               # x0 > x1 :
                    return 0
               
        else:  # horizontal line
            if not ScalarEqual(y0 , y1) :
                return 0

            elif ScalarEqual(x1,x0) or ScalarEqual(x0,x2) or max(x1,x2)>x0 and x0>min(x1,x2) :  #  y1 == y0
                return 2
    else:
        return 0

def PointInSegment2D(x0,y0,x1,y1,x2,y2):
    if ScalarEqual(max(y1,y2),y0) or ((max(y1,y2)>y0) & ( y0>min(y1,y2))):   
    #  if (max(y1,y2)>=y0) & ( y0>=min(y1,y2)) in the condition that all intersection occurs by the right
        if not ScalarEqual(y1 , y2) :   # y1 != y2 :
            x=x1+(y0-y1)*(x2-x1)/(y2-y1)   # predicted point
            if  ScalarEqual(x0, x) :  # x0 == x :
                return 2
            if x0 < x :
                return 1 
            return 0
               
        else:  # horizontal line
            if ScalarEqual(x1,x0) or ScalarEqual(x0,x2) or max(x1,x2)>x0 and x0>min(x1,x2) :  #  y1 == y0
                return 2
            return 0
    elif ScalarEqual(min(y1,y2) , y0):
        if ScalarEqual(min(y1,y2) , y1):
            if ScalarEqual(x1,x0):
                return 2
            else:
                return 0
        else:
            if ScalarEqual(x2,x0):
                return 2
            else:
                return 0
    else:
        return 0



# functions from Internet:
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


#
#  Demo how to use them
#
def test_PointsInPolygon2D():
    P = [(7,8),(6.5,7.7),(10,5),(10,11),(7,13),(6,-1),(5,5),(10,10),(10,5),(5,10)]
    vertices = [(5,5),(5,10),(10,10),(10,5)]

    Points = np.array(P)
    polygon = np.array(vertices)
    ret = PointsInPolygon2D(Points, polygon)
    print(ret)
    print(Points[ret])

def test_PointsInPath2D():
    P = [(7,8),(6.5,7.7),(10,5),(10,11),(7,13),(6,-1),(5,5),(10,10),(10,5),(5,10)]
    vertices = [(5,5),(5,10),(10,10),(10,5)]
    Points = np.array(P)
    polygon = np.array(vertices)
    ret = PointsInPolygon2D(P, polygon, Method = 'Matplotlib')
    print(ret)
    print(Points[ret])

def main():
    test_PointsInPolygon2D()
    test_PointsInPath2D()

if __name__ == '__main__':
    main()
