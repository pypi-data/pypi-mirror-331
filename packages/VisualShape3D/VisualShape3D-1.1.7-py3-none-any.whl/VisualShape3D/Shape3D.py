import numpy as np
import copy
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from VisualShape3D.plotable  import Plotable, OpenView
from VisualShape3D.mathutils import Vector, Matrix3
from VisualShape3D.geomutils import PointInPolygon,PointInSegment
from VisualShape3D.Polygons  import createPolygon, regularPolygon
from VisualShape3D.Polygons  import getPolygonInputDict,add_col,format_dict
from VisualShape3D.Polygons  import isDefaultShape, flip, displace
from VisualShape3D.Polygons  import translate,transform,rotate_by_alpha,rotate_by_beta

class Point(Vector, Plotable):
    def __init__(self, *args, **kwargs):          
        Vector.__init__(self,*args)
        Plotable.__init__(self)
        
    ### Custom get_instance()/iplot()/get_domain()
    def get_instance(self): return self

    def iplot(self, style, ax, **kwargs):
        # defaul setting
        color  = style['color']  if 'color' in style else self.color  
        marker = style['marker'] if 'marker'in style else self.marker  
        alpha  = style['alpha']  if 'alpha' in style else self.alpha 
        label  = style['label']  if 'label' in style else self.label  

        if ax is None:
            ax = self.get_ax()

        ax.scatter(self.x, self.y, self.z, alpha=alpha, c=color, marker=marker)

        if label is not None :
            dz = 0.1
            text = f"{self.x, self.y, self.z}"

            Plotable.text3d(ax, (self.x+dz, self.y, self.z + dz), text, zdir="y", size = 0.2, usetex=False,
                                angle=0, ec="none", fc="k", **kwargs)
            # ax.text(self.x, self.y, self.z, text, zdir=(1, 1, 1))

    def get_domain(self) :
        width = 2

        xlower = self.x - 0.5*width
        xupper = self.x + 0.5*width

        ylower = self.y - 0.5*width
        yupper = self.y + 0.5*width

        zlower = self.z - 0.5*width
        zupper = self.z + 0.5*width


        domain = np.array([(xlower,xupper ), 
                           (ylower,yupper ),
                           (zlower,zupper )])

        return domain.T    

def line_intersects_plane(p0, p1, v1, v2, v3):  
    p0, p1 = np.asarray(p0), np.asarray(p1)
    v1,v2,v3 = np.asarray(v1), np.asarray(v2), np.asarray(v3)
    
    # 计算平面的法向量  
    u = v2 - v1  
    w = v3 - v1  
    n = np.cross(u, w)  
    
    # 平面方程的常量项  
    d = -np.dot(n, v1)  

    # 直线的参数方程  
    direction = p1 - p0  # 直线的方向  
    denominator = np.dot(n, direction)  
    
    # 检查直线是否平行于平面  
    if np.isclose(denominator, 0):  
        print("Line is parallel to the plane.")  
        return None  

    # 计算交点 t  
    t = -(np.dot(n, p0) + d) / denominator  
    
    # 检查交点是否在直线段上  
    if 0 <= t <= 1:  
        intersection = p0 + t * direction  
        return intersection  
    else:  
        return None  

