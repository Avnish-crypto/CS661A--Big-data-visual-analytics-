#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#import modules...
from vtk import *

# load the data
reader = vtkXMLImageDataReader()
reader.SetFileName('Data\Isabel_2D.vti')
reader.Update()
data = reader.GetOutput()

val = input("Please enter the isovalue : ")
c = float(val)

### create points
points = vtkPoints()

### Create a cell array to store the lines
cells = vtkCellArray()

number_of_cells = data.GetNumberOfCells()
data_arr = data.GetPointData().GetArray('Pressure')

def Getpointid(cell,i):
    # return pid of a point
    return cell.GetPointId(i)

def Getval(i):
    # return val of point
    return data_arr.GetTuple1(i)

def Getcoor(i):
    # returns coordinate of point
    return data.GetPoint(i)

def marching_Square_alogrithm():
    
    for i in range(number_of_cells):

        cell = data.GetCell(i)
        
        pid1 = Getpointid(cell,0)
        pid2 = Getpointid(cell,1)       #pid's of vertices
        pid3 = Getpointid(cell,3)   
        pid4 = Getpointid(cell,2)    

        CoorDinate1 = Getcoor(pid1)
        coordinate2 = Getcoor(pid2)
        coordinate3 = Getcoor(pid3)   # getting coordinates of points
        coordinate4 = Getcoor(pid4)

        x1,y1,z1 = CoorDinate1[0],CoorDinate1[1],CoorDinate1[2]
        x2,y2,z2 = coordinate2[0],coordinate2[1],coordinate2[2]  #(x,y,z)
        x3,y3,z3 = coordinate3[0],coordinate3[1],coordinate3[2]
        x4,y4,z4 = coordinate4[0],coordinate4[1],coordinate4[2]


        val1 = Getval(pid1)
        val2 = Getval(pid2)  # getting val of point
        val3 = Getval(pid3)
        val4 = Getval(pid4)
        
        if (val1 <= c and val2 >= c) or (val1 >= c and val2 <= c):
            l1 = (val1 - c) / (val1 - val2)
            z = l1 * (z2-z1) + z1
            y = l1 * (y2-y1) + y1  #calculating new points Coordinates
            x = l1 * (x2-x1) + x1
            temp = [x,y,z]
            points.InsertNextPoint(temp)
    
        if (val2 <= c and val3 >= c) or (val2 >= c and val3 <= c):
            l2 = (val2 - c) / (val2 - val3)
            z = l2 * (z3-z2) + z2
            y = l2 * (y3-y2) + y2
            x = l2 * (x3-x2) + x2
            temp = [x,y,z]
            points.InsertNextPoint(temp)
        
        if (val3 <= c and val4 >= c) or (val3 >= c and val4 <= c):
            l3 = (val3 - c) / (val3 - val4)
            z = l3 * (z4-z3) + z3
            y = l3 * (y4-y3) + y3
            x = l3 * (x4-x3) + x3
            temp = [x,y,z]
            points.InsertNextPoint(temp)
        
        if (val4 <= c and val1 >= c) or (val4 >= c and val1 <= c):
            l4 = (val4 - c) / (val4 - val1)
            z = l4 * (z4-z1) + z1
            y = l4 * (y4-y1) + y1
            x = l4 * (x4-x1) + x1
            temp = [x,y,z]
            points.InsertNextPoint([x,y,z])

marching_Square_alogrithm()

poly_line = vtkPolyLine()
num_of_points = points.GetNumberOfPoints()

for i in range(0,num_of_points,2):
    poly_line.GetPointIds().SetNumberOfIds(2)
    poly_line.GetPointIds().SetId(0,i)
    poly_line.GetPointIds().SetId(1,i+1)
    cells.InsertNextCell(poly_line)

poly_data = vtkPolyData()
poly_data.SetPoints(points)
poly_data.SetLines(cells)
writer = vtkXMLPolyDataWriter()
writer.SetFileName("Isocontour.vtp")
writer.SetInputData(poly_data)
writer.Write()

def show():
    # Load the polydata
    reader = vtkXMLPolyDataReader()
    reader.SetFileName("Isocontour.vtp")
    reader.Update()

    # Create a mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(reader.GetOutput())

    # Create an actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    colors = vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d('blue'))

    # Create a renderer
    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('black'))

    # Create a render window
    render_window = vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Start the interactor
    interactor.Initialize()

    interactor.Start()

show()

