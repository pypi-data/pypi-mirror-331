from matplotlib import path 
import numpy as np
from math import radians, cos, sin, pi
from VisualShape3D.mathutils import get_eps,get_sig_figures,UnitVector

"""
    Rapid creation of 3D polygons of simple shapes
    Shape Functions
         (1) Input a 2D Polygon in yz Plane 
         (2) Move it to a 3D position 
                        with regard to its origin  P0 
                        as well as normal direction of surface n
"""
def add_col(n, dtype=int):
    """
    It adds a column of length n
    return a column of array.
    """
    return np.reshape(np.arange(n, dtype = dtype), (n, 1))


# 1) To create a dictionary list that holds all arguments 
#      for shapes just inputed.
__polygonInputDicts = []

def polygonInputDict(each_shape_input):
    __polygonInputDicts.append(each_shape_input)
    return each_shape_input

@polygonInputDict
def dict_rectangle(*args):
    return {"shape":"rectangle","W":args[0],"H":args[1]}

@polygonInputDict
def dict_triangle(*args):
    return {"shape":"triangle","W" : args[0], "H" : args[1], "A" : args[2]}

@polygonInputDict
def dict_rectangleWithHole(*args):
    return {
            "shape":"rectangleWithHole",
            "W" : args[0],
            "H" : args[1], 
            "A" : args[2],
            "B" : args[3],
            "C" : args[4],
            "D" : args[5]}

@polygonInputDict
def dict_fourSided(*args):
    return {
            "shape":"fourSided","W" : args[0],
            "H" : args[1], 
            "A" : args[2],
            "B" : args[3],
            "C" : args[4]}

@polygonInputDict
def dict_fiveSided(*args):
    return {
            "shape":"fiveSided","W" : args[0],
            "H" : args[1], 
            "A" : args[2],
            "B" : args[3],
            "C" : args[4],
            "D" : args[5]}

@polygonInputDict
def dict_regularPolygon(*args):
    return {
            "n": args[0], 
            "R": args[1]
            }

@polygonInputDict
def dict_polygon(*args):
    # return np.array(list(map(lambda x:x,args)))
    return  np.array(list(map(lambda x:x,args[0])))


#2) to create vertices (0,y,z) for each shape
# define a function collection
__shapeFunctions = []
def shapeFunction(each_definition_func):
    __shapeFunctions.append(each_definition_func)
    return each_definition_func

@shapeFunction
def rectangle(*args):
    W = args[0]
    H = args[1]
    return np.array([(0,0,0),(0,W,0),(0,W,H),(0,0,H)])

@shapeFunction
def triangle(*args):
    W = args[0]
    H = args[1] 
    A = args[2]
    return np.array([(0,0,0),(0,W,0),(0,A,H)])


