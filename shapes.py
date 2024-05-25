import json
import math

"""
    class shape for storing and manipulating 2d shapes in the following format:
    <shape_name> <num_of_vertexes> <x1>;<y1>;...<xN>;<yN> <optional radius>
    shape name: is a string representing the name of the shape either a square,triangle,circle or polygon
    num_of_vertexes: is an integer representing the number of vertexes in the shape
    x1,y1,...xN,yN: are float values representing the x and y coordinates of the vertexes in the shape
"""
class Shape():
    def __init__(self,line):
        """
        The function initializes attributes based on input parameters parsed from a line of text in a predefined format.
        
        """
        parameters=line.split(" ")
        print(parameters)
        self.name=parameters[0]
        self.vertexes=parameters[1]
        self.center = Point(0,0)
        self.SetPoints(parameters[2])
        self.color="black"

    def __str__(self) -> str:
        """
        The `__str__` function returns a string representation of an object, including its name and points.
        """
        return f"Name = {self.name} Points = {[str(obj) for obj in self.points]}"

    def SetPoints(self,line):
        """
        This function takes a line of coordinates, creates Point objects for each pair of coordinates,
        calculates the center point, and stores all points in a list.
        
        """
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
        """
        This function calculates the average coordinates of the vertices in a shape to determine its center point.
        """
        avgX,avgY=0,0
        for vertex in self.points:
            avgX += vertex.x
            avgY += vertex.y
        numberOfVertexes = len (self.points)
        self.center = Point(avgX/numberOfVertexes,avgY/numberOfVertexes)


    def PrintPoints(self):
        """
        This debbugging function iterates through a list of points and prints each point.
        """
        for point in self.points:
            print(point)

    def PointString(self):
        """
        This debbuging function iterates through a list of points and concatenates their X and Y
        coordinates into a string separated by semicolons.
        """
        string=''
        for point in self.points:
            cord=point.GetX() + ";" + point.GetY() + ";"
            string+=cord
        return string

    def GetString(self):
        """
        The `GetString` function in Python constructs and returns a string by combining the object's name,
        vertexes, and a modified point string.
        """
        pointS=self.PointString()
        pointS=pointS[:-1]
        string=self.name + " " + self.vertexes + " " + pointS
        return string
    def MoveShape(self,Mx : float,My : float):
        """
        The `MoveShape` function updates the x and y coordinates of each point in a shape by adding the
        specified values and then updates the center of the shape.
        
        """
        for point in self.points:
            point.x+=Mx
            point.y+=My
        self.UpdateCenter()
    def ScaleShape(self,Sf : float):
        """
        This function scales a shape around its center by a given scale factor.
        the scaling is done by moving the vertex on a line thats intercepts the center of the shape and the coresponding vertex
        scale factor is a float value representing the scale factor in percentage around center of the shape
        """
        for point in self.points:
            point.x = self.center.x + (point.x - self.center.x) * Sf
            point.y = self.center.y + (point.y - self.center.y) * Sf
    def RotateShape(self,rotate_angle : float):
        """
        The RotateShape function rotates a shape around its center by a specified angle in radians.
        spins the shape by 5 degrees using a trigonometrical function to recalculate the new vertex positions
        rotate angle is a float value representing the angle in degrees around center of the shape
        """
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
            

"""
    class point storing the x and y coordinates of a point in 2d space
"""
class Point():
    def __init__(self,x,y):
        """
        This constructor that initializes two instance variables x and y with floating-point values.
        """
        self.x=float(x)
        self.y=float(y)

    def __str__(self) -> str:
        """
        The above function defines a `__str__` method that returns a string representation of an object with attributes `x` and `y`.
        """
        return f"[{str(self.x)},{str(self.y)}]"
    
    def GetX(self):
        """
        The function GetX returns the value of the attribute x as a string.
        """
        return str(self.x)
    def GetY(self):
        """
        The GetY function returns the y attribute of an object as a string.
        """
        return str(self.y)
    


"""
    class polygon inheriting from shape class to distinguish between different types of shapes
"""
class Polygon(Shape):
    pass

"""
    class circle inheriting from shape class to distinguish between different types of shapes and cases specific circle functions
"""
class Circle(Shape):
    def __init__(self,line):
        """
        The above function is a constructor in Python that initializes an object with a given line and sets
        its radius based on the input line.
        """
        Shape.__init__(self,line)
        self.radius=self.SetRadius(line)

    def __str__(self) -> str:
        """
        The above function overrides the `__str__` method to return a string representation of a Circle
        object including its radius.
        """
        return super(Circle,self).__str__() + "radius = " + str(self.radius)

    def SetRadius(self,line) -> float:
        """
        This function takes a string input, splits it by spaces, and returns the fourth element as a float.
        """
        para=line.split(" ")
        return float(para[3])
    def GetString(self):
        """
        This function returns a string containing the name, vertexes, point string, and radius of an object.
        """
        pointS=self.PointString()
        pointS=pointS[:-1]
        string=self.name + " " + self.vertexes + " " + pointS + " " +str(self.radius)
        return string
    def ScaleShape(self,Sf : float):
        """
        This function scales the radius of a shape by a given factor `Sf`.
        """
        self.radius*=Sf
    


def CreateShapes(lines):
    """
    This function takes a list of lines as input, creates shapes based on the content of
    each line (either a circle or a polygon), and returns a dictionary of shape objects with unique IDs.
    """
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
    """
    This function determines whether to create a Circle or Polygon object based on the input line.
    """
    shape = None
    if("circle" in line):
        shape = Circle(line)
    else:
        shape = Polygon(line)
    print(shape)
    return shape


"""
    class for encoding shape objects into json format
"""
class ShapeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        This function overrides the default JSON encoding behavior to handle instances of the `Shape` class by calling the `GetString` method.
        """
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