class Segment(Plotable):

    def __init__(self,*args):
        self.P1, self.P2 = Point(), Point()
        if len(args) == 2 :
            self.P1, self.P2 = Point(args[0]),Point(args[1])
            
        if len(args) == 1 :
            self.P2 = Point(args[0])

        self.L  = self.direction()
            
        super().__init__()

            
    def __str__(self):
        name = self.__class__.__name__
        return f"{name}({self.P1},{self.P2})"
            
    def __eq__(self, other):
        if isinstance(other,Segment):
            return  other.P1 == self.P1 and self.P2 == other.P2
        else:
            return False

    def __getitem__(self, item):
        """return one of lines"""
        if item == 0 :
            return self.P1.as_array()
        elif item == 1 :
            return self.P2.as_array()
        else:
            return None

    def __setitem__(self, item, value):
        """set one of Line """
        if item == 0 :
            self.P1 = Point(value)
        elif item == 1 :
            self.P2 = Point(value)

        # print(f"item : {item}, value : {value}")

    def __hash__(self):
        return hash(
        round(self.P1[0],get_sig_figures()),
        round(self.P2[1],get_sig_figures()),
        round(self.P1[0] * self.P2[1] - self.P1[1] * self.P2[0], get_sig_figures()))  

    def __contains__(self, other):
        """Checks if a point in the segment"""
        P = other
        if not isinstance(other,Point):
            P = Point(other)

        P,P1,P2 = P.as_array(),self.P1.as_array(),self.P2.as_array()
        return PointInSegment(P,P1,P2)

    ### Custom get_instance()/iplot()/get_domain()
    def get_instance(self): return self

    def iplot(self, style, ax, **kwargs):

        color     = style['color']     if 'color'     in style else self.color
        linewidth = style['linewidth'] if 'linewidth' in style else self.linewidth 
        alpha     = style['alpha']     if 'alpha'     in style else self.alpha
        node      = style['node']      if 'node'      in style else 'invisible'
        nodecolor = style['nodecolor'] if 'nodecolor' in style else 'r'
        marker    = style['marker']    if 'marker'    in style else 'o'

        p = self.midpoint()

        xs = self.P1.x, p.x, self.P2.x 
        ys = self.P1.y, p.y, self.P2.y
        zs = self.P1.z, p.z, self.P2.z

        vertices = list(zip(xs,ys,zs))
     
        line = Poly3DCollection([vertices],edgecolors=color,linewidths=linewidth, alpha=alpha)

        if ax is None:
            ax = self.get_ax()

        ax.add_collection3d(line)

        if node == 'visible':
            ax.scatter(self.P1.x, self.P1.y, self.P1.z, alpha=alpha, c=nodecolor, marker=marker)
            ax.scatter(self.P2.x, self.P2.y, self.P2.z, alpha=alpha, c=nodecolor, marker=marker)

    def get_domain(self):
        points = np.array([(self.P1.x,self.P1.y,self.P1.z), 
                           (self.P2.x,self.P2.y,self.P2.z)])
        return np.array([points.min(axis=0),points.max(axis=0)])    
    
    def midpoint(self):
        P = self.P1 + self.P2
        return 0.5*P
    
    def direction(self):
        v = self.P2 - self.P1
        return v.unit()

    def intersect(self, poly):
        p0,p1 = self[0], self[1]
        if isinstance(poly,Polygon):
            v1,v2,v3 = poly.vertices[0],poly.vertices[1],poly.vertices[2]
            p = line_intersects_plane(p0, p1, v1, v2, v3)
            return p  
        else :
            return None           

    def broken_at(self,v):
        if self.P1 == v :
            return False
        elif self.P2 == v:
            return False

        else:
            # L1 = Segment(self.P1,v)
            # L2 = Segment(v, self.P2)
            return Polyline([self.P1,v,self.P2])  

