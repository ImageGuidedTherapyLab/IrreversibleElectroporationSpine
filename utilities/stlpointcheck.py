import vtk

# open stl 
stlReader = vtk.vtkSTLReader()
stlReader.SetFileName( 'registerstl.stl' )
stlReader.Update()


# check if point within bound
vtkbound = vtk.vtkSelectEnclosedPoints()
vtkbound.Initialize(stlReader.GetOutput()) 

for point in [(0.,0.,0.),(.4,.6,.7)]:
   print vtkbound.IsInsideSurface(point[0],point[1],point[2])

