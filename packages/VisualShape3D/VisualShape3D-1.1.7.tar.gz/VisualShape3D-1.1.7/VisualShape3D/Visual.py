import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from dataclasses import dataclass, field 
from typing import List, Tuple, Dict, Optional, Any
from VisualShape3D.plotable import Plotable, OpenView, Origin
from VisualShape3D.Shape3D import Point, Shape

def _set_axes_equal(ax):
    """Set 3D plot axes to be equal."""
    x_limits = ax.get_xlim()
    y_limits = ax.get_ylim()
    z_limits = ax.get_zlim()

    max_range = max(
        x_limits[1] - x_limits[0],
        y_limits[1] - y_limits[0],
        z_limits[1] - z_limits[0]
    ) / 2.0

    mid_x = (x_limits[1] + x_limits[0]) * 0.5
    mid_y = (y_limits[1] + y_limits[0]) * 0.5
    mid_z = (z_limits[1] + z_limits[0]) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

# VisualShape3D, 继承自 OpenView
class VisualShape3D(OpenView):

    @staticmethod
    def Usage():
        """  
        提供 VisualShape3D 的使用示例。  

        :return: 使用示例的字符串。  
        """ 
        return  "使用示例: vs3d = VisualShape3D()"  
    
    def itsInput(self):
        return self.__repr__()

    def __init__(self, style=None):
        """  
        初始化 VisualShape3D 实例。  
        :param style: 可选参数，定义形状的样式。默认为 None。  
        """  
        super().__init__()

        self.shapes = []    # 存储所有的形状
        
        if style is None :  # by default
            pass
        else:
            self.set_style(style)

        self.input_str = f"type = {type}"

    def __str__(self):
        """  
        生成当前对象的字符串表示，供 print() 使用。  

        :return: 字符串表示。  
        """  
        return f"VisualShape3D with {len(self.shapes)} shapes." 
        
    def __repr__(self):
        """  
        生成当前对象的详细表示，供调试使用。  
        :return: 详细字符串表示。  
        """ 
        return f"{self.__class__.__name__}({self.input_str})"

    def add_shape(self, shape:Any, style:dict = None):
        """  
        将形状添加到 VisualShape3D 实例中。  

        :param shape: 要添加的形状实例（应为可视形状对象）。  
        :param style: 可选参数，定义此形状的样式。如果未提供，则使用默认样式。  
        """  
        default_style = self.get_style()     

        if style is None :
            style = default_style
        else :
            style = {**default_style, **style}
            # 将两个字典 default_style 和 style 合并成一个新的字典，并将结果赋值给 style 变量
            # 如有重叠，则 style的值会覆盖 default_style的值，因为 style 位于最后。
        shape.set_style(style)  
        self.shapes.append(shape)

    def add_shapes(self,*args):
        for k,v in enumerate(args):
            if type(v) is list :
                for i, shape in enumerate(v):
                    self.add_shape(shape)
            else :
                self.add_shape(v)

    def show(self, elev:float= 20.0, azim :float = -80.0, axes:str = "off", origin:str = "on", **kwargs):
        """  
        展示所有形状于 3D 图中。  

        :param elev: 视角的高度角（以度为单位）。默认为 20.0。  
        :param azim: 视角的方位角（以度为单位）。默认为 -80.0。  
        :param axes: 设定是否显示坐标轴。可选值为 "on" 或 "off"。默认为 "off"。  
        :param origin: 是否显示原点。可选值为 "on" 或 "off"。默认为 "on"。  
        :param kwargs: 额外参数，传递给添加图形时使用（取决于具体形状的可选参数）。  
        :return: 绘制图形的坐标轴对象。  
        """ 
        ax = self.get_ax()
        if ax is None :
            return
      
        ax.view_init(elev, azim)
        hideAxes = axes.lower() == "off"
        if hideAxes :
            ax.set_axis_off()

        if origin.lower() == "on":
            R0 = Origin()
            self.add_plot(R0)
            
        for shape in self.shapes:
            # print(shape.get_title())
            style = shape.get_style()
            self.add_plot(shape, style = style, hideAxes = hideAxes, **kwargs)

        _set_axes_equal(ax)
        plt.show()

        return ax        