class Polygon(Plotable):
    """
    A visible 3D polygon.
    It is iterable , and when indexed, it returns the vertices.
    
    The polygon's vertices are a ndarray of 3D points 
          np.array(N, 2 or 3) for (xyz or xy).

    It requires a open loop, the first point != the end point.

    NOTE:: In future, this object could be locked for calculation once,  
    for a rapid rendering.
    """
    def __init__(self, vertices = [(0,0),(1,0),(0.5,1)]):
               
        if isinstance(vertices,list):
            Points = np.array(vertices)
            
        elif isinstance(vertices,np.ndarray) :
            Points = vertices
            
        else :
            raise ValueError('Polygon : needs vertices as a list/np.array !!!')   
        
        if Points.shape[1] == 2:
            # from Utilities import add_col
            Points = np.hstack((Points,add_col(Points.shape[0])*0))
            
        self.vertices = Points
        self.R0 = self.vertices[0]
        self.n  = self.getNormal()
        self.area = self.getArea()
  
        # Optional processing
        self.path = None
        self.parametric = None
        self.shapely = None

        super().__init__()

        
    def __str__(self):
        name = self.__class__.__name__
        return f"{name}\n{self.vertices}"
 
    def __hash__(self):
        return hash(tuple(sorted(self.vertices, key=lambda p: p.x)))

    def __iter__(self): return iter(self.vertices)

    def __getitem__(self, i): return self.vertices[i]

    def __contains__(self, other):
        if isinstance(other, Point):
            return PointInPolygon(other.coordinates,self.vertices)         # in polygon
           # return abs(other.V * self.n - self.p.V * self.n) < const.get_eps()  # in plane
        else:
            raise NotImplementedError("")    
    
    def getU(self):
        """
            Get transform matrix of the polygon
        """
        v = self.vertices
        if type(v) != np.ndarray :
            v = Array(v) 
        a = Vector(v[1,:] - v[0,:])
        b = Vector(v[2,:] - v[1,:])
        c = a.cross(b)
        #   unitary vectors 
        i = a.unit()
        k = c.unit()
        j = k.cross(i)
        U = np.vstack((i.as_array(),j.as_array(),k.as_array()))
        
        return U
    
    def getNormal(self):
        #
        #   C = A x B 
        #
        v = self.vertices
        A = Vector(v[1,:] - v[0,:])
        B = Vector(v[2,:] - v[1,:])
        C = A.cross(B)        
        return C.unit()   
    
    # transformation from 3D to 2D
    def XYZ_2_ijk(self):
        U  = self.getU()
        R  = self.vertices
        R0 = self.R0      
        r  = U@(R - R0).T  # @ is for vector x matrix
                             
        vertices2D = r.T[:,0:2]
        return vertices2D
    
    def getArea(self):
        xy = self.XYZ_2_ijk()
        x,y = list(zip(*xy))
        m = len(x)
        s = x[m-1]*y[0] - x[0]*y[m-1]
        for i in range(m-1):
            s += x[i]*y[i+1] - y[i]*x[i+1]
            
        return 0.5*s

    ### Custom get_instance()/iplot()/get_domain()
    def get_instance(self): 
        return self
    
    def get_domain(self):
        """
        :returns: opposite vertices of the bounding prism for this object.
        :       ndarray([min], [max])
        """

        # Min/max along the column
        return np.array([self.vertices.min(axis=0),  # min (x,y,z)
                         self.vertices.max(axis=0)]) # max (x,y,z)

    def iplot(self, style, ax, **kwargs):

        plotable3d = self.__get_plotable_data()

        facecolor = self.facecolor  
        edgecolor = self.edgecolor  
        linewidth = self.linewidth  
        alpha     = self.alpha      

        if 'facecolor' in style : facecolor = style['facecolor'] 
        if 'edgecolor' in style : edgecolor = style['edgecolor'] 
        if 'linewidth' in style : linewidth = style['linewidth'] 
        if 'alpha'     in style : alpha     = style['alpha']     

        for polygon in plotable3d:
            polygon.set_facecolor(facecolor)
            polygon.set_edgecolor(edgecolor)
            polygon.set_linewidth(linewidth)
            polygon.set_alpha(alpha)
            ax.add_collection3d(polygon)
    
    def __get_plotable_data(self):
        """
        :returns: matplotlib Poly3DCollection
        :rtype: mpl_toolkits.mplot3d
        """
        # import mpl_toolkits.mplot3d as mplot3d
        # return [mplot3d.art3d.Poly3DCollection([self.vertices])]
        return [Poly3DCollection([self.vertices])]    
       
    # 2d plotting        
    def to_2d(self):
        """
        To calculate the local coordinates of vertices.
        """

        # Create the matrix from global to local systems
        xy = self.XYZ_2_ijk()

        xy[np.isclose(xy, 0.0)] = 0.0
        
        # print(r.shape)
        return Polygon(xy[:, :2])
        
    def plot2d(self, style = ('wheat', 'yellowgreen', 1)):
        """
        It plots the 2D Polygon
        
        Inputs 
           1)style = color, edge_color, alpha ):
               (1)      color: 'default', matplotlib color for polygon
               (2) edge_color : 'k'     , matplotlib color for edge
        :      (3)       alpha:  1,      pacity, float
        :  2) ret: If True, the function returns the figure, so as to add 
                 more elements to the plot or to modify it.
        
        Output: 
          None or axes(matplotlib axes)
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        (color,edge_color,alpha) = style
        path = self.to_2d().get_path()
        domain = self.to_2d().get_domain()[:, :2]

        if color == 'default': color = 'yellowgreen'

        # Plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.add_patch(patches.PathPatch(path, facecolor=color, lw=1, 
                                       edgecolor=edge_color, alpha=alpha))
        ax.set_xlim(domain[0,0],domain[1,0])
        ax.set_ylim(domain[0,1], domain[1,1])

        return plt,ax

    def get_path(self):
        """
        :returns: matplotlib.path.Path object for the z=0 projection of 
            this polygon.
        """
        if self.path == None:
            from matplotlib import path
            
            return path.Path(self.vertices[:, :2]) # z=0 projection!
        return self.path

    def get_area(self):
        """
        :returns: The area of the polygon.
        """
        if self.area is None:
            # self.area = self.to_2d().get_shapely().area
            self.area = self.getArea()
        return self.area

    def intersect(self,line) :
        if isinstance(line, Segment):
            return line.intersect(self)

        elif isinstance(line, Polyline):
            return line.intersect(self)

        else :
            return None

class Polyline(Plotable):
    ### Initialization
    def __init__(self, *points):
        super().__init__()

        vertices = self._init_vertices(*points)

        self.vertices = vertices     # a 2D list of shape N x 3, each line for [x,y,z]
        self.lines = []              # a list of Segment() created by two Point()

        # create segments
        if len(self.vertices)> 1:
            v1 = self.vertices[0]
            for v2 in self.vertices[1:]:
                line = Segment(v1,v2)
                self.lines.append(line)
                v1 = v2   
 

    def __str__(self):
        name = self.__class__.__name__
        return f"{name}{[v for v in self.vertices[0:-1]]}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.vertices})"

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, item):
        """return one of lines"""
        return self.lines[item]

    def __setitem__(self, item, value):
        """set one of Line """
        setattr(self, "lines"[item], value)
        # print(f"item : {item}, value : {value}")

    def __hash__(self):
        return hash(tuple(sorted(self.vertices, key=lambda p: p.x)))

    def _init_vertices(self, *args):
        if len(args) == 0 :
            return []
        
        if len(args) == 1 :
            first = args[0]
            return self.set_points(*first)
        else:
            return self.set_points(*args)

    def set_points(self, *args):
        vertices = []  # np.array([], dtype=object)
        for each in args:
            if type(each) is list or  type(each) is tuple:
                vertices.append(Point(each))

            elif type(each) is np.ndarray :
                vertices.append(Point(each))
    
            elif type(each) is Point :
                vertices.append(each)

        return vertices

    @property
    def P1(self):
        return self.vertices[0]
 
    @property
    def P2(self):
        return self.vertices[-1]

    @P1.setter
    def P1(self, xyz):
        self.vertices[0] = xyz

    @P2.setter
    def P2(self, xyz):
        self.vertices[-1] = xyz

    ### Custom get_instance()/iplot()/get_domain()
    def get_instance(self): return self

    def get_domain(self):
        """
        :returns: opposite corners of the bounding prism for this object.
        :       ndarray([min], [max])
        """
        # Min/max along the column
        m = len(self.vertices)
        vertices = np.zeros((m,3))
        for i in range(m):
            vertices[i] = self.vertices[i].as_list()

        return np.array([vertices.min(axis=0),  # min (x,y,z)
                         vertices.max(axis=0)]) # max (x,y,z)

    def iplot(self, style, ax,**kwargs):
        # style = {'node':'invisible','edgecolor':'default', ...}
        #                 'visible'               'gradient'
        # for 'gradient' 
        default_colors = ['darkgoldenrod', 'goldenrod','gold','khaki','darkkhahi','olive','oilvedrab','darkolivedrab','beige']
        colors = []

        bColors = 0 
        if style.get('color') == 'gradient' :
            bColors = 1

        if 'colors' in style :
            bColors = 2
            colors = style['colors']

        i=0
        for line in self.lines:

            if bColors == 1 :
                style['color'] = default_colors[i]
                i += 1
                i = i % len(default_colors)

            elif bColors == 2 :
                style['color'] = colors[i]
                i += 1
                i = i % len(colors)

            line.iplot(style, ax,**kwargs)

    ### Funcions
    def intersect(self, poly):
        if isinstance(poly,Polygon):
            for i,L in enumerate(self.lines) :
                P = L.intersect(poly) 
                if P is not None :
                    return P
            return None

        else:
            return None   

    def broken_at(self,v):
        V = v
        if not isinstance(v,Point):
            V = Point(v)   
        
        vertices = copy.deepcopy(self.vertices) 
        lines   = copy.deepcopy(self.lines)    
        for i,L in enumerate(lines):
            if V in L:
                two_lines = L.broken_at(V)          
                if two_lines is not None:  
                    vertices.insert(i+1,V)
                    return Polyline(vertices)
        return self  
         

    # def broken_at(self,v):
    #     if v is None:
    #         return None
        
    #     V = v
    #     if not isinstance(v,Point):
    #         V = Point(v)

    #     if len(self.vertices) == 1:
    #         self.append(V)
    #         return 2

    #     elif len(self.vertices) >= 2:
    #         if self.P1 == V :
    #             return None
            
    #         i = 0
    #         for L in self.lines :
    #             if V in L:
    #                 if V == L.P2 :
    #                     return None 
                    
    #                 self.insert_at(i+1,V)
    #                 return i+1
    #             i += 1

    #         return None


    # def insert_at(self,i,v):

    #     if not isinstance(v,Point):
    #         v = Point(v)

    #     if i >= len(self.vertices):
    #         self.append(v)

    #     elif i == 0 :
    #         self.vertices.insert(0,v)
    #         v0 = self.vertices[0]
    #         v1 = self.vertices[1]
    #         self.lines.insert(0, Segment(v0,v1))

    #     else:
    #         v0 = self.vertices[i-1]
    #         v1 = v
    #         v2 = self.vertices[i]
            
    #         # print(f" v0's type is {type(v0)}")
    #         # print(f" v1's type is {type(v1)}")
    #         # print(f" v2's type is {type(v2)}")

    #         self.vertices.insert(i,v)

    #         self.lines.pop(i-1)
    #         self.lines.insert(i-1, Segment(v0,v1))
    #         self.lines.insert(i,Segment(v1,v2))

    # def append(self, v):
    #     v1 = self.vertices[-1]
    #     v2 = v
    #     self.vertices.append(v)
    #     self.lines.append(Segment(v1,v2))

class Shape(Polygon):
    @staticmethod
    def listThem( array):
        return [ tuple(each) for each in array ]
    
    def __init__(self, shape=None, W=6, H=3, A=1, B=1, C=1, D=1, **kwargs):
        args = W,H,A,B,C,D
        self.input_str = ""        
        
        # 如果shape是字符串或None，通过shape名称创建顶点
        if (isinstance(shape, str) and isDefaultShape(shape)) or shape is None:
            vertices, P0 = self.createVertices(shape or 'rectangle', *args, **kwargs)
                
        # 如果shape是列表或NumPy数组，直接使用这些顶点
        elif isinstance(shape, (list, np.ndarray)):
            vertices = np.asarray(shape)
            if vertices.shape[1] == 2:
                vertices = np.hstack((add_col(vertices.shape[0])*0, vertices)) 
                
            self.shapeName = 'polygon'  # 如果直接给定顶点，形状类型设置为多边形
            self.input_str = f"'Polygon', vertices = {self.listThem(vertices)}"
        else:
            # 如果shape是新的字符串命，根据 W 所含数据创建顶点
            if isinstance(shape, str) and isinstance(W, (list, np.ndarray)):
                self.shapeName = shape.lower()
                vertices = np.asarray(W)
                if vertices.shape[1] == 2:
                    vertices = np.hstack((add_col(vertices.shape[0])*0, vertices)) 
                
                self.input_str = f"'{self.shapeName}', vertices = {self.listThem(vertices)}"
            else :
                raise ValueError(f"Unsupported shape type: {type(shape)}")
            
        points = np.asarray(vertices)
        super().__init__(points)      
        self.set_title(self.shapeName)
        if P0 is not None:
            self.R0 = P0
           
    def createVertices(self, shape, *args, **kwargs):
        self.shapeName = shape.lower()
        args_ = list(args)
        P0 = None
     
        if self.shapeName == 'polygon':
            
            vertices = args[0]
            
            if 'W' in kwargs:
                vertices = kwargs['W']                
            if 'w' in kwargs:
                vertices = kwargs['w']                            
            if 'vertices' in kwargs :
                vertices = kwargs['vertices']
            if 'Vertices' in kwargs:
                vertices = kwargs['Vertices']
                
            args_[0] = vertices
            
            self.input_str = f"'Polygon', vertices = {args_[0]}"
            
        elif self.shapeName == 'regularpolygon':
            N  = kwargs['N'] if 'N' in kwargs else  args[0]
            r  = kwargs['r'] if 'r' in kwargs else  args[1]
            n  = kwargs['n'] if 'n' in kwargs else  N
            R  = kwargs['R'] if 'R' in kwargs else  r            
            self.input_str = f"'regularPolygon', n={args[0]}, R={args[1]}"
            args_ = n,R
            P0 = (0,0,0) 
            
        else :                    
            dict_str = getPolygonInputDict(self.shapeName,*args_)
            self.input_str = format_dict(dict_str)
 
        vertices = createPolygon(self.shapeName,*args_)

        # Adapt 2D/3D
        if vertices.shape[1] == 2:
            vertices = np.hstack((add_col(vertices.shape[0])*0, vertices))
         
        return vertices, P0
    
    def __str__(self):
        return f"{len(self.vertices)} vertices :\n{self.vertices}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.input_str})"
            
    def __iter__(self): return iter(self.vertices)
    
    def __getitem__(self, key): return self.vertices[key]

    def set_origin(self,new_origin):
        self.R0 = np.asarray(new_origin)

    # change the object from one position to the new one 
    # of origin point, together with change in orientation.
    # Both angles are around the global YZ
    def transform(self, to = None, angles = None, alpha=0, beta=0, origin = None):
        if origin is None : origin = self.R0
        if to is None : to = self.R0

        if angles is not None :
            vertices = transform(self.vertices, to, angles, origin)
            shape = self.make_shape(vertices = vertices, R0 = to)
        
        else:
            shape = self.move(to, origin)
            if alpha != 0:
                shape = self.rotate_by_alpha(shape, alpha, origin = to)

            if beta != 0 :
                shape = self.rotate_by_beta(shape, beta, origin = to)

        return shape

    def move(self, to = None, origin = None):
        if origin is None : origin = self.R0
        if to is None : to = self.R0
        vertices = translate(self.vertices, to, origin)
        return self.make_shape(vertices = vertices, R0 = to)

    def rotate_by_alpha(self, shape, angle, origin):
        vertices = rotate_by_alpha(shape.vertices, angle, origin)
        return self.make_shape(vertices=vertices, R0=origin)

    def rotate_by_beta(self,shape, angle, origin):
        vertices = rotate_by_beta(shape.vertices, angle, origin)
        return self.make_shape(vertices=vertices, R0=origin)

    def flip(self):
        self.vertices =  flip(self.vertices)
        return self.make_shape()

    def displace(self, by):
        self.vertices = displace(self.vertices, by = by)
        self.R0 = displace(self.R0, by = by)
        return self.make_shape()

    def make_shape(self, vertices = None, R0=None):
       
        if vertices is None :
            newShape = Shape(shape='Polygon',**{'vertices':self.vertices})
        else:
            newShape = Shape(shape='Polygon',**{'vertices':vertices})

        if R0 is None : 
            newShape.R0 = self.R0   
        else : 
            newShape.R0 = R0

        return newShape

    def get_object(self):
        return self

    def formal_arguments(self):
        return self.__repr__()

#  end of class 

def test():
    # view = OpenView()
    p = Point()
    print(f" v = {p}")
    
    # view.add_plot(p)
    
    edge = Segment((1,2,3),(4,5,6))
    print(edge)
    # view.add_plot(edge)
    
    poly = Polygon()
    # view.add_plot(poly)
    
    line = Polyline((0,0,0),(3,1.,2))
    print(line)

    shape = Shape('Triangle')
    print(repr(shape))
    print(shape.formal_arguments())

if __name__ == '__main__':
    test()