@shapeFunction
def rectangleWithHole(*args):
    W = args[0]
    H = args[1]
    A = args[2]
    B = args[3]
    C = args[4]
    D = args[5]


    if C > 0 and D > 0 and (A + C) < W and (B + D) < H:
        ret = np.array(
            [(0, 0, 0), (0, W, 0), (0, W, H), (0, A, H), (0, A, B + D), (0, C + A, B + D), (0, C + A, B), (0, A, B),
             (0, A, H), (0, 0, H)])

    elif A == 0.0:
        if B == 0.0 and (A + C) < W and (B + D) < H:
            ret = np.array([(0, C, 0), (0, W, 0), (0, W, H), (0, 0, H), (0, 0, D), (0, C, D)])

        if B != 0.0 and (A + C) < W and (B + D) < H:
            ret = np.array(
                [(0, 0, 0), (0, W, 0), (0, W, H), (0, 0, H), (0, 0, B + D), (0, C, B + D), (0, C, B), (0, 0, B)])

        if B != 0.0 and (A + C) < W and (B + D) >= H:
            ret = np.array([(0, 0, 0), (0, W, 0), (0, W, H), (0, C, H), (0, C, B), (0, 0, B)])


    elif A != 0.0:
        if B == 0.0 and (C + A) < W and (B + D) < H:
            ret = np.array(
                [(0, 0, 0), (0, A, 0), (0, A, D), (0, A + C, D), (0, A + C, 0), (0, W, 0), (0, W, H), (0, 0, H)])

        if B != 0.0 and (A + C) < W and (B + D) >= H:
            ret = np.array(
                [(0, 0, 0), (0, W, 0), (0, W, H), (0, A + C, H), (0, A + C, B), (0, A, B), (0, A, H), (0, 0, H)])

        if B == 0.0 and (A + C) >= W and (B + D) < H:
            ret = np.array([(0, 0, 0), (0, A, 0), (0, A, D), (0, W, D), (0, W, H), (0, 0, H)])

        if B != 0.0 and (A + C) >= W and (B + D) < H:
            ret = np.array(
                [(0, 0, 0), (0, W, 0), (0, W, B), (0, A, B), (0, A, B + D), (0, W, B + D), (0, W, H), (0, 0, H)])

        if B != 0.0 and (A + C) >= W and (B + D) >= H:
            ret = np.array([(0, 0, 0), (0, W, 0), (0, W, B), (0, A, B), (0, A, H), (0, 0, H)])

    else:
        raise ValueError(f"Incorrect inputs : W={W}, H={H}, A={A}, B={B}, C={C}, D={D}")

    return ret

@shapeFunction
def fourSided(*args):
    W = args[0]
    H = args[1] 
    A = args[2]
    B = args[3]
    C = args[4]
    return np.array([(0,0,0),(0,W,0),(0,A+C,H),(0,A,B)])

@shapeFunction
def fiveSided(*args):
    W = args[0]
    H = args[1] 
    A = args[2]
    B = args[3]
    C = args[4]
    D = args[5]
    return np.array([(0,0,0),(0,W,0),(0,W+C,D),(0,A+B,H),(0,A,H)])

@shapeFunction
def regularPolygon(*args):
    if len(args) < 2 :
        raise ValueError(" Usage : regularPolygon(n, R)")
        return

    dict_regularPolygon(*args)

    n     = args[0]
    R     = args[1] 

    if n < 3 :
        n = 3

    theta = pi/n
    s = R * sin(theta)
    a = R * cos(theta)

    theta = 2*pi/n
    vertices = []
    for i in range(n):
        angle = i * theta
        x = 0.0
        y = R * cos(angle)
        z = R * sin(angle)
        vertices.append((x,y,z))

    return np.array(vertices)  #,s,a

@shapeFunction
def polygon(*args):
    value = args[0]
    if isinstance(value,list):
        vertices = np.array(value)

    elif isinstance(value,np.ndarray) :
        vertices = value
    else :
        raise ValueError(' Usage : polygon( vertices ): vertices be list or array !!!')

    dict_polygon(*args)

    if vertices.shape[1] == 2:
    # from Utilities import add_col
        vertices = np.hstack((add_col(vertices.shape[0])*0, vertices))

    # return np.array(list(map(lambda x:x,args)))
    return np.array(vertices)


# create a namelist of these function
__shapeNames = [func.__name__ for func in __shapeFunctions ]

def createPolygon(shapeName,*args):
    name = [x.lower() for x in __shapeNames]
    i = name.index(shapeName.lower())
    __polygonInputDicts[i](*args)
    return __shapeFunctions[i](*args)

def isDefaultShape(shapeName):
    name = [x.lower() for x in __shapeNames]
    return shapeName.lower() in name

def polygons():
    return __shapeNames

def getPolygonInputDict(shapeName,*args):
    name = [x.lower() for x in __shapeNames]
    i = name.index(shapeName.lower())
    return __polygonInputDicts[i](*args)

