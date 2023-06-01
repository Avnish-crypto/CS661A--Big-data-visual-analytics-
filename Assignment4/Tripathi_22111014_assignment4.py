#import the necessary libraries
import vtk
import random
import numpy as np
import time
from scipy.interpolate import griddata
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk



reader = vtk.vtkXMLImageDataReader()
reader.SetFileName("Isabel_3D.vti") # Loading the 3D scalar field volume dataset.
reader.Update()

volume = reader.GetOutput() # Volume data
dimensions = volume.GetDimensions() # Dimensions
total_number_of_points = dimensions[0] * dimensions[1] * dimensions[2]




def WRITER(poly_data):
    ''' Function to write .vtp file
    '''
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(poly_data)
    writer.SetFileName("sample_points.vtp")
    writer.Write()



def SRS(sampling_percentage):
    
    sampled_points_count = int(total_number_of_points * sampling_percentage/100) # Calculating the number of points to sample based on the sampling percentage
    Samples = set([(i * (dimensions[0] - 1),j * (dimensions[1] - 1),k * (dimensions[2] - 1)) for i in range(2) for j in range(2) for k in range(2)]) #store the sampled points
    indexes = np.random.choice(total_number_of_points, sampled_points_count, replace=False) #Random selection of remaining points


    for counter,index in enumerate(indexes):
        z = index % dimensions[2]
        y = ((index - z) // dimensions[2]) % dimensions[1]
        x = (((index - z) // dimensions[2]) - y) // dimensions[1]
        point = (x, y, z)
        Samples.add(point)

    points = vtk.vtkPoints()
    data = vtk.vtkDoubleArray()
    data.SetName("Data")

    for counter,point in enumerate(Samples):
        i, j, k = point
        value = volume.GetScalarComponentAsDouble(i, j, k, 0) 
        points.InsertNextPoint(i, j, k) #Adding Sampled points to vtkpoints
        data.InsertNextTuple1(value) #Adding Sampled points to vtkDoubleArray objects

    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)
    poly_data.GetPointData().AddArray(data)
    
    WRITER(poly_data)

sampling_percentage = float(input("Enter the desired sampling percentage: "))
SRS(sampling_percentage)



def get_nop(poly_data):
    '''
    function for returning the number of sample points in the polydata.
    '''
    return poly_data.GetNumberOfPoints()



def WRITER1(nearest,file_name):
    '''
    function to save the .vti file
    '''
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(nearest)
    writer.Write()



reader1 = vtk.vtkXMLPolyDataReader()
reader1.SetFileName('sample_points.vtp')
reader1.Update()

poly_data = reader1.GetOutput()
nop = get_nop(poly_data)

POINTSARRAY = np.zeros((nop, 3))
DATAARRAY = np.zeros(nop)

for i in range(nop):
    point = poly_data.GetPoint(i)
    POINTSARRAY[i] = point
    DATAARRAY[i] = poly_data.GetPointData().GetArray("Data").GetValue(i) # storing the points in the polydata in the numpy array point_arr and array DATAARRAY.

dims = (250, 250, 50)
x = np.linspace(0, 249, 250)
y = np.linspace(0, 249, 250)   ## Creating a grid of points as the same dimensions as of the real Data
z = np.linspace(0, 49, 50)    
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
grid = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))


option=(input("Enter the choice of reconstruction technique: {nearest/linear} ")).lower()
print("Choosen Technique for Reconstruction from sampled points: ",option )


if option == 'nearest': # Performing nearest neighbor interpolation
    nearest = vtk.vtkImageData()
    nearest.SetDimensions(dims)
    nearest.SetOrigin(0, 0, 0)
    nearest.SetSpacing(1, 1, 1)
    nearest.AllocateScalars(vtk.VTK_FLOAT, 1)

    t1 = time.time()
    grid_data = griddata(POINTSARRAY, DATAARRAY, grid, method='nearest')
    t2 = time.time()
    times = t2-t1
    print('Sampling Percentage ',sampling_percentage,' %')
    print("Time taken for reconstructing using nearest interpolation technique:", times," secs.")


    grid_data = np.reshape(grid_data, dims)
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                idx = nearest.ComputePointId([i, j, k])
                nearest.GetPointData().GetScalars().SetTuple1(idx, grid_data[i, j, k])
    file_name = "reconstructed_nearest.vti"

    WRITER1(nearest,file_name)


elif option == 'linear': # performing linear interpolation based reconstruction
    linear = vtk.vtkImageData()
    linear.SetDimensions(dims)
    linear.SetOrigin(0, 0, 0)
    linear.SetSpacing(1, 1, 1)
    linear.AllocateScalars(vtk.VTK_FLOAT, 1)

    t1 = time.time()
    grid_data = griddata(POINTSARRAY, DATAARRAY, grid, method='linear') # Replacing the nan values with nearest neighbor values
    mask = np.isnan(grid_data)
    grid_data[mask] = griddata(POINTSARRAY, DATAARRAY, grid[mask], method='nearest')
    t2 = time.time()
    times = t2 - t1
    print('Sampling Percentage ',sampling_percentage,' %')
    print("Time taken for reconstructing using linear interpolation technique:", times," secs.")
    
    grid_data = np.reshape(grid_data, dims)
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                idx = linear.ComputePointId([i, j, k])
                linear.GetPointData().GetScalars().SetTuple1(idx, grid_data[i, j, k])
    
    file_name = "reconstructed_linear.vti"
    WRITER1(linear,file_name)
    
else:
    print("PLEASE ENTER PROPER RECONSTRUCTION CHOICE!!")




def get_data(point_data):
    return vtk.util.numpy_support.vtk_to_numpy(point_data.GetArray(0))


def Numpy(file_name):
    '''function for reconstructed file and original file to numpy array'''
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(file_name)
    reader.Update()
    data = reader.GetOutput()
    point_data = data.GetPointData()
    numpy_array = get_data(point_data)
    return numpy_array

reconstructed_array = Numpy(file_name)
real_array = Numpy('Isabel_3D.vti')


def print_result(snr_value):
    '''
    # function for displaying the corresponding SNR
    '''
    if option == 'linear':
        print('Signal-to-Noise ratio for reconstructed data while using linear technique is : ',snr_value)
    elif option == 'nearest':
        print('Signal-to-Noise ratio for reconstructed data while using nearest technique is : ',snr_value)



def calculate_SNR(arrgt, recons):
    ''''
    calculations for SNR
    '''
    diff = arrgt - recons 
    sqd_max_diff = (np.max(arrgt) - np.min(arrgt)) ** 2 
    snr = 10 * np.log10(sqd_max_diff / np.mean(diff ** 2))
    return snr

snr_value = calculate_SNR(real_array,reconstructed_array)


print_result(snr_value)




