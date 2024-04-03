class Shape():
    def __init__(self):
        self.shapes=[]
        self.points-[]
        self.name=""
        self.vertexes=0
        self.color="black"

    def SetPoints(self,points):
        count=0
        for point in points:
            x=0
            y=0
            if(count%2==0):
                x=point
            else:
                y=point
            if(x!=0 and y!=0):
                temp=Point(x,y)
                self.points.append(temp)
        self.vertexes=count/2

    def PrintPoints(self):
        for point in self.points:
            print(point)
    
    def AddShape(self,name):

        if(name=="circle"):
            shape=Circle()
            self.name=name
        
        else:
            shape=Polygon()
            self.name=name

    
    def CreateShapes(self,lines):
        count=0
        for line in lines:


class Point():
    def __init__(self,x,y):
        self.x=float(x)
        self.y=float(y)



class Polygon(Shape):
    pass

class Circle(Shape):
    def __init__(self):
        self.center=[]
        self.color="black"
        self.radius=0
    def SetRadius(self,radius):
        self.radius=radius
    def SetCenter(self,x,y):
        center=Point(x,y)
        self.center.append(center)


def main():

    file=open('V:\Leva.Downloads\shapes.txt','r')
    count=0
    lines=[]
    while True:
        count+=1
        lines.append(file.readline())

        if not lines[count-1]:
            break
        print("Line{}: {}".format(count, lines[count-1].strip()))
    file.close()

    for line in lines:
        print(line)
    

if __name__ == "__main__":
    main()