class View3D(VisualShape3D):
    def __init__(self, style=None):
        super().__init__(style)
        
    def add_entity(self, entity:Any, style:dict = None):
        self.add_shape(entity,style)

    def add_entities(self,*args):
        self.add_shapes(*args)

# define a manager for models
__modelClassList = []

def modelClass(each_definition):
    __modelClassList.append(each_definition)
    return each_definition

@dataclass  
class Face:  
    indices: List[int]  # 存储顶点的索引  
    style: Dict[str, any] = None
    title: str ="Untitled"
        
    def __post_init__(self):
        
        # 设定默认样式颜色
        if self.style is None :
            self.style = {
                          "facecolor": 'xkcd:beige',  
                          "edgecolor": 'olive',  
                          "linewidth": 1,  
                          "alpha": 1,  
                          }  
            
    def __iter__(self): return iter(self.indices)


@modelClass
class VisualModel(Plotable):
    def __init__(self, title = None):  
        super().__init__()
        
        # 初始化空的顶点库和多边形列表  
        self.vertices = []  # 存储顶点的列表  
        self.faces = []  # 存储多边形对象的列表  
        
        if title is None :
            title = "Untitled"
        self.set_title(title)

        self.hidden = False
        self.input_str = f""

    def __iter__(self): return iter(self.faces)
    
    def get_connection(self):
        connections = []
        for each in self.faces:
            connections.append(each.indices)
        return connections
        
    def add_shape(self, shape:Any, style: Optional[Dict[str, any]] = None, title:Optional[str]=None):  
        """添加一个shape，并更新顶点集合和边的连接"""  
        new_indices = []  
        for vertices in shape:  
            # 检查当前顶点是否已经在库中  
            if tuple(vertices) in self.vertices:  
                # 找到该顶点在库中的索引  
                index = self.vertices.index(tuple(vertices))  
            else:  
                # 如果不在库中，则添加到库，并使用新的索引  
                self.vertices.append(tuple(vertices))  
                index = len(self.vertices) - 1  
            
            # 将顶点的新索引添加到多边形中  
            new_indices.append(index)  

        # 创建一个新的 Face 对象并将其添加到面列表中 
        default_style = self.get_style()     
        if style is None :
            style =  default_style
        else :
            style = {**default_style, **style}
            # 将两个字典 default_style 和 style 合并成一个新的字典，并将结果赋值给 style 变量
            # 如有重叠，则 style的值会覆盖 default_style的值，因为 style 位于最后。
             
        default_title = f"face({len(self.faces)})"
        if type(shape) is Shape:
            default_title = shape.get_title()        
        
        if title is None:
            title = default_title
           
        face = Face(indices=new_indices, style=style, title=title)  
        self.faces.append(face)  

    def get_vertices(self) -> np.ndarray:  
        """返回当前的顶点库"""  
        return np.array(self.vertices)  

    def get_faces(self) -> List[Face]:  
        """返回当前的多边形对象列表"""  
        return self.faces    
    
    # for plotting function
    def get_domain(self):  
        """返回模型的边界"""  
        vertices = self.get_vertices()
        return np.array([vertices.min(axis=0), vertices.max(axis=0)])  
    
    def iplot(self, style, ax=None, **kwargs):
        # 确保这个方法有效 
        if ax is None:  
            ax = self.get_ax() 
            
        title = kwargs["title"] if 'title' in kwargs  else self.get_title()
        if title is True:
            self.write_title()
          
        mode = kwargs["plot_mode"] if 'plot_mode' in kwargs  else "all_at_once"   
        if mode.lower() == "face_by_face":
            self.iplot_face_by_face(style, ax=ax, **kwargs)
        else :
            self.iplot_all_at_once(style, ax=ax, **kwargs)
            
    def iplot_face_by_face(self, style, ax=None, **kwargs):  
        vertices = self.get_vertices()  
        for facet in self.faces:  
            face = [vertices[i] for i in facet] 
            face = Poly3DCollection([face])
            face.set_facecolor(facet.style["facecolor"])
            face.set_edgecolor(facet.style["edgecolor"])
            face.set_linewidth(facet.style["linewidth"])
            face.set_alpha(facet.style["alpha"])
            ax.add_collection3d(face)
            
    def iplot_all_at_once(self, style, ax=None, **kwargs):  
        vertices = self.get_vertices()  
        faces = []  
        for facet in self.faces:  
            face = [vertices[i] for i in facet]  
            faces.append(face)  

        poly3d = Poly3DCollection(faces)  

        style = self.get_style()  
        poly3d.set_facecolor(style['facecolor'])
        poly3d.set_edgecolor(style['edgecolor'])
        poly3d.set_linewidth(style['linewidth'])
        poly3d.set_alpha(style['alpha'])
                      
        ax.add_collection3d(poly3d)  

    def write_title(self):
        ax = self.get_ax()
        
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        zmin, zmax = ax.get_zlim()

        # set the grid
        x = [xmin, xmin, xmin]
        y = [ymin, ymin, ymin]
        z = [zmin, zmin, zmin]
        
        dx = 0.15*(xmax - xmin)
        dy = 0.15*(ymax - ymin)
        dz = 0.15*(zmax - zmin)

        title = self.get_title()
        size = len(title)
        Plotable.text3d(ax, ( (xmax - dx)/2, (ymin-2*dy)/2, zmin), 
                        title, zdir="z", size=.1, usetex=False,ec="none", fc="k")        
        
        
    def get_instance(self):  
        return self  # 返回当前的 Face 实例 
    
    # helper functions
    @staticmethod
    def Usage():
        return  f"class myClass({__class__.__name__})： ... ..."
    
    def itsInput(self):
        return self.__repr__()    

    def __str__(self):
        return f"{self.__repr__()} : \n vertices {len(self.vertices)}"
        
    def __repr__(self):
        return f"{__class__.__name__}({self.input_str})"  

    def turn_off(self):
        self.hidden = True

    def turn_on(self):
        self.hidden = False
    
    def show(self, elev= 20.0, azim = -80.0, axes = "off", origin = "off", style = {}, **kwargs):
        
        """自我展示模型"""
        ax = self.get_ax()
        if ax is not None:
            self.close()   #  close the existing figure

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.view_init(elev, azim)

        self.set_ax(ax)
        self.set_fig(fig)

        hideAxes = axes.lower() == "off"
        if hideAxes :
            ax.set_axis_off()

        if origin.lower() == "on":
            R0 = Origin()
            self.add_plot(R0)

        self.plot( style = style, ax = ax, **kwargs )
        
        _set_axes_equal(ax)
        plt.show()