# change the result of getpolygonInputDict 
# to a list of strings in the format of key = value 
def format_dict(kwargs):
    args_list = kwargs.items()
    shape = kwargs["shape"]
    new_format = list(map(lambda x: f"{x[0]}={x[1]}", kwargs.items())) 
    new_format[0] = f"'{shape}'"
    return ', '.join(e for e in new_format)


# For a 2D shape created at the initial position,
# one can move it to a desired position by a matrix below
# angles : degree
def tranformMatrix(alpha, beta):
    al = radians(alpha)
    be = radians(beta)
    X = [cos(be)*cos(al), -sin(al), -sin(be)*cos(al)]
    Y = [cos(be)*sin(al),  cos(al), -sin(be)*sin(al)]
    Z = [sin(be),                0,          cos(be)]
    return np.vstack([X,Y,Z])
#
#   row-based calculation : V * U  + V0
#
def transform(shape, to = None, angles = (0.0,0.0), origin = None):
    R  = translate(shape, to, origin)
    R1 = np.asarray(to)
    dR = R - R1

    alpha, beta = angles[0], angles[1]
    U  = tranformMatrix(alpha, beta)
    
    return np.dot(dR, U.T) + R1

def translate(shape, to = None, origin = None):
    vertices = shape
    if vertices.shape[1] == 2:
        vertices = np.hstack((add_col(vertices.shape[0])*0, vertices))    

    if origin is None : origin = vertices[0]
    if to is None : to = vertices[0]

    R0  = np.asarray(origin)
    R1  = np.asarray(to)
    dR1 = R1 - R0
    R   = vertices + dR1
    return R

def transform_matrix_for_alpha(y_vector,z_vector):
    # Create a local coordinate system.
    b = np.asarray(y_vector)
    c = np.asarray(z_vector)
    a = np.cross(b, c)
    b = np.cross(c, a)

    i = UnitVector(a)
    j = UnitVector(b)
    k = UnitVector(c)
    return i,j,k

def rotate_by_alpha(shape, alpha=0.0, origin=None):
    # 计算第一条边（第一两个点）  
    v1,v2,v3 = shape[0],shape[1],shape[2]  
    y_vector = v2 - v1  
    z_vector = [0,0,1]
    
    """ 局部坐标系，多边形位于 yz 平面， z 轴穿过 origin 点且与 Z轴平行 (0,0,1) """  
    transMatrix = transform_matrix_for_alpha(y_vector,z_vector)
     
    if origin is None :
        origin = v1

    vertices = localized(shape, transMatrix, origin) 

    """ 绕z轴，逆时针旋转 alpha  """
    U = tranformMatrix(alpha, 0.0)
    dR  = vertices 
    transformed_vertices = np.dot(dR, U.T)

    """ 返回原坐标系 """
    global_vertices = globalized(transformed_vertices, transMatrix, origin)
     
    return global_vertices

def transform_matrix_for_beta(y_vector,normal_vector):
    # Create a local coordinate system.
    a = np.asarray(normal_vector)
    b = np.asarray(y_vector)
    c = np.cross(a, b)

    i = UnitVector(a)
    j = UnitVector(b)
    k = UnitVector(c)
    return i,j,k

def rotate_by_beta(shape, beta=0.0, origin=None):
    # 计算第一条边（第一两个点）  
    v1,v2,v3 = shape[0],shape[1],shape[2]  
    y_vector = v2 - v1  
    
    # 计算法向量（使用第一点和第二、第三点形成的平面）  
    normal = np.cross(v2-v1, v3-v1)  

    """ 移动坐标系y轴，让多边形第一条边位于 yz 平面， z 轴穿过 origin 点 """  
    transMatrix = transform_matrix_for_beta(y_vector,normal)
    if origin is None :
        origin = v1 
    vertices = localized(shape, transMatrix, origin)

    """ 绕 y 轴，逆时针旋转 beta  """
    U = tranformMatrix(0.0, beta)
    dR  = vertices 
    transformed_vertices = np.dot(dR, U.T) 

    """ 返回原坐标系 """
    global_vertices = globalized(transformed_vertices, transMatrix, origin)
     
    return global_vertices

