# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 11:37:39 2015

@author: abarry
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 01:11:35 2015

@author: alex
"""
from kivy.app import App
from Magnet import Magnet
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.graphics import Color, Line

Builder.load_file('draggableimages.kv')

#A Cell in the Dragging Grid
class DraggingGridCell(BoxLayout):
    grid=ObjectProperty(None)
    row=NumericProperty(None)
    col=NumericProperty(None)
    
    def next_cell(self):
        if self.row == self.grid.size - 1:
            return self.grid.getCell(self.row - 1, self.col)
        if self.col == self.grid.size - 1:
            return self.grid.getCell(self.row + 1, self.col)
        return self.grid.getCell(self.row + 1, self.col)
        
    def isEmpty(self):
        if len(self.children == 0):
            return True
        else:
            return False

#The Dragging Grid
class DraggingGrid(GridLayout):
    cells=ListProperty([])
    size=NumericProperty(3)
    
    def __init__(self, **kwargs):

        super(DraggingGrid, self).__init__(**kwargs)
        self.cols=self.size
        for i in range(0, self.size):
            for j in range(0, self.size):
                cell=DraggingGridCell(grid=self, row=i, col=j)
                self.cells.append(cell)
                self.add_widget(cell)
   
    def getCell(self, x, y):
        for cell in self.cells:
            if cell.row == x and cell.col == y:
                return cell
        return 0
            
#This class defines the line drawn between two nodes
class MenuConnector(Widget):
    
    #Front and Back vertices, the line is drawn in between
    #2 Entry Lists
    front = ListProperty([0, 0])
    back = ListProperty([1, 1])
    
    #The color of the lines
    #3 Entry Lists
    line_color = ListProperty([1, 1, 1])
    
    ellipse_diameter = NumericProperty(20)
    
    def __init__(self, **kwargs):
        super(MenuConnector, self).__init__(**kwargs)
        self.bind(front=self.set_front, back=self.set_back, line_color=self.set_color)
    
    def set_front(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(self.line_color[0], self.line_color[1], self.line_color[2])
            Line(points=[self.front[0], self.front[1], self.back[0], self.back[1]])
    
    def set_back(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(self.line_color[0], self.line_color[1], self.line_color[2])
            Line(points=[self.front[0], self.front[1], self.back[0], self.back[1]])
    
    def set_color(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(self.line_color[0], self.line_color[1], self.line_color[2])
            Line(points=[self.front[0], self.front[1], self.back[0], self.back[1]])

#This class defines a draggable image
class DraggableImage(Magnet):
    img = ObjectProperty(None, allownone=True)
    app = ObjectProperty(None)
    grid = ObjectProperty(None)
    cell = ObjectProperty(None)
    start_cell = NumericProperty(0)

    def on_img(self, *args):
        self.clear_widgets()
        if self.img:
            Clock.schedule_once(lambda *x: self.add_widget(self.img), 0)

    def on_touch_down(self, touch, *args):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                pass
            else:
                touch.grab(self)
                self.remove_widget(self.img)
                self.app.root.add_widget(self.img)
                self.center = touch.pos
                self.img.center = touch.pos
            return True

        return super(DraggableImage, self).on_touch_down(touch, *args)

    def on_touch_move(self, touch, *args):

        if touch.grab_current == self:
            self.img.center = touch.pos
        return super(DraggableImage, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch, *args):
        if touch.grab_current == self:
            if self.grid.collide_point(*touch.pos):
                for cel in self.grid.cells:
                    if cel.collide_point(*touch.pos):
                        self.cell.remove_widget(self)
                        self.app.root.remove_widget(self.img)
                        self.cell=cel
                        self.cell.add_widget(self)
                        self.add_widget(self.img)
                        touch.ungrab(self)
                        return True
                self.app.root.remove_widget(self.img)
                self.cell=1
                self.add_widget(self.img)
                touch.ungrab(self)
                return True
            else:
                self.cell.remove_widget(self)
                self.app.root.remove_widget(self.img)
                self.cell.add_widget(self)
                self.add_widget(self.img)
                touch.ungrab(self)
        return super(DraggableImage, self).on_touch_up(touch, *args)
        
class SimpleConnectorButton(Button):
    #The Grid being worked on
    grid=ObjectProperty(None)
    
    #The Cell the button currently resides in
    cell=ObjectProperty(None)
    
    #The connector node the button belongs to
    node=ObjectProperty(None)
    
         
class ConnectorButton(Image):
    #The Grid being worked on
    grid=ObjectProperty(None)
    
    #The Cell the button currently resides in
    cell=ObjectProperty(None)
    
    #The connector node the button belongs to
    node=ObjectProperty(None)
    
    #To expose on_press events
    press=ListProperty([0,0])
    
    double_press=ListProperty([0,0])
    
    triple_press=ListProperty([0,0])
    
    def __init__(self, **kwargs):
        super(ConnectorButton, self).__init__(**kwargs)
        
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.double_press=touch.pos
        elif touch.is_triple_tap:
            self.triple_press=touch.pos
        else:
            self.press=touch.pos

#The overall flowchart node
class ConnectorNode(BoxLayout):
    
    app = ObjectProperty(None)
    
    #The Grid being added to
    grid = ObjectProperty(None)
    
    cell = ObjectProperty(None)
    
    #Property exposed to set the list of connected nodes
    connected_nodes = ListProperty([])    

    #The color of the connection lines in rgb
    connector_color = ListProperty([1, 1, 1])
    
    #Internal Properties
    #The Center Widget
    center_node = ObjectProperty(None)
    
    #Internal property to track the connections
    connect = ListProperty([])
    
    def __init__(self, **kwargs):
        super(ConnectorNode, self).__init__(**kwargs)
        #create the center button & bind the properties
        c_node = SimpleConnectorButton(grid=self.grid, cell=self.cell, node=self)
        c_node.bind(pos=self.set_front, on_press=self.press_front)
        self.center_node = c_node
        self.add_widget(self.center_node)
        
    def set_front(self, *args):
        for con in self.connect:
            con.front = self.center_node.center
        
    def set_back(self, *args):
        i=0
        for con in self.connect:
            con.back = self.connected_nodes[i].center
            i+=1
        
    def press_front(self, *args):
        #Add the option nodes and connectors to the widget if it's closed
        #Otherwise, close the widget
        if len(self.connect) == 0:
            for option in self.connected_nodes:
                connector = MenuConnector(line_color=self.connector_color)
                self.connect.append(connector)
                
        #Add a new connector and a new draggable image lists
        connector = MenuConnector(line_color=self.connector_color)
        self.connect.append(connector)
        
        image = Image(source='drag_node_small.png')
        drag = DraggableImage(img=image, app=self.app, grid=self.grid, cell=self.cell.next_cell())
        self.connected_nodes.append(drag)
        
        self.clear_widgets()
        cel = self.cell.next_cell()
        cel.clear_widgets()
        for con in self.connect:
            cel = self.cell.next_cell()
            cel.add_widget(con)
        for option in self.connected_nodes:
            option.bind(pos=self.set_back)
            cel = self.cell.next_cell()
            cel.add_widget(option)
        self.add_widget(self.center_node)
            
        for con in self.connect:
            con.front = self.center_node.center
        
class FlowchartExampleWidget(GridLayout):
    drag_grid=ObjectProperty(None)
        
class FlowchartExampleApp(App):
    def build(self):
        root = FlowchartExampleWidget()
        drag = ConnectorNode(app=self, grid=root.drag_grid, cell=root.drag_grid.cells[0])
        root.drag_grid.cells[0].add_widget(drag)
        return root
  
if __name__ == '__main__':
    FlowchartExampleApp().run()