@modelClass
class Cube(VisualModel):
    # 验证
    @staticmethod
    def Usage():
        return  f"obj = {__class__.__name__}(width=1,height=1,length=1)"

    def __init__(self,width=1,height=1,length=1):
        super().__init__()

        self.set_title('Cube')
        self.create(width,height,length)
        self.input_str = f" width={width}, height={height} ,length={length} "
 
    def create(self,width,height,length):
        w,l,h = width, length, height
        
        # 定义立方体的顶点坐标，self.vertices = vertices  
        vertices = np.array([[0, 0, 0],  
                             [w, 0, 0],  
                             [w, l, 0],  
                             [0, l, 0],  
                             [0, 0, h],  
                             [w, 0, h],  
                             [w, l, h],  
                             [0, l, h]])  
        
        # 定义立方体的面，每面由顶点的索引表示, self.faces = faces  
        faces = [[vertices[j] for j in [0, 1, 2, 3]],  # 底面  
                 [vertices[j] for j in [4, 5, 6, 7]],  # 顶面  
                 [vertices[j] for j in [0, 1, 5, 4]],  # 前面  
                 [vertices[j] for j in [2, 3, 7, 6]],  # 后面  
                 [vertices[j] for j in [0, 3, 7, 4]],  # 左面  
                 [vertices[j] for j in [1, 2, 6, 5]]]  # 右面  
        
        # 上述结果用于检验下面标准建模过程的正确性
        # 定义多边形  
        floor = Shape("Polygon", faces[0])  
        roof  = Shape("Polygon", faces[1])  
        front = Shape("Polygon", faces[2]) 
        back  = Shape("Polygon", faces[3]) 
        left  = Shape("Polygon", faces[4]) 
        right = Shape("Polygon", faces[5]) 
        
        # 逐步用多边形建模型，其自动生成 self.vertices, self.faces  
        self.add_shape(floor)  
        self.add_shape(roof,style={"facecolor":'r',"alpha":0.6})  
        self.add_shape(front) 
        self.add_shape(back)  
        self.add_shape(left)  
        self.add_shape(right)

