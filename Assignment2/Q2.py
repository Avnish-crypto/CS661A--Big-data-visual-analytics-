#!/usr/bin/env python
# coding: utf-8

# In[1]:


def render_3d():
    import vtk

    # Load the 3D data
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("Data/Isabel_3D.vti")
    reader.Update()

    # Creating the color transfer function as asked in assignment
    COLORTF = vtk.vtkColorTransferFunction()
    COLORTF.AddRGBPoint(-4931.54, 0, 1, 1)
    COLORTF.AddRGBPoint(-2508.95, 0, 0, 1)
    COLORTF.AddRGBPoint(-1873.9, 0, 0, 0.5)
    COLORTF.AddRGBPoint(-1027.16, 1, 0, 0)
    COLORTF.AddRGBPoint(-298.031, 1, 0.4, 0)
    COLORTF.AddRGBPoint(2594.97, 1, 1, 0)

    # Creating  the opacity transfer function as asked in assignment
    OPACITYTF = vtk.vtkPiecewiseFunction()
    OPACITYTF.AddPoint(-4931.54, 1.0)
    OPACITYTF.AddPoint(101.815, 0.002)
    OPACITYTF.AddPoint(2594.97, 0.0)

    # Using the vtkSmartVolumeMapper for volume rendering
    volumeMapper = vtk.vtkSmartVolumeMapper()
    volumeMapper.SetInputData(reader.GetOutput())

    # Creating the volume property
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(COLORTF)
    volumeProperty.SetScalarOpacity(OPACITYTF)

    # Checking if the user wants to use Phong shading or not
    Phong = input("Do you want to use Phong shading or not? (yes/no) ")

    if Phong == "no":
        volumeProperty.ShadeOff()
    else:
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.5)
        volumeProperty.SetDiffuse(0.5)
        volumeProperty.SetSpecular(0.5)

    # Create the volume and set the mapper and property
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    # Use vtkOutlineFilter to add an outline to the volume
    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(reader.GetOutput())
    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outline.GetOutputPort())
    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)

    # Create a render window and add the volume and outline
    ren = vtk.vtkRenderer()
    ren.AddVolume(volume)
    ren.AddActor(outlineActor)

    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(1000, 1000)
    renWin.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Start the interaction
    iren.Initialize()
    renWin.Render()
    iren.Start()
    
render_3d()  #function

