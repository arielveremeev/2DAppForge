class Shape():
    def __init__(self,line):
        parameters=line.split(" ")
        print(parameters)
        self.name=parameters[0]
        self.vertexes=parameters[1]
        self.points=self.SetPoints(parameters[2])
        self.color="black"

    def __str__(self) -> str:
        return f"Name = {self.name} Points = {[str(obj) for obj in self.points]}"

    def SetPoints(self,line):
        coordinates=line.split(";")
        points=[]
        for i in range (0,len(coordinates),2):
            x=coordinates[i]
            y=coordinates[i+1]
            points.append(Point(x,y))
        return points

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

    def SetRadius(self,line):
        para=line.split(" ")
        return para[3]
    def GetString(self):
        pointS=self.PointString()
        pointS=pointS[:-1]
        string=self.name + " " + self.vertexes + " " + pointS + " " +str(self.radius)
        return string
    


def CreateShapes(lines):
    shapes=[]
    for line in lines:
        if("circle" in line):
            shape=Circle(line)
        else:
            shape=Polygon(line)
        print(shape)
        shapes.append(shape)
    return shapes

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

    print('\n')

    newL=''

    count=0
    for shape in shapes:
        newL+=shape.GetString()
        if(count<len(shapes)-2):
            newL+= "\n"

    print(newL)

    newF=open("C:\Projects\\2DAppForge\\assests\shapes2.avsf","w")
    newF.write(newL)
    newF.close()




if __name__ == "__main__":
    main()