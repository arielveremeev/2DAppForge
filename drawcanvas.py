import tkinter as tk
import math
from PIL import Image, ImageDraw

class DrawCanvas(tk.Canvas):
    def __init__(self,parent,callbacks):
        """
        This Python function initializes a canvas with various attributes and variables for shape
        manipulation.
        
        """
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
        self.drag_shape_id = None
        self.aggregate=1.0
        self.aggregate_angle=0



    def change_draw_type(self,text):
        """
        This function changes the operating mode:edit existing shapes or draw new shapes
        based on the input text and prints the current drawing type.
        
        """
        if text:
            self.selectedtype=text
            if(self.selectedtype == "edit"):
                self.toggle_edit()
            else:
                self.toggle_draw()
            print("current drawing type is " + str(self.selectedtype))

    def change_shape_type(self,text):
        """
        The function changes the drawn shape type and updates the drawing behavior accordingly.
        
        """
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
        """
        The function sets the selected edit type and binds specific mouse events based on the selected edit type.
        
        """
        if text:
            if self.selectededit:
                if self.selectededit == "scale_shape":
                    self.send_scale(tk.Event())
                elif self.selectededit == "rotate_shape":
                    self.send_rotate(tk.Event())
                self.delete("bounding_box")
                self.delete("debug_shapes")

            self.selectededit=text
            print("selected edit type is " + self.selectededit)

            self.unbind("<B1-Motion>")
            self.unbind("<ButtonRelease-1>")
            self.unbind("<MouseWheel>")
            self.unbind("<Double-Button-1>")
            
            if self.selectededit == "move_shape":
                self.bind("<B1-Motion>", self.move_shape)
                self.bind("<ButtonRelease-1>", self.stop_move)
            elif self.selectededit == "scale_shape":
                self.bind("<MouseWheel>", self.scale_shape)
                self.bind("<Double-Button-1>",self.send_scale)
            elif self.selectededit == "rotate_shape":
                self.bind("<MouseWheel>", self.rotate_shape)
                self.bind("<Double-Button-1>",self.send_rotate)
            

    def toggle_draw(self):
        """
        The `toggle_draw` function enables drawing functionality on a canvas by binding mouse events to
        corresponding methods.
        """
        self.canvas_status=True
        self.bind("<Button-1>", self.start_draw)
        self.bind("<B1-Motion>", self.draw_shape)
        self.bind("<ButtonRelease-1>", self.stop_draw)

        self.selectededit=None

    def toggle_edit(self):
        """
        The `toggle_edit` function in Python unbinds certain mouse events and binds a new event to handle
        shape clicking.
        """
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")
        self.bind("<Button-1>", self.on_shape_click)
       

    def on_shape_click(self, event):
        """
        This function handles actions when a shape is clicked, including deleting debug shapes, identifying
        the clicked shape, and initiating drag functionality.
        
        """

        print("on shape pressed")
        for shape_id in self.debug_shapes:
            self.delete(shape_id)
        self.debug_shapes = []
        
        bbox_id = self.find_withtag("bounding_box")
        bbox_id = bbox_id[0] if (len(bbox_id) > 0) else None
        debug_ids = self.find_withtag("debug_shapes")
            
        shapes_found = self.find_closest(event.x, event.y)
        if len(shapes_found) > 0:
            self.drag_shape_id = shapes_found[0]
            if self.drag_shape_id:
                print("shape pressed")
                if self.is_inside_shape(event.x, event.y,self.drag_shape_id):
                    self.draw_shape_bb(self.drag_shape_id)
                    self.start_drag_x,self.start_drag_y=event.x,event.y
                    self.move_x,self.move_y=0,0
                    self.start_coords=self.coords(self.drag_shape_id)
                    self.draw_scale_star3debug(self.drag_shape_id)
                else:
                    self.delete("bounding_box")
                
    def is_inside_shape(self, x, y, shape):
        # Get the bounding box of the shape
        bbox = self.bbox(shape)
        if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
            return True
        return False


    def move_shape(self,event):
        """
        The `move_shape` function updates the position of a shape based on the user's drag movement.
        
        """
        if self.drag_shape_id is not None:
            delta_x = event.x - self.start_drag_x
            delta_y = event.y - self.start_drag_y
            self.move(self.drag_shape_id,delta_x,delta_y)
            self.draw_shape_bb(self.drag_shape_id)
            self.draw_scale_star3debug(self.drag_shape_id)
            self.start_drag_x,self.start_drag_y=event.x,event.y
            self.move_x+=delta_x
            self.move_y+=delta_y

    def stop_move(self,event):
        """
        The function `stop_move` checks if a shape is being dragged and calls a callback function with the
        shape's ID and position before resetting the drag shape ID.
        
        """
        if self.drag_shape_id is not None:
            self.callbacks["on_shape_move"](self.drag_shape_id,self.move_x,self.move_y)
        self.drag_shape_id=None

    def scale_shape(self,event):
        """
        The function code scales a shape based on the event delta value which is detected by the mouse scroll wheel.
        each event(spin of the mouse wheel) scales the shape by 5%,mousewheel up increases by 5%,mousewheel down decreases by 5%
        the scaling is done by moving the vertex on a line thats intercepts the center of the shape and the coresponding vertex
        
        """
        if self.drag_shape_id is not None:
            size =(5*event.delta)/120
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
                print("aggregate",self.aggregate)
                    
                for i in range(0,len(self.coords(self.drag_shape_id)),2):
                    x=coords[i]
                    y=coords[i+1]
                    dir_x = x - avgX
                    dir_y = y - avgY
                
                    newX = avgX + dir_x * scale_factor
                    newY = avgY + dir_y * scale_factor

                    cCoords.append(newX)
                    cCoords.append(newY)
                self.coords(self.drag_shape_id,cCoords)
            self.draw_shape_bb(self.drag_shape_id)

    def send_scale(self,event):
        """
        The function is called when a shape is double clicked while the scale edit mode is selected.
        it updates the scale of a shape and triggers a callback function with the shape's ID and the scale value.
        
        """
        if self.drag_shape_id is not None:
            print(self.aggregate)
            self.callbacks["on_shape_scale"](self.drag_shape_id,self.aggregate)
        self.aggregate=1.0
        self.drag_shape_id=None

    def rotate_shape(self,event):
        """
        The `rotate_shape` function rotates a shape around its center based on the mouse wheel event.
        each mousewheel event spins the shape by 5 degrees using a trigonometrical function to recalculate the new vertex positions
        
        """
        if self.drag_shape_id is not None:
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

            print (f"from rotate on canvas [{avgX},{avgY}]:",cCoords)
            self.coords(self.drag_shape_id,cCoords)
            self.draw_shape_bb(self.drag_shape_id)
            self.draw_scale_star3debug(self.drag_shape_id)

    def send_rotate(self,event):
        """
        This function sends the aggregated angle to the specified callback function.
        
        """
        if self.drag_shape_id is not None:
            print(self.aggregate)        
            self.callbacks["on_shape_rotate"](self.drag_shape_id,self.aggregate_angle)
        self.aggregate_angle=0
        self.drag_shape_id=None

    def calc_center(self,coords):
        """
        This function calculates the center point of a set of coordinates by averaging the x and y values.
        
        """
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
        """
        The function `draw_scale_star3debug` in Python draws lines from a given point to the canvas
        boundaries for debugging purposes.
        
        """
        if Sid:
            coords = self.coords(Sid)
            center_x,center_y = self.calc_center(coords)
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            for shape_id in self.debug_shapes:
                self.delete(shape_id)
            self.debug_shapes = []
        

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
                line_id = self.create_line(x1, y1, x2, y2, fill="green",tags="debug_shapes")
                self.debug_shapes.append(line_id)



    def edit_shape(self,Sid,details:list):
        """
            this function recives a shape id and a list of details about a shape in a specific format
            after which it parses the list and redraws the shape whos id was provided in the arguments
        """
        if Sid and details:
            print("drawcanvas::edit_shape:: coords from canvas",self.coords(int(Sid)))
            print("drawcanvas::edit_shape:: coords from server",details)
            shapeProperties = details.split(' ')
            if(shapeProperties[0] == "triangle" or shapeProperties[0] == "polygon" or shapeProperties[0] == "square"):
                Scoords=shapeProperties[2].split(";")
                Fcoords=self.convert_poly_2float(Scoords)
                self.coords(int(Sid),Fcoords)
            elif shapeProperties[0] == "circle":
                radius=shapeProperties[3]
                Scoords = shapeProperties[2].split(";")
                Ccoords=self.get_circle_points(radius,Scoords)
                self.coords(int(Sid),float(Ccoords[0]), float(Ccoords[1]), float(Ccoords[2]), float(Ccoords[3]))
                
    def start_draw(self, event):
        """
            this function is triggered on the click of the left mouse button and creates a shape object.
            the shape object is created based on the selected drawing type. 
        """
        self.start_x = event.x
        self.start_y = event.y
        if self.selectedshape == "rectangle":
            self.current_shape_item = self.create_polygon(
                self.start_x, self.start_y, self.start_x, self.start_y,self.start_x, self.start_y,self.start_x, self.start_y, outline="black",fill=""
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
        """
            this function is triggered when u drag the mouse with the left mouse button held and it redraws the shape object.
            it redraws the shape object based on the selected draw type and the position of the mouse cursor on the canvas
        """
        if self.current_shape_item is not None:
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
                self.coords(self.current_shape_item, self.start_x, self.start_y, x, self.start_y, x, y, self.start_x, y)
    
    def stop_draw(self, event):
        """
            this function is triggered on the release of the left mouse button and it saves all the coordinates of the current shape object (and the radius if its a circle)
            after they are saved a message a string is construced which consists of the name of the shape the amount of vertexes it has and its coordinates(and a radius if its a circle)
            then a callback is called with the construced string as a parameter
        """
        if self.current_shape_item is not None:
            Ccoords=self.coords(self.current_shape_item)
            shape=""
            print(Ccoords)
            if(self.selectedshape == "rectangle"):
                coords=self.convert_poly_2str(Ccoords)
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
        """
            this function is the draw function for the polygon drawing mode and it works by creating and appending the coordinates where the mouse was clicked into a list.
            this list is forwarded to the draw_polygon canvas function which recives a list of points no matter its length as long as it has an even amount of coordinates.
            the function is triggered upon the left mouse click and each click adds a points to the list.
        """
        self.PolyPoints.append((event.x, event.y))
        self.delete(self.polygon)
        self.polygon=self.create_polygon(self.PolyPoints,outline="black", fill="")
        print(self.coords(self.polygon))

    def stop_polygon(self,event):
        """
            this function is triggered upon a double left mouse click with the polygon drawing mode exclusivly and on addition to triggering the addition of another point to the list before this functions trigger
            it creates a string which consists of the shape name(polygon) the amount of vertexes it has and all of their coordinates
            then a callback is called with the construced string as a parameter
        """
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
        """
            this function recives a string as shape details and parses them, after that it creates a canvas shape object according to the details in the string recived in the parameter
            then returns the shape object
        """
        shapeProperties = details.split(' ')
        if shapeProperties[0] == "square":
           coords = shapeProperties[2].split(";")
           current_shape_item = self.create_polygon(
                float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3]),float(coords[4]), float(coords[5]),float(coords[6]),float(coords[7]),outline="black",fill=""
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
        """
            this function deletes a bounding box from the canvas if it exists and then creates a bounding box around the shape whose id is provided in the parameters
        """
        self.delete("bounding_box")
        if Sid:
            x1, y1, x2, y2 = self.bbox(Sid)
            self.create_rectangle(x1, y1, x2, y2, outline="red", tags="bounding_box")

    def remove_shape(self,Sid):
        """
            this function deletes a shape from the canvas while also deleting a bounding box if it exists
        """
        if Sid:
            self.delete(Sid)
            self.delete("bounding_box")

    def get_center(self,x1, y1, x2, y2):
        """
            this function is used to calculate the center of a circle using the 2 edges of the circle
            returns the x and y coordinates of the center
        """
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        return center_x, center_y

    def get_radius(self,x1, x2):
        """
            this function calculates the radius of a circle based on the x values of the 2 edges of the circle
            return the radius of the circle
        """
        radius = abs(x2 - x1) / 2
        return radius
    
    def get_circle_points(self,Sradius,Scoords):
        """
            this function recalculates the edges of a circle based on the circles radius and its previous edges
            returns its new edges coordinates
        """
        radius=float(Sradius)
        Ccoords=[]
        Ccoords.append(float(Scoords[0]) - radius)
        Ccoords.append(float(Scoords[1]) - radius)
        Ccoords.append(float(Scoords[0]) + radius)
        Ccoords.append(float(Scoords[1]) + radius)

        return Ccoords
    def convert_poly_2float(self,Spoints:list):
        """
            this function converts a list of points from strings into a point list of floats
            return the float list
        """
        Fpoints=[]
        for cord in Spoints:
            Fpoints.append(float(cord))
        return Fpoints
    def convert_poly_2str(self,Fpoints:list):
        """
            this function converts a list of points from floats into a point list of strings
            return the string list
        """
        Spoints=""
        count=0
        for cord in Fpoints:
            Spoints+=str(cord)
            if count < len(Fpoints) -1:
                Spoints+=";"
            count+=1
        return Spoints

    def on_clear(self,event):
        """
            this functions clears the canvas
        """
        self.delete("all")

    def has_tags(self, shape):
        # Get the tags of the shape
        tags = self.gettags(shape)
        return bool(tags)

    def CretaeSceenShotOfDraws(self):
        ''' Create a screenshot of the current canvas by redrawing all the shapes on a new PIL.Image and returning it
        '''
        # canvas_image = self.canvas.postscript(file ="dima.ps")
        
        all_shapes = self.find_all()
        
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")

        #loop for calculating the bounding box of all the shapes on the canvas
        for shape_id in all_shapes:
            if self.has_tags(shape_id):
                print("Edit/debug shape")
            else:
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
            if self.has_tags(shape_id):
                print("Edit/debug shape")
            else:
                shape_type = self.type(shape_id)
                cCoords=self.coords(shape_id)
                cCoords = [cCoords[i] - min_x if i % 2 == 0 else cCoords[i] - min_y for i in range(len(cCoords))]
                if shape_type == "rectangle":
                    draw.rectangle(cCoords, outline="black")
                elif shape_type == "oval":
                    draw.ellipse(cCoords, outline="black")
                elif shape_type == "line":
                    draw.line(cCoords, outline="black")
                elif shape_type == "polygon":
                    draw.polygon(cCoords, outline="black")
        return image