@modelClass
class Sphere(VisualModel): 
    # 直接底层操作
    @staticmethod
    def Usage():
        return  f"obj = {__class__.__name__}(radius, center=(0, 0, 0), resolution=50)" 
    def __init__(self, radius, center=(0, 0, 0), resolution=50):
        super().__init__(title="Sphere")
        self.radius = radius  
        self.center = np.array(center)  
        self.resolution = resolution  
        self.vertices = self.create_vertices()  
        self.faces = self.create_faces()  

    def create_vertices(self):  
        # 使用极坐标生成球体的顶点  
        u = np.linspace(0, 2 * np.pi, self.resolution)  
        v = np.linspace(0, np.pi, self.resolution)  

        x = self.radius * np.outer(np.cos(u), np.sin(v)) + self.center[0]  
        y = self.radius * np.outer(np.sin(u), np.sin(v)) + self.center[1]  
        z = self.radius * np.outer(np.ones(np.size(u)), np.cos(v)) + self.center[2]  

        return np.column_stack((x.flatten(), y.flatten(), z.flatten()))  

    def create_faces(self):  
        faces = []  
        for i in range(self.resolution - 1):  
            for j in range(self.resolution - 1):  
                v0 = i * self.resolution + j  
                v1 = v0 + 1  
                v2 = (i + 1) * self.resolution + j + 1  
                v3 = v2 - 1  
                faces.append([v0, v1, v2, v3])  # 面片  
                 
        return faces  

#     def plot(self, ax=None, color='b', alpha=0.6):  
#         if ax is None:  
#             fig = plt.figure()  
#             ax = fig.add_subplot(111, projection='3d')  

#         for face in self.faces:  
#             v0, v1, v2, v3 = self.vertices[face]  
#             poly3d = [[v0, v1, v2, v3]]  
#             face_collection = Poly3DCollection(poly3d, color=color, alpha=alpha)  
#             ax.add_collection3d(face_collection)  

#         ax.set_xlabel('X')  
#         ax.set_ylabel('Y')  
#         ax.set_zlabel('Z')  
#         ax.set_xlim([-self.radius, self.radius])  
#         ax.set_ylim([-self.radius, self.radius])  
#         ax.set_zlim([-self.radius, self.radius])  
#         plt.show() 





# create a namelist of these function
__classNames = [each.__name__ for each in __modelClassList ]
def visualModelList():
    return __classNames

def howtoUseClass(className):
    name = [x.lower() for x in visualModelList()]
    i = name.index(className.lower())
    return __modelClassList[i].Usage()


# 使用示例
def demo_model():
    vs3d = VisualModel()
    vs3d.add_shape("Sphere")
    vs3d.add_shape("Cube")
    vs3d.show()

def demo_cube():
    cube = Cube(5, 3, 2)
    cube.show(elev= 20.0, azim = -45.0, style={'facecolor':'y'})

if __name__ == "__main__":
    demo_cube()