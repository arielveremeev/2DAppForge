import tkinter as tk
import math
from PIL import Image, ImageDraw

class DrawCanvas(tk.Canvas):
    def __init__(self,parent,callbacks):
        tk.Canvas.__init__(self,parent,bg="white")
        
        self.callbacks=callbacks
        self.selectedshape=""
        self.selectedtype=""
        self.selectededit=""
        self.canvas_status=False

        self.start_x = None
        self.start_y = None
        self.current_shape_item = None
        self.debug_shapes = []
        self.aggregate=1.0
        self.aggregate_angle=0



    def change_draw_type(self,text):
        if text:
            self.selectedtype=text
            if(self.selectedtype == "edit"):
                self.toggle_edit()
            else:
                self.toggle_draw()
            print("current drawing type is " + str(self.selectedtype))

    def change_shape_type(self,text):
        if text:
            self.selectedshape=text
            print("current shape is " + str(self.selectedshape))
            if text == "polygon":
                self.unbind("<B1-Motion>")
                self.unbind("<ButtonRelease-1>")
                self.bind("<Button-1>", self.draw_polygon)
                self.bind("<Double-Button-1>",self.stop_polygon)

                self.PolyPoints=[]
                self.polygon=None
            else:
                self.toggle_draw()

    def change_edit_type(self,text):
        if text:
            self.selectededit=text
            print("selected edit type is " + self.selectededit)
            

    def toggle_draw(self):
        self.canvas_status=True

        self.bind("<Button-1>", self.start_draw)
        self.bind("<B1-Motion>", self.draw_shape)
        self.bind("<ButtonRelease-1>", self.stop_draw)

    def toggle_edit(self):
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")

        self.bind("<Button-1>", self.on_shape_click)
        #self.bind("<B1-Motion>", self.move_shape)
        #self.bind("<ButtonRelease-1>", self.stop_move)

    def on_shape_click(self, event):

        print("on shape pressed")
        for shape_id in self.debug_shapes:
            self.delete(shape_id)
        self.debug_shapes = []
        self.drag_shape_id = self.find_closest(event.x, event.y)[0]
        if self.drag_shape_id:
            print("shape pressed")
            self.draw_shape_bb(self.drag_shape_id)
            self.start_drag_x,self.start_drag_y=event.x,event.y
            self.move_x,self.move_y=0,0
            self.start_coords=self.coords(self.drag_shape_id)
            if self.selectededit == "move_shape":
                self.bind("<B1-Motion>", self.move_shape)
                self.bind("<ButtonRelease-1>", self.stop_move)
            elif self.selectededit == "scale_shape":
                self.debug_shapes = self.draw_scale_star3debug(self.drag_shape_id)
                self.bind("<MouseWheel>", self.scale_shape)
                self.bind('<Double-Button-1>',self.send_scale)
            elif self.selectededit == "rotate_shape":
                self.debug_shapes = self.draw_scale_star3debug(self.drag_shape_id)
                self.bind("<MouseWheel>", self.rotate_shape)
                self.bind('<Double-Button-1>',self.send_rotate)

    def move_shape(self,event):
        if self.drag_shape_id:
            delta_x = event.x - self.start_drag_x
            delta_y = event.y - self.start_drag_y
            self.move(self.drag_shape_id,delta_x,delta_y)
            self.draw_shape_bb(self.drag_shape_id)
            self.start_drag_x,self.start_drag_y=event.x,event.y
            self.move_x+=delta_x
            self.move_y+=delta_y

    def stop_move(self,event):
        self.callbacks["on_shape_move"](self.drag_shape_id,self.move_x,self.move_y)
        self.drag_shape_id=None

    def scale_shape(self,event):
        if self.drag_shape_id:
            size =(5*event.delta)/120
            print(self.size)
            if len(self.start_coords) == 4:
                cCoords=self.coords(self.drag_shape_id)
                self.coords(self.drag_shape_id,cCoords[0] - size, cCoords[1] - size, cCoords[2] + size, cCoords[3] + size)
            else:
                scale_factor=0
                avgX,avgY=self.calc_center(self.coords(self.drag_shape_id))
                newX,newY=None,None
                coords=self.coords(self.drag_shape_id)
                cCoords=[]
                scale_factor = 1.05 if event.delta > 0 else 0.95
                self.aggregate =self.aggregate * scale_factor
                for i in range(0,len(self.coords(self.drag_shape_id)),2):
                    x=coords[i]
                    y=coords[i+1]
                    dir_x = x - avgX
                    dir_y = y - avgY
                
                    newX = avgX + dir_x * scale_factor
                    newY = avgY + dir_y * scale_factor

                    print("aggregate",self.aggregate)
                    cCoords.append(newX)
                    cCoords.append(newY)
                self.coords(self.drag_shape_id,cCoords)
            self.draw_shape_bb(self.drag_shape_id)

    def send_scale(self,event):
        print(self.aggregate)
        self.callbacks["on_shape_scale"](self.drag_shape_id,self.aggregate)
        self.aggregate=1.0
        self.drag_shape_id=None

    def rotate_shape(self,event):
        if self.drag_shape_id:
            angle=5 if event.delta > 0 else -5
            avgX,avgY=self.calc_center(self.coords(self.drag_shape_id))
            cCoords=[]
            # Convert the angle from degrees to radians
            angle_rad = math.radians(angle)
            
            # Create a new list for the rotated vertices
            rotated_vertices = []

            self.aggregate_angle+=angle
            for i in range(0, len(self.coords(self.drag_shape_id)), 2):
                x = self.coords(self.drag_shape_id)[i]
                y = self.coords(self.drag_shape_id)[i + 1]
                
                # Calculate the position relative to the center
                rel_x = x - avgX
                rel_y = y - avgY
                
                # Apply the rotation transformation
                new_rel_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
                new_rel_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
                
                # Calculate the new vertex position
                new_x = avgX + new_rel_x
                new_y = avgY + new_rel_y
                
                # Append the new vertex to the rotated vertices list
                cCoords.append(new_x)
                cCoords.append(new_y)

                
            self.coords(self.drag_shape_id,cCoords)
            self.draw_shape_bb(self.drag_shape_id)

    def send_rotate(self,event):
        print(self.aggregate)
        self.callbacks["on_shape_rotate"](self.drag_shape_id,self.aggregate_angle)
        self.aggregate_angle=0
        self.drag_shape_id=None

    def calc_center(self,coords):
        count=0
        avgX,avgY=0,0
        for cord in coords:
            if count%2==0:
                avgX+=cord
            else:
                avgY+= cord
            count+=1
        avgX=avgX/(count/2)
        avgY=avgY/(count/2)
        return [avgX,avgY]
    
    def draw_scale_star3debug(self,Sid):
        if Sid:
            coords = self.coords(Sid)
            center_x,center_y = self.calc_center(coords)
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            shape_ids = []

            for i in range(0, len(coords), 2):
                x = coords[i]
                y = coords[i+1]

                # Calculate the slope of the line
                if x != center_x:
                    slope = (y - center_y) / (x - center_x)
                else:
                    slope = float('inf')

                # Calculate the y-intercept of the line
                if slope != float('inf'):
                    intercept = y - slope * x
                else:
                    intercept = float('inf')

                # Calculate the x and y coordinates of the line's intersection with the canvas boundaries
                if slope != 0:
                    if x < center_x:
                        x1 = 0
                        y1 = intercept
                        x2 = center_x #canvas_width
                        y2 = center_y #slope * x2 + intercept
                    else:
                        x1 = center_x
                        y1 = center_y
                        x2 = canvas_width
                        y2 = slope * x2 + intercept
                else:
                    x1 = x
                    y1 = 0
                    x2 = x
                    y2 = canvas_height

                # Draw the line
                line_id = self.create_line(x1, y1, x2, y2, fill="green")
                shape_ids.append(line_id)

            return shape_ids
        return []


    def edit_shape(self,Sid,details:list):
        if Sid and details:
            print(self.coords(int(Sid)))
            shapeProperties = details.split(' ')
            if shapeProperties[0] == "square":
                coords = shapeProperties[2].split(";")
                self.coords(int(Sid),float(coords[0]), float(coords[1]), float(coords[6]), float(coords[7]))
            elif(shapeProperties[0] == "triangle" or shapeProperties[0] == "polygon"):
                Scoords=shapeProperties[2].split(";")
                Fcoords=self.convert_poly_2float(Scoords)
                self.coords(int(Sid),Fcoords)
            elif shapeProperties[0] == "circle":
                radius=shapeProperties[3]
                Scoords = shapeProperties[2].split(";")
                Ccoords=self.get_circle_points(radius,Scoords)
                self.coords(int(Sid),float(Ccoords[0]), float(Ccoords[1]), float(Ccoords[2]), float(Ccoords[3]))
                
    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.selectedshape == "rectangle":
            self.current_shape_item = self.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="black"
            )

        elif self.selectedshape == "triangle":
            self.current_shape_item=self.create_polygon(
                self.start_x,self.start_y,self.start_x,self.start_y,self.start_x,self.start_y,outline="black",fill=""
            )
            
        elif self.selectedshape == "circle":
            self.current_shape_item = self.create_oval(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="black"
            )

    def draw_shape(self, event):
        if self.current_shape_item:
            if(self.selectedshape=="circle"):
                x= event.x
                y=(x-self.start_x) + self.start_y
                self.coords(self.current_shape_item, self.start_x, self.start_y, x, y)
            elif(self.selectedshape=="triangle"):
                if(event.x > self.start_x):
                    self.coords(self.current_shape_item,self.start_x,self.start_y,event.x,event.y,self.start_x-(event.x-self.start_x),event.y)
                else:
                    self.coords(self.current_shape_item,self.start_x,self.start_y,event.x,event.y,(self.start_x - event.x) + self.start_x,event.y)
            else:
                x, y = event.x, event.y
                self.coords(self.current_shape_item, self.start_x, self.start_y, x, y)
    
    def stop_draw(self, event):
        Ccoords=self.coords(self.current_shape_item)
        shape=""
        print(Ccoords)
        if(self.selectedshape == "rectangle"):
            coords=str(Ccoords[0]) + ";"+str(Ccoords[1]) + ";" + str(Ccoords[2]) + ";" + str(Ccoords[1]) + ";" + str(Ccoords[0])+ ";" + str(Ccoords[3])+ ";" + str(Ccoords[2])+ ";" + str(Ccoords[3])
            shape="square 4 "+ coords
            print(shape)

        elif(self.selectedshape == "triangle"):
            coords=self.convert_poly_2str(Ccoords)
            shape="triangle 3 "+coords
            print(shape)

        elif(self.selectedshape=="circle"):
            print(Ccoords[0])
            print(Ccoords[1])
            print(Ccoords[2])
            print(Ccoords[3])
            center=self.get_center(Ccoords[0],Ccoords[1],Ccoords[2],Ccoords[3])
            radius=self.get_radius(Ccoords[ 0],Ccoords[2])
            CenCord=str(center[0]) + ";" + str(center[1])
            shape="circle 1 " + str(CenCord) + " " + str(radius)

        self.delete(self.current_shape_item)
        self.callbacks["on_shape_finish"](shape)
        self.current_shape_item = None

    def draw_polygon(self,event):
        self.PolyPoints.append((event.x, event.y))
        self.delete(self.polygon)
        self.polygon=self.create_polygon(self.PolyPoints,outline="black", fill="")
        print(self.coords(self.polygon))

    def stop_polygon(self,event):
        Ccoords=self.coords(self.polygon)
        coords=self.convert_poly_2str(Ccoords)
        vertexes=len(self.PolyPoints)
        shape="polygon" + " " + str(vertexes) + " " + coords 
        print(shape)

        self.delete(self.polygon)

        self.callbacks["on_shape_finish"](shape)

        self.polygon=None
        self.PolyPoints=[]

    def add_shape(self,details)->list:
        shapeProperties = details.split(' ')
        if shapeProperties[0] == "square":
           coords = shapeProperties[2].split(";")
           current_shape_item = self.create_rectangle(
                float(coords[0]), float(coords[1]), float(coords[6]), float(coords[7]), outline="black"
            )
           
        elif(shapeProperties[0] == "triangle"):
            coords=shapeProperties[2].split(";")
            print(coords)
            current_shape_item=self.create_polygon(
                float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3]),float(coords[4]), float(coords[5]),outline="black",fill=""
            )
        elif shapeProperties[0] == "circle":
            radius=shapeProperties[3]
            Scoords = shapeProperties[2].split(";")
            Ccoords=self.get_circle_points(radius,Scoords)
            current_shape_item = self.create_oval(
                float(Ccoords[0]), float(Ccoords[1]), float(Ccoords[2]), float(Ccoords[3]), outline="black"
            )
        elif shapeProperties[0] == "polygon":
            coords=self.convert_poly_2float(shapeProperties[2].split(";"))
            current_shape_item=self.create_polygon(
                coords,outline="black",fill=""
            )
        print("from add shape",current_shape_item)
        return current_shape_item

    def draw_shape_bb(self,Sid):
        self.delete("bounding_box")
        if Sid:
            x1, y1, x2, y2 = self.bbox(Sid)
            self.create_rectangle(x1, y1, x2, y2, outline="red", tags="bounding_box")

    def remove_shape(self,Sid):
        if Sid:
            self.delete(Sid)
            self.delete("bounding_box")

    def get_center(self,x1, y1, x2, y2):
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y

    def get_radius(self,x1, x2):
        radius = abs(x2 - x1) / 2
        return radius
    
    def get_circle_points(self,Sradius,Scoords):
        radius=float(Sradius)
        Ccoords=[]
        Ccoords.append(float(Scoords[0]) - radius)
        Ccoords.append(float(Scoords[1]) - radius)
        Ccoords.append(float(Scoords[0]) + radius)
        Ccoords.append(float(Scoords[1]) + radius)

        return Ccoords
    def convert_poly_2float(self,Spoints:list):
        Fpoints=[]
        for cord in Spoints:
            Fpoints.append(float(cord))
        return Fpoints
    def convert_poly_2str(self,Fpoints:list):
        Spoints=""
        count=0
        for cord in Fpoints:
            Spoints+=str(cord)
            if count < len(Fpoints) -1:
                Spoints+=";"
            count+=1
        return Spoints

    def on_clear(self,event):
        self.delete("all")
    def CretaeSceenShotOfDraws(self):
        ''' Create a screenshot of the current canvas by redrswing all the shapes on a new PIL.Image and returning it
        '''
        # canvas_image = self.canvas.postscript(file ="dima.ps")
        
        all_shapes = self.find_all()
        
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        for shape_id in all_shapes:
            bbox = self.bbox(shape_id)
            min_x = min(min_x, bbox[0])
            min_y = min(min_y, bbox[1])
            max_x = max(max_x, bbox[2])
            max_y = max(max_y, bbox[3])
        # the output image size is 10% more that boundix box of all shapes
        image = Image.new("RGB", (int((max_x - min_x) * 1.1), int((max_y - min_y) * 1.1)), "white")
        draw = ImageDraw.Draw(image)

        min_x *= 0.9
        min_y *= 0.9
        
        for shape_id in all_shapes:
            shape_type = self.type(shape_id)
            cCoords=self.coords(shape_id)
            cCoords = [cCoords[i] - min_x if i % 2 == 0 else cCoords[i] - min_y for i in range(len(cCoords))]
            if shape_type == "rectangle":
                draw.rectangle(cCoords, outline="black")
            elif shape_type == "oval":
                draw.ellipse(cCoords, outline="black")
            elif shape_type == "line":
                draw.line(cCoords, outline="black")
        return image