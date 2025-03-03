import VisualShape3D.Shape3D as vs
import VisualShape3D.plotable as rd
import numpy as np


highEfficiencyMode = False  # 高效率模式下，会减少一些边，从而提高预览速率


class room():  # 右侧的带遮阳棚小屋
    def __init__(self, xSize, ySize, zSize, roomNumber, style):
        self.xSize = xSize  # 房间的长
        self.ySize = ySize  # 房间的宽
        self.zSize = zSize  # 房间的高
        self.roomNumber = roomNumber  # 房间编号
        self.style = style
        self.floorFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面
        # self.frontFace = vs.Shape('rectangle',ySize,zSize).transform(to=(0,0,0),angles=(0,0,0))   #添加一个平面(前面)
        if self.style == 0:  # 右侧小屋样式
            self.frontFace = vs.Shape('rectangleWithHole', ySize, zSize, 1, 1, ySize - 2, zSize - 2)  # 添加一个平面(前面)
        elif self.style == 1:  # 左侧小屋样式
            self.frontFace = vs.Shape('rectangleWithHole', ySize, zSize, ySize - 5, 0, 4, zSize - 2)  # 添加一个平面(前面)

        self.backFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(后面)
        self.cellFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面(天花板面)
        if self.style == 0:
            self.awnings = vs.Shape('rectangle', ySize, zSize - 3)  # 添加一个平面(遮阳棚板面)
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 7) or (
                self.style == 1):  # 如果highEfficiencyMode配置为True将不会添加模型内部的墙
            self.leftFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(左面)
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 0) or (self.style == 1):  # 根据房间号的规律判断是左边墙还是右边墙可以不用建
            self.rightFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(右面)

    def setRoomPos(self, x, y, z):  # 设置屋子的位置和各个面的旋转方向
        self.floorFace = self.floorFace.transform(to=(x, y, z), angles=(0, -90))
        self.frontFace = self.frontFace.transform(to=(x, y, z), angles=(0, 0))
        self.backFace = self.backFace.transform(to=(self.xSize + x, y, z), angles=(0, 0))
        self.cellFace = self.cellFace.transform(to=(x, y, z + self.zSize), angles=(0, -90))
        if self.style == 0:  # 根据房屋的不同类型，设计开孔矩形的不同开孔位置
            self.awnings = self.awnings.transform(to=(x, y, z + self.zSize), angles=(0, 120))
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 7) or (self.style == 1):  # 这里是效率化处理，
            self.leftFace = self.leftFace.transform(to=(x, y + self.ySize, z), angles=(-90, 0))
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 0) or (
                self.style == 1):  # 如果highEfficiencyMode配置为True将不会添加模型内部的墙
            self.rightFace = self.rightFace.transform(to=(x, y, z), angles=(-90, 0))

    def setCanvas(self, view):  # 将上述的面加入到显示中
        view.add_plot(self.floorFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        view.add_plot(self.frontFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        view.add_plot(self.backFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        view.add_plot(self.cellFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        if self.style == 0:  # 根据房屋的不同类型，设计开孔矩形的不同开孔位置
            view.add_plot(self.awnings, style={'facecolor': 'turquoise', 'edgecolor': 'k'})  # 遮阳棚应该颜色鲜艳一些
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 7) or (self.style == 1):
            view.add_plot(self.leftFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 0) or (self.style == 1):
            view.add_plot(self.rightFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰

class tower():  # 中间的塔楼式建筑
    def __init__(self, xSize, ySize, zSize, roomNumber):
        self.xSize = xSize  # 房间的长
        self.ySize = ySize  # 房间的宽
        self.zSize = zSize  # 房间的高
        self.roomNumber = roomNumber  # 房间编号
        self.floorFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面
        self.frontFace = vs.Shape('rectangle', ySize, zSize).transform(to=(0, 0, 0), angles=(0, 0))  # 添加一个平面(前面)
        # self.frontFace = vs.Shape('rectangleWithHole',ySize,zSize,1,1,ySize-2,zSize-2)  #添加一个平面(前面)
        self.backFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(后面)
        self.cellFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面(天花板面)
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 7):
            self.leftFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(左面)
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 0):
            self.rightFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(右面)

    def setRoomPos(self, x, y, z):  # 配置房间墙面的位置与旋转角度，组合成一个矩形房间
        self.floorFace = self.floorFace.transform(to=(x, y, z), angles=(0, -90))  # 配置墙面旋转角
        self.frontFace = self.frontFace.transform(to=(x, y, z), angles=(0, 0))  # 配置墙面旋转角
        self.backFace = self.backFace.transform(to=(self.xSize + x, y, z), angles=(0, 0))  # 配置墙面旋转角
        self.cellFace = self.cellFace.transform(to=(x, y, z + self.zSize), angles=(0, -90))  # 配置墙面旋转角
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 7):  # 效率化处理，不需要的墙不配
            self.leftFace = self.leftFace.transform(to=(x, y + self.ySize, z), angles=(-90, 0))  # 配置墙面旋转角
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 0):  ##效率化处理
            self.rightFace = self.rightFace.transform(to=(x, y, z), angles=(-90, 0))

    def setCanvas(self, view):  # 将建好的墙加入view中以进行显示
        view.add_plot(self.floorFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        view.add_plot(self.frontFace,
                      style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})  # 材质选择落地窗玻璃
        view.add_plot(self.backFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        view.add_plot(self.cellFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 7):
            view.add_plot(self.leftFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰
        if (highEfficiencyMode is False) or (self.roomNumber % 8 == 0):
            view.add_plot(self.rightFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})  # 材质选择水泥灰

class door():  # 大门
    def __init__(self, xSize, ySize, zSize):
        self.xSize = xSize  # 房间的长
        self.ySize = ySize  # 房间的宽
        self.zSize = zSize  # 房间的高
        self.floorFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面
        # self.frontFace = vs.Shape('rectangle',ySize,zSize).transform(to=(0,0,0),angles=(0,0,0))   #添加一个平面(前面)
        self.frontFace = vs.Shape('rectangleWithHole', ySize, zSize, 1, 0, ySize - 2, zSize - 2)  # 添加一个平面(前面，门洞)
        self.backFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(后面)
        self.cellFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面(天花板面)
        self.awnings = vs.Shape('rectangle', ySize, zSize - 3)  # 添加一个平面(天花板面)
        self.step = vs.Shape('rectangle', ySize, zSize)  # 进门口的台阶
        if (highEfficiencyMode is False):
            self.leftFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(左面)
            self.rightFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(右面)

    def setRoomPos(self, x, y, z):  # 配置房间墙面的位置与旋转角度，组合成一个矩形房间
        self.floorFace = self.floorFace.transform(to=(x, y, z), angles=(0, -90))
        self.frontFace = self.frontFace.transform(to=(x, y, z), angles=(0, 0))
        self.backFace = self.backFace.transform(to=(self.xSize + x, y, z), angles=(0, 0))
        self.cellFace = self.cellFace.transform(to=(x, y, z + self.zSize), angles=(0, -90))
        self.awnings = self.awnings.transform(to=(x, y, z + self.zSize), angles=(0, 90))
        self.step = self.step.transform(to=(x, y, z), angles=(0, 90))
        if (highEfficiencyMode is False):
            self.leftFace = self.leftFace.transform(to=(x, y + self.ySize, z), angles=(-90, 0))
            self.rightFace = self.rightFace.transform(to=(x, y, z), angles=(-90, 0))

    def setCanvas(self, view):  # 将建好的墙加入view中以进行显示
        view.add_plot(self.floorFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
        view.add_plot(self.frontFace, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
        view.add_plot(self.backFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
        view.add_plot(self.cellFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
        view.add_plot(self.awnings, style={'facecolor': 'turquoise', 'edgecolor': 'k'})
        view.add_plot(self.step, style={'facecolor': 'darkred', 'edgecolor': 'k'})
        if (highEfficiencyMode is False):
            view.add_plot(self.leftFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.rightFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})


class roof():
    def __init__(self, xSize, ySize, zSize, style):
        self.xSize = xSize  # 房间的长
        self.ySize = ySize  # 房间的宽
        self.zSize = zSize  # 房间的高
        self.style = style  # 阳台、顶棚的样式
        if self.style == 0:  # 左侧阳台
            self.floorFace1 = vs.Shape('rectangle', ySize - 15 + zSize, -zSize)  # 添加一个平面，阳台地面
            self.floorFace2 = vs.Shape('rectangle', xSize - 15, -zSize)  # 添加一个平面，转角阳台地面
            self.guardrail1 = vs.Shape('rectangle', ySize - 15 + zSize, -zSize)  # 添加一个平面，阳台玻璃护栏
            self.guardrail2 = vs.Shape('rectangle', xSize - 15, -zSize)  # 添加一个平面，阳台玻璃护栏
            self.guardrail3 = vs.Shape('rectangle', zSize, -zSize)  # 添加一个平面，阳台玻璃护栏
            self.guardrail4 = vs.Shape('rectangle', zSize, -zSize)  # 添加一个平面，阳台玻璃护栏
            self.guardrail5 = vs.Shape('rectangle', zSize, -zSize)  # 添加一个平面，阳台玻璃护栏

        elif self.style == 1:  # 左侧瓦屋屋顶
            self.floorFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面
            self.frontFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(前面)
            # self.frontFace = vs.Shape('rectangleWithHole',ySize,zSize,1,1,ySize-2,zSize-2)  #添加一个平面(前面)
            self.backFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(后面)
            self.cellFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面(天花板面)
            self.leftFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(左面)
            self.rightFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(右面)
            self.roof1 = vs.Shape('rectangle', ySize, xSize / 2 / np.cos(np.pi / 6))  # 添加一个平面瓦屋面1
            self.roof2 = vs.Shape('rectangle', ySize, xSize / 2 / np.cos(np.pi / 6))  # 添加一个平面瓦屋面2
            self.roof3 = vs.Shape('triangle', xSize / 2, xSize / 4 / np.cos(np.pi / 6), 0)  # 添加一个平面瓦屋面的侧面三角形
            self.roof4 = vs.Shape('triangle', xSize / 2, xSize / 4 / np.cos(np.pi / 6), 0)  # 添加一个平面瓦屋面的侧面三角形
            self.roof5 = vs.Shape('triangle', xSize / 2, xSize / 4 / np.cos(np.pi / 6), 0)  # 添加一个平面瓦屋面的侧面三角形
            self.roof6 = vs.Shape('triangle', xSize / 2, xSize / 4 / np.cos(np.pi / 6), 0)  # 添加一个平面瓦屋面的侧面三角形

        elif self.style == 2:  # 中央塔楼屋顶
            self.frontFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(前面)
            self.backFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(后面)
            self.leftFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(左面)
            self.rightFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(右面)

        elif self.style == 3:  # 金属屋面
            self.roof = vs.Shape('rectangle', ySize, xSize)  # 添加一个金属屋面

        elif self.style == 4:  # U型玻璃屋面
            self.roof = vs.Shape('rectangle', ySize, xSize)  # U型玻璃屋面

        elif self.style == 5:  # 采光玻璃顶
            self.frontFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(前面)
            self.backFace = vs.Shape('rectangle', ySize, zSize)  # 添加一个平面(后面)
            self.cellFace = vs.Shape('rectangle', ySize, xSize)  # 添加一个平面(天花板面)
            self.leftFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(左面)
            self.rightFace = vs.Shape('rectangle', xSize, zSize)  # 添加一个平面(右面)

    def setRoomPos(self, x, y, z):  # 配置房间墙面的位置与旋转角度，组合成一个矩形房间
        if self.style == 0:
            self.floorFace1 = self.floorFace1.transform(to=(x, y + 15, z), angles=(0, -90))  # 阳台地面
            self.floorFace2 = self.floorFace2.transform(to=(x, y + self.ySize, z), angles=(-90, -90))  # 阳台地面
            self.guardrail1 = self.guardrail1.transform(to=(x - self.zSize, y + 15, z + self.zSize),
                                                   angles=(0, 0))  # 阳台栏杆，玻璃透明
            self.guardrail2 = self.guardrail2.transform(to=(x, y + self.ySize + self.zSize, z + self.zSize),
                                                   angles=(-90, 0))  # 阳台栏杆，玻璃透明
            self.guardrail3 = self.guardrail3.transform(to=(x - self.zSize, y + self.ySize + self.zSize, z + self.zSize),
                                                   angles=(-90, 0))  # 阳台栏杆，玻璃透明
            self.guardrail4 = self.guardrail4.transform(to=(x - self.zSize, y + 15, z + self.zSize),
                                                   angles=(-90, 0))  # 阳台栏杆，玻璃透明
            self.guardrail5 = self.guardrail5.transform(
                to=(x + self.xSize - 15, y + self.ySize, z + self.zSize))  # 阳台栏杆，玻璃透明

        elif self.style == 1:
            self.floorFace = self.floorFace.transform(to=(x, y, z), angles=(0, -90))  # 顶棚附属配件
            self.frontFace = self.frontFace.transform(to=(x, y, z), angles=(0, 0))  # 顶棚附属配件
            self.backFace = self.backFace.transform(to=(self.xSize + x, y, z), angles=(0, 0))  # 顶棚附属配件
            self.cellFace = self.cellFace.transform(to=(x, y, z + self.zSize), angles=(0, -90))  # 顶棚附属配件
            self.leftFace = self.leftFace.transform(to=(x, y + self.ySize, z), angles=(-90, 0))  # 顶棚附属配件
            self.rightFace = self.rightFace.transform(to=(x, y, z), angles=(-90, 0))  # 顶棚附属配件
            self.roof1 = self.roof1.transform(to=(x, y, z + self.zSize), angles=(0, -60))  # 倾斜顶棚
            self.roof2 = self.roof2.transform(to=(x + self.xSize, y, z + self.zSize), angles=(0, 60))  # 倾斜顶棚
            self.roof3 = self.roof3.transform(to=(x + self.xSize / 2, y, z + self.zSize), angles=(-90, 0))  # 补面三角形
            self.roof4 = self.roof4.transform(to=(x + self.xSize / 2, y, z + self.zSize), angles=(90, 0))  # 补面三角形
            self.roof5 = self.roof5.transform(to=(x + self.xSize / 2, y + self.ySize, z + self.zSize),
                                         angles=(-90, 0))  # 补面三角形
            self.roof6 = self.roof6.transform(to=(x + self.xSize / 2, y + self.ySize, z + self.zSize),
                                         angles=(90, 0))  # 补面三角形

        elif self.style == 2:  # 塔楼和右侧房子天台上的一圈围栏
            self.frontFace = self.frontFace.transform(to=(x, y, z), angles=(0, 0))  # 天台上的一圈围栏
            self.backFace = self.backFace.transform(to=(self.xSize + x, y, z), angles=(0, 0))  # 天台上的一圈围栏
            self.leftFace = self.leftFace.transform(to=(x, y + self.ySize, z), angles=(-90, 0))  # 天台上的一圈围栏
            self.rightFace = self.rightFace.transform(to=(x, y, z), angles=(-90, 0))  # 天台上的一圈围栏

        elif self.style == 3:  # 金属屋面
            self.roof = self.roof.transform(to=(x, y, z + self.zSize), angles=(0, -90))

        elif self.style == 4:  # 玻璃屋顶
            self.roof = self.roof.transform(to=(x, y, z + self.zSize), angles=(0, -90))

        elif self.style == 5:  # 采光玻璃顶
            self.frontFace = self.frontFace.transform(to=(x, y, z), angles=(0, 0))
            self.backFace = self.backFace.transform(to=(self.xSize + x, y, z), angles=(0, 0))
            self.cellFace = self.cellFace.transform(to=(x, y, z + self.zSize), angles=(0, -90))
            self.leftFace = self.leftFace.transform(to=(x, y + self.ySize, z), angles=(-90, 0))
            self.rightFace = self.rightFace.transform(to=(x, y, z), angles=(-90, 0))

    def setCanvas(self, view):  # 将建好的墙加入view中以进行显示
        if self.style == 0:
            view.add_plot(self.floorFace1, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.floorFace2, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.guardrail1, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.guardrail2, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.guardrail3, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.guardrail4, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.guardrail5, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})

        elif self.style == 1:
            view.add_plot(self.floorFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.frontFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.backFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.cellFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.leftFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.rightFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.roof1, style={'facecolor': 'sienna', 'edgecolor': 'saddlebrown'})
            view.add_plot(self.roof2, style={'facecolor': 'sienna', 'edgecolor': 'saddlebrown'})
            view.add_plot(self.roof3, style={'facecolor': 'sienna', 'edgecolor': 'saddlebrown'})
            view.add_plot(self.roof4, style={'facecolor': 'sienna', 'edgecolor': 'saddlebrown'})
            view.add_plot(self.roof5, style={'facecolor': 'sienna', 'edgecolor': 'saddlebrown'})
            view.add_plot(self.roof6, style={'facecolor': 'sienna', 'edgecolor': 'saddlebrown'})

        elif self.style == 2:
            view.add_plot(self.frontFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.backFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.leftFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})
            view.add_plot(self.rightFace, style={'facecolor': 'dimgray', 'edgecolor': 'k'})

        elif self.style == 3:
            view.add_plot(self.roof, style={'facecolor': 'lightgray', 'edgecolor': 'w'})  # 金属屋面

        elif self.style == 4:
            view.add_plot(self.roof, style={'facecolor': 'azure', 'edgecolor': 'w', 'alpha': 0.5})  # 玻璃屋顶

        elif self.style == 5:
            view.add_plot(self.frontFace, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.backFace, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.cellFace, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.leftFace, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})
            view.add_plot(self.rightFace, style={'facecolor': 'cornflowerblue', 'edgecolor': 'k', 'alpha': 0.5})


class solarPanel():  # 太阳能板组件
    def __init__(self, xSize, ySize, angle, side):  # 安装的角度以及是否侧着装
        self.xSize = xSize  # 太阳能板的长
        self.ySize = ySize  # 太阳能板的宽
        self.angle = angle  # 太阳能板的倾斜角度
        self.side = side
        self.panel = vs.Shape('rectangle', ySize, xSize)  # 太阳能班板
        if self.angle < 90 and self.side == False:  # 斜着装需要支架
            self.support1 = vs.Shape('rectangle', 0.2, xSize * np.cos(np.deg2rad(angle)))  # 右支架
            self.support2 = vs.Shape('rectangle', 0.2, xSize * np.cos(np.deg2rad(angle)))  # 左支架

    def setRoomPos(self, x, y, z):
        if self.side == False:
            self.panel = self.panel.transform(to=(x, y, z), angles=(0, -self.angle))  # 太阳能板
        else:
            self.panel = self.panel.transform(to=(x, y, z), angles=(-90, 0))  # 太阳能板

        if self.angle < 90 and self.side == False:  # 斜着装需要支架
            self.support1 = self.support1.transform(to=(x + self.xSize * np.sin(np.deg2rad(self.angle)), y, z), angles=(0, 0))
            self.support2 = self.support2.transform(
                to=(x + self.xSize * np.sin(np.deg2rad(self.angle)), y + self.ySize - 0.2, z), angles=(0, 0))  # 支架

    def setCanvas(self, view):
        view.add_plot(self.panel, style={'facecolor': 'navy', 'edgecolor': 'lightgray'})
        if self.angle < 90 and self.side == False:  # 斜着装才需要支架
            view.add_plot(self.support1, style={'facecolor': 'lightgray', 'edgecolor': 'k'})
            view.add_plot(self.support2, style={'facecolor': 'lightgray', 'edgecolor': 'k'})


# How to put a typical room:
# STEP1 Create a target size room
# using room1 = room(xSize,ySize,zSize,roomNumber,style)
# xSize: The length of the room in the X direction
# ySize: The length of the room in the Y direction
# zSize: The length of the room in the Z direction
# roomNumber: The room number sequence
# style: 0:Small room with window  1:Small room without windows

# STEP2 Move this room to the specified location
# using room1.setRoomPos(x,y,z)

# STEP3 Add the room to the canvas
# using room1.setCanvas(view)

if __name__ == "__main__":
    view = rd.OpenView()  # open the canvas view
    room1 = room(5, 5, 5, 0, 0)  # creat a room sized 5*5*5 number 0 and style 0
    room1.setRoomPos(0, 0, 0)  # set this room to (0,0,0) position
    room1.setCanvas(view)  # add this room to the view canvas
    view.show()



# if __name__=="__main__":
#     view = rd.OpenView()       #打开视图

#     room1 = []  #右侧带遮阳棚的小屋
#     for floor in range(3):
#         for i in range(8):
#             room1.append(room(30,5,5,i+floor*8,0))
#             room1[i+floor*8].setRoomPos(0,5*i,floor*5)
#             room1[i+floor*8].setCanvas(view)

#     tower1 = [] #中央玻璃幕墙塔楼
#     for floor in range(4):
#         for i in range(8):
#             if floor==0 and (i==1 or i ==2):
#                 tower1.append(0)
#                 continue        #为门口留空间
#             tower1.append(tower(30,6,5,i+floor*8))
#             tower1[i+floor*8].setRoomPos(0,6*i+40,floor*5)
#             tower1[i+floor*8].setCanvas(view)

#     door1 = []     #入户门
#     for i in range(2):
#         door1.append(door(30,6,5))
#         door1[i].setRoomPos(0,46+6*i,0)
#         door1[i].setCanvas(view)

#     room2 = []       #左侧带斜面顶棚的小屋
#     for floor in range(3):
#         room2.append(room(30,40,5,floor,1))
#         room2[floor].setRoomPos(0,88,5*floor)
#         room2[floor].setCanvas(view)

#     room2 = []       #左侧带斜面顶棚的小屋
#     for floor in range(3):
#         room2.append(room(30,40,5,floor,1))
#         room2[floor].setRoomPos(0,88,5*floor)
#         room2[floor].setCanvas(view)

#     roof1 = []      #左侧的三层阳台
#     for floor in range(3):
#         roof1.append(roof(30,40,3,0))
#         roof1[floor].setRoomPos(0,88,5*floor)
#         roof1[floor].setCanvas(view)

#     roof2=roof(30,40,3,1)   #左侧砖瓦顶
#     roof2.setRoomPos(0,88,5*3)
#     roof2.setCanvas(view)

#     roof3=roof(30,48,2,2)   #中间塔楼的顶部围栏
#     roof3.setRoomPos(0,40,20)
#     roof3.setCanvas(view)

#     roof4=roof(30,40,2,2)   #右侧房间的顶部围栏
#     roof4.setRoomPos(0,0,15)
#     roof4.setCanvas(view)

#     roof5=roof(30,20,2,3)   #金属顶
#     roof5.setRoomPos(0,20,15)
#     roof5.setCanvas(view)

#     roof6=roof(30,20,2,4)   #U型玻璃顶
#     roof6.setRoomPos(0,0,15)
#     roof6.setCanvas(view)

#     roof7=roof(24,20,3,5)   #采光顶
#     roof7.setRoomPos(3,40+22+3,20)
#     roof7.setCanvas(view)

#     pannel1 = []
#     for x in range(4):
#         for y in range(3):
#             pannel1.append(solarPannel(5,5,60,False))   #平屋面太阳能板安装，倾斜30°带支架
#             pannel1[y+3*x].setRoomPos(3+6*x,42+8*y,20)
#             pannel1[y+3*x].setCanvas(view)

#     pannel2 = []
#     for x in range(4):
#         for y in range(3):
#             pannel2.append(solarPannel(5,5,90,False))   #玻璃屋顶上部的太阳能板
#             pannel2[y+3*x].setRoomPos(3+6*x,0+8*y,15+0.3)   #按照阵列展开
#             pannel2[y+3*x].setCanvas(view)

#     pannel3 = []
#     for z in range(3):
#         for x in range(6):
#             pannel3.append(solarPannel(4.5,4.5,90,True))        #侧面墙面太阳能板
#             pannel3[x+6*z].setRoomPos(0.25+5*x,-0.3,0.5+5*z)    #按照阵列展开
#             pannel3[x+6*z].setCanvas(view)

#     #view.show()
#     view.show(hideAxes=True,origin=False)