import json
import math

class Shape():
    def __init__(self,line):
        parameters=line.split(" ")
        print(parameters)
        self.name=parameters[0]
        self.vertexes=parameters[1]
        self.center = Point(0,0)
        self.SetPoints(parameters[2])
        self.color="black"

    def __str__(self) -> str:
        return f"Name = {self.name} Points = {[str(obj) for obj in self.points]}"

    def SetPoints(self,line):
        coordinates=line.split(";")
        self.points=[]
        avgX,avgY=0,0
        for i in range (0,len(coordinates),2):
            x=coordinates[i]
            y=coordinates[i+1]
            avgX+=float(x)
            avgY+=float(y)
            self.points.append(Point(x,y))
        numberOfVertexes = len (self.points)
        self.center = Point(avgX/numberOfVertexes,avgY/numberOfVertexes)

    def UpdateCenter(self):
        avgX,avgY=0,0
        for vertex in self.points:
            avgX += vertex.x
            avgY += vertex.y
        numberOfVertexes = len (self.points)
        self.center = Point(avgX/numberOfVertexes,avgY/numberOfVertexes)


    def PrintPoints(self):
        for point in self.points:
            print(point)

    def PointString(self):
        string=''
        for point in self.points:
            cord=point.GetX() + ";" + point.GetY() + ";"
            string+=cord
        return string

    def GetString(self):
        pointS=self.PointString()
        pointS=pointS[:-1]
        string=self.name + " " + self.vertexes + " " + pointS
        return string
    def MoveShape(self,Mx : float,My : float):
        for point in self.points:
            point.x+=Mx
            point.y+=My
        self.UpdateCenter()
    def ScaleShape(self,Sf : float):
        ''' scale factor is a float value representing the scale factor in percentage around center of the shape'''        
        for point in self.points:
            point.x = self.center.x + (point.x - self.center.x) * Sf
            point.y = self.center.y + (point.y - self.center.y) * Sf
    def RotateShape(self,rotate_angle : float):
        ''' rotate angle is a float value representing the angle in degrees around center of the shape'''        
        # Convert the angle from degrees to radians
        angle_rad = math.radians(rotate_angle)
        print (f"Shape rotate center [{self.center.x},{self.center.y}]")
        for point in self.points:
            # Calculate the position relative to the center
            rel_x = point.x - self.center.x
            rel_y = point.y - self.center.y
            
            # Apply the rotation transformation
            new_rel_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
            new_rel_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
            
            # Calculate the new vertex position
            point.x = self.center.x + new_rel_x
            point.y = self.center.y + new_rel_y
            

class Point():
    def __init__(self,x,y):
        self.x=float(x)
        self.y=float(y)

    def __str__(self) -> str:
        return f"[{str(self.x)},{str(self.y)}]"
    
    def GetX(self):
        return str(self.x)
    def GetY(self):
        return str(self.y)
    


class Polygon(Shape):
    pass

class Circle(Shape):
    def __init__(self,line):
        Shape.__init__(self,line)
        self.radius=self.SetRadius(line)

    def __str__(self) -> str:
        return super(Circle,self).__str__() + "radius = " + str(self.radius)

    def SetRadius(self,line) -> float:
        para=line.split(" ")
        return float(para[3])
    def GetString(self):
        pointS=self.PointString()
        pointS=pointS[:-1]
        string=self.name + " " + self.vertexes + " " + pointS + " " +str(self.radius)
        return string
    def ScaleShape(self,Sf : float):
        self.radius*=Sf
    


def CreateShapes(lines):
    shapes={}
    shapeid=0
    for line in lines:
        shapeid+=1
        if("circle" in line):
            shapes.update({shapeid:Circle(line)})
        else:
            shapes.update({shapeid:Polygon(line)})
        print(shapes[shapeid])
    return shapes

def CreateShape(line)->Shape:
    shape = None
    if("circle" in line):
        shape = Circle(line)
    else:
        shape = Polygon(line)
    print(shape)
    return shape


class ShapeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Shape):
            return obj.GetString()
        return json.JSONEncoder.default(self, obj)


def main():

    file=open('V:\Leva.Downloads\shapes.txt','r')
    count=0
    lines=[]
    while True:
        count+=1
        line = file.readline()
        line=line.rstrip()
        
        if not line:
            break
        lines.append(line)
        print("Line{}: {}".format(count, lines[count-1].strip()))
    file.close()

    count=0

    print("\n")

    shapes=CreateShapes(lines)
    print(shapes)
    print(json.dumps(shapes,cls=ShapeJsonEncoder))
    print('\n')

 




if __name__ == "__main__":
    main()