def localized(polygon, transformation_matrix, origin):  
    """ 将多边形顶点从全局坐标系转换到局部坐标系 """  
    local_vertices = []  
    
    for vertex in polygon:  
        vertex = np.asarray(vertex) - origin  # 平移到原点  
        local_vertex = np.dot(transformation_matrix, vertex)  
        local_vertices.append(local_vertex)  
    
    return local_vertices  

def globalized(polygon, transformation_matrix, origin):  
    """ 将多边形顶点从局部坐标系转换到全局坐标系 """  
    global_vertices = [] 
    U_inv = np.linalg.inv(transformation_matrix)
    
    for vertex in polygon:  
        vertex = np.asarray(vertex)   # 平移到原点  
        dR = np.dot(U_inv, vertex)  
        global_vertices.append(dR + origin)      
    return global_vertices 

def displace(shape, by = (0,0,0) ):
    points = np.asarray(shape)
    if points.ndim == 2 :
       vertices = points
       if points.shape[1] == 2:  # ([x,y],[x,y],...,[x,y]])
           vertices = np.insert(points,0,0,axis = 1) 
           # np.hstack((add_col(points.shape[0])*0, vertices))

    elif points.ndim == 1:  
       vertices = points
       if points.shape[0] == 2:  # [x,y]
           vertices = np.insert(points,0,0,axis = 1)

    displacement = np.asarray(by)
    vertices = vertices + displacement  
    return vertices  

def flip(shape):
    # it swaps the negative and positive sides
    vertices = np.asarray(shape)
    if vertices.shape[1] == 2:
        vertices = np.hstack((add_col(vertices.shape[0])*0, vertices))
    return np.flipud(vertices)


# move from the intial position to a desired position ( old style )
#              column-based calculation : U * V + V0
#              input-output : row-based vertices
def move(shape = rectangle(1.0,1.0), origin = None, to = None, by = (0.0,0.0)):
    (alpha, beta) = by
    # Comment them out for fast run
    # if (type(shape) is list) or type(shape) is tuple:
    #     vertices = np.array(shape)
    # elif type(shape) is np.ndarray :
    #     vertices = shape
    # else :
    #     raise ValueError('move() needs a list/np.array for a polygon')

    # print(f" to rotate by {by}")

    vertices = shape
    if vertices.shape[1] == 2:
        vertices = np.hstack((add_col(vertices.shape[0])*0, vertices))
    
    facet = vertices.transpose() 

    if origin is None : origin = vertices[0,:]
    if to is None : to = vertices[0,:]

    R0 = np.array(origin).reshape(-1,1) 
    R1 = np.array(to).reshape(-1,1)
    dR = R1 - R0

    U = tranformMatrix(alpha,beta)
    facet_new = U.dot(facet) + dR

    return facet_new.transpose()


def main():
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    def plot_shape(vertices, ax, label="Original"):
        """绘制三维形状"""
        vertices = np.vstack([vertices, vertices[0]])  # Close the shape
        ax.plot(vertices[:, 0], vertices[:, 1], vertices[:, 2], label=label)
    
    # 初始形状的顶点
    vertices = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1]])
    
    # 计算旋转后的顶点
    alpha, beta = np.radians(30), np.radians(45)  # 旋转角度
    U = tranformMatrix(alpha, beta)  # 使用你的tranformMatrix函数
    rotated_vertices = vertices.dot(U.T)  # 应用旋转矩阵
    
    # 绘制旋转前后的形状
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plot_shape(vertices, ax, "Original")
    plot_shape(rotated_vertices, ax, "Rotated")
    ax.legend()
    plt.show()


if __name__ == '__main__':
    main()