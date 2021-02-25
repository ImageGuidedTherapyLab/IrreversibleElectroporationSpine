import os
import ConfigParser
import vtk
import numpy
import subprocess
import math

# write vtk points file
def WriteVTKPoints(vtkpoints,OutputFileName):
   # loop over points an store in vtk data structure
   #vtkpoints = vtk.vtkPoints()
   vertices= vtk.vtkCellArray()
   for idpoint in range(vtkpoints.GetNumberOfPoints()):
       #vertices.InsertNextCell( 1 ); vertices.InsertCellPoint( vtkpoints.InsertNextPoint(point) )
       vertices.InsertNextCell( 1 ); vertices.InsertCellPoint( idpoint )

   # set polydata
   polydata = vtk.vtkPolyData()
   polydata.SetPoints(vtkpoints)
   polydata.SetVerts( vertices )

   # write to file
   polydatawriter = vtk.vtkDataSetWriter()
   polydatawriter.SetFileName(OutputFileName)
   polydatawriter.SetInputData(polydata)
   polydatawriter.Update()

# Applicator Transform
def GetApplicatorTransform(pointtip,pointentry,SourceLandmarkFileName, TargetLandmarkFileName ):
  ApplicatorTipLength = .011 #m
  # template applicator center at coordinate       (0,                         0., 0. ) m
  # template applicator distal ends at coordinates (0,  0.,+/- ApplicatorTipLength/2. ) m
  originalOrientation = vtk.vtkPoints()
  originalOrientation.SetNumberOfPoints(2)
  originalOrientation.SetPoint(0,0.,0.,         0.            )
  originalOrientation.SetPoint(1,0.,0., ApplicatorTipLength/2.)
  slicerLength   = numpy.linalg.norm( numpy.array(pointentry) - numpy.array(pointtip) )
  unitdirection  = 1./slicerLength * (numpy.array(pointentry) - numpy.array(pointtip) ) 
  pointscaled = pointtip + ApplicatorTipLength/2. * unitdirection
  print "points", pointentry, pointtip, pointscaled, slicerLength, numpy.linalg.norm( unitdirection  ), numpy.linalg.norm( pointscaled - pointtip ) 
  slicerOrientation   = vtk.vtkPoints()
  slicerOrientation.SetNumberOfPoints(2)
  slicerOrientation.SetPoint(0,pointtip[   0],pointtip[   1],pointtip[   2] )
  slicerOrientation.SetPoint(1,pointscaled[0],pointscaled[1],pointscaled[2] )

  # write landmarks to file
  WriteVTKPoints(originalOrientation,SourceLandmarkFileName)
  WriteVTKPoints(slicerOrientation  ,TargetLandmarkFileName)

  ApplicatorLineTransform = vtk.vtkLandmarkTransform()
  ApplicatorLineTransform.SetModeToRigidBody()
  ApplicatorLineTransform.SetSourceLandmarks(originalOrientation)
  ApplicatorLineTransform.SetTargetLandmarks(slicerOrientation  )
  ApplicatorLineTransform.Update()
  print ApplicatorLineTransform.GetMatrix()

  # create model of applicator 
  ApplicatorLength   = .10 #m
  vtkCylinder = vtk.vtkCylinderSource()
  vtkCylinder.SetHeight( ApplicatorLength ); 
  vtkCylinder.SetRadius( .00075 );
  vtkCylinder.SetCenter(0.0, 0.0, 0.0 );
  vtkCylinder.SetResolution(16);
  vtkCylinder.SetCapping(1);

  # model orientation
  modelOrientation = vtk.vtkPoints()
  modelOrientation.SetNumberOfPoints(2)
  modelOrientation.SetPoint(0, 0.,         0.         ,0. )
  modelOrientation.SetPoint(1, 0.,-ApplicatorLength/2.,0. )

  ModelLineTransform = vtk.vtkLandmarkTransform()
  ModelLineTransform.SetModeToRigidBody()
  ModelLineTransform.SetSourceLandmarks(modelOrientation   )
  ModelLineTransform.SetTargetLandmarks(slicerOrientation  )
  ModelLineTransform.Update()
  print ModelLineTransform.GetMatrix()

  # transform
  slicertransformFilter = vtk.vtkTransformFilter()
  slicertransformFilter.SetInputData(vtkCylinder.GetOutput() ) 
  slicertransformFilter.SetTransform( ModelLineTransform ) 
  slicertransformFilter.Update()
  apppolyData=slicertransformFilter.GetOutput();

  # write model to file
  vtkModelWriter = vtk.vtkDataSetWriter()
  vtkModelWriter.SetInputData(apppolyData)
  vtkModelWriter.SetFileName("applicator.vtk")
  vtkModelWriter.SetFileTypeToBinary()
  vtkModelWriter.Write()
  # return transform
  return ApplicatorLineTransform

# setup command line parser to control execution
from optparse import OptionParser
parser = OptionParser()
parser.add_option( "--ini", 
                  action="store", dest="config_ini", default=None,
                  help="ini FILE containing setup info", metavar="FILE")
parser.add_option( "--resample", 
                  action="store", dest="resample", default=None,
                  help="image data FILE where we will resample to", metavar="FILE")
parser.add_option( "--outputid", 
                  action="store", dest="outputid", default=None,
                  help="string ID of fem and output file", metavar="STR")
(options, args) = parser.parse_args()

if (options.config_ini != None):

  # read config file
  config = ConfigParser.SafeConfigParser({})
  config.read(options.config_ini)
  
  # get tissue type replacement info info
  tissuereplace       = config.get('tissue','tissue_replace') 
  # get header info
  niftiimage          = config.get('setup','imagefile') 
  vtkimage            = niftiimage.replace('.nii.gz','.vtk')
  vtknerverootimage   = niftiimage.replace('.nii.gz','.nerve.vtk')
  getHeaderCmd = 'c3d %s -info ' % niftiimage  
  print getHeaderCmd 
  headerProcess = subprocess.Popen(getHeaderCmd ,shell=True,stdout=subprocess.PIPE )
  while ( headerProcess.poll() == None ):
     pass
  rawheaderinfo = headerProcess.stdout.readline().strip('\n')
  # rawheaderinfo = 'Image #1: dim = [512, 512, 184];  bb = {[124 124 -85], [372 372 835]};  vox = [0.484375, 0.484375, 5];  range = [0, 14];  orient = LPI'
  conversionfactor = .001
  spacing   = [conversionfactor *dxvox  for  dxvox in eval(rawheaderinfo.split(";")[2].split("=")[1]) ]
  dimension = [              int(dxvox) for  dxvox in eval(rawheaderinfo.split(";")[0].split("=")[1]) ]

  # convert to meters
  convertMeterCmd = 'c3d %s -replace %s -origin 0.0x0.0x0.0mm -spacing %fx%fx%fmm -o %s' % (niftiimage,tissuereplace , spacing[0],spacing[1],spacing[2], vtkimage   )
  print convertMeterCmd 
  os.system(convertMeterCmd )

  # extract nerve root data, convert to meters 
  convertNerveCmd = 'c3d %s -origin 0.0x0.0x0.0mm -spacing %fx%fx%fmm -o %s' % (niftiimage , spacing[0],spacing[1],spacing[2],vtknerverootimage  )
  print convertNerveCmd 
  os.system(convertNerveCmd )
 
  # initialize queue
  jobList = []
  jobListPost = []

  # open makefile
  jobid = options.config_ini.split(".")[0]
  os.system("mkdir -p %s " % jobid )
  jobmakefilename = 'exec.%s.makefile' % jobid 
  fileHandle = file(jobmakefilename  ,'w')
  

  # expected labels for each voltage
  voltageList = eval(config.get('setup','voltageList' ))
  for voltage,applicatorid in voltageList :
    #for controlrun,worstcasetype in [ (True,"electric_conductivity"),(False,"electric_conductivity_lb"),(False,"electric_conductivity_ub")]:
    for controlrun,worstcasetype in [ (True,"electric_conductivity")]:
      # id the run
      outputid = "%s.%04d.%02d.%02d" % (worstcasetype,voltage,applicatorid['tip'],applicatorid['entry'])
      print "\n\n",outputid 
      # get applicator info 
      applicatorTipInfoCMD   = 'c3d %s -threshold %d %d 1 0 -centroid ' % (vtknerverootimage  , applicatorid['tip'  ],applicatorid['tip'  ])
      print applicatorTipInfoCMD 
      applicatorTipInfoProcess = subprocess.Popen(applicatorTipInfoCMD ,shell=True,stdout=subprocess.PIPE )
      while ( applicatorTipInfoProcess.poll() == None ):
         pass
      applicatorTipInfo = applicatorTipInfoProcess.stdout.readlines()
      print applicatorTipInfo

      applicatorEntryInfoCMD = 'c3d %s -threshold %d %d 1 0 -centroid ' % (vtknerverootimage  , applicatorid['entry'],applicatorid['entry'])
      print applicatorEntryInfoCMD 
      applicatorEntryInfoProcess = subprocess.Popen(applicatorEntryInfoCMD,shell=True,stdout=subprocess.PIPE )
      while ( applicatorEntryInfoProcess.poll() == None ):
         pass
      applicatorEntryInfo = applicatorEntryInfoProcess.stdout.readlines()
      print applicatorEntryInfo

      nerveRootInfoCMD = 'c3d %s -threshold %d %d 1 0 -centroid ' % (vtknerverootimage  , applicatorid['root'],applicatorid['root'])
      print nerveRootInfoCMD 
      nerveRootInfoProcess = subprocess.Popen(nerveRootInfoCMD,shell=True,stdout=subprocess.PIPE )
      while ( nerveRootInfoProcess.poll() == None ):
         pass
      nerveRootInfo = nerveRootInfoProcess.stdout.readlines()
      print nerveRootInfo

      spinalCordInfoCMD = 'c3d %s -threshold %d %d 1 0 -centroid ' % (vtknerverootimage  , applicatorid['cord'],applicatorid['cord'])
      print spinalCordInfoCMD 
      spinalCordInfoProcess = subprocess.Popen(spinalCordInfoCMD,shell=True,stdout=subprocess.PIPE )
      while ( spinalCordInfoProcess.poll() == None ):
         pass
      spinalCordInfo = spinalCordInfoProcess.stdout.readlines()
      print spinalCordInfo

      # build fem command
      dmplexCmd = '/home/ire/IrreversibleElectroporationSpine/Code/ireSolver -run_type full -dim 3 -petscspace_order 1 -variable_coefficient field  -snes_type ksponly  -snes_monitor -snes_converged_reason -ksp_converged_reason -ksp_rtol 1.e-6 -pc_type bjacobi -info -info_exclude null,pc,vec,mat '
      #dmplexCmd = './tcaPointSource -run_type full -dim 3 -petscspace_order 1 -variable_coefficient field  -snes_type ksponly  -snes_monitor -snes_converged_reason -ksp_converged_reason -ksp_rtol 1.e-12 -pc_type bjacobi -info -info_exclude null,vec,mat '
      dmplexCmd += '-f %s '   % config.get('setup','meshfile') 
      #tippoint   = eval(config.get('registration','tippoint'   ))
      #entrypoint = eval(config.get('registration','entrypoint' ))
      tippoint      = [idvox*dxvox for  idvox,dxvox in zip(eval(applicatorTipInfo[0].strip(  '\n').strip('CENTROID_VOX ')    ) ,spacing)]
      entrypoint    = [idvox*dxvox for  idvox,dxvox in zip(eval(applicatorEntryInfo[0].strip('\n').strip('CENTROID_VOX ')    ) ,spacing)]
      tippointvox   = eval(applicatorTipInfo[0].strip(  '\n').strip('CENTROID_VOX ') )   
      entrypointvox = eval(applicatorEntryInfo[0].strip('\n').strip('CENTROID_VOX ') )   
      nerverootvox  = eval(nerveRootInfo[0].strip(      '\n').strip('CENTROID_VOX ') )   
      spinalcordvox = eval(spinalCordInfo[0].strip(     '\n').strip('CENTROID_VOX ') )   
      print "extremes:", tippointvox, entrypointvox, nerverootvox, spinalcordvox 
      roiimage            = niftiimage.replace('.nii.gz',outputid+'.vtk')
      #FIXME -application specific hacks
      AxialROI = True
      AxialROI = False
      if(AxialROI):
        axialbounds   = [ int(min(tippointvox[2],entrypointvox[2],nerverootvox[2],spinalcordvox[2])), int(max(tippointvox[2],entrypointvox[2],nerverootvox[2],spinalcordvox[2]))+1]
        extractROICmd = 'c3d %s -region 0x0x%dvox %dx%dx%dvox -o %s' % (vtkimage, axialbounds[0], dimension[0],dimension[1],axialbounds[1]-axialbounds[0],roiimage )
        if(axialbounds[1] - axialbounds[0] > 10   ):
           print voltage,applicatorid 
           raise RuntimeError("too large domain")
      else:
        extractROICmd = 'c3d %s -o %s' % (vtkimage,roiimage )

      print extractROICmd 
      os.system(extractROICmd )
      dmplexCmd += '-vtk %s ' % roiimage            
                  
      SourceLandmarkFileName = "%s/sourcelandmarks.%s.vtk" % (jobid,outputid)
      TargetLandmarkFileName = "%s/targetlandmarks.%s.vtk" % (jobid,outputid)
      dmplexCmd += '-sourcelandmark %s ' % SourceLandmarkFileName
      dmplexCmd += '-targetlandmark %s ' % TargetLandmarkFileName
      # tissue dictionary should be of the form
      # types = { 'csf':2.0, 'grey':0.23 , 'white':0.23 , 'muscle':0.1 , 'bone':0.02 , 'fat':0.012 }
      # electric_conductivity = { 'csf':2.0, 'grey':0.23 , 'white':0.23 , 'muscle':0.1 , 'bone':0.02 , 'fat':0.012 }
      typeDictionary = eval(config.get('tissue','tissue_types' ))
      tissueDictionary = eval(config.get('tissue',worstcasetype))
      dmplexCmd += '-electric_conductivity %12.5e,%f,%f,%f,%f,%f,%f ' %  ( tissueDictionary[typeDictionary[0]],tissueDictionary[typeDictionary[1]],tissueDictionary[typeDictionary[2]], tissueDictionary[typeDictionary[3]],  tissueDictionary[typeDictionary[4]], tissueDictionary[typeDictionary[5]], tissueDictionary[typeDictionary[6]])
      #dmplexCmd += '-forcingconstant %f ' % config.getfloat('setup','forcingconstant')
      dmplexCmd += '-voltage %f ' % voltage
      dmplexCmd += '-dataid %s/%s ' % (jobid, outputid )

      # create applicator model
      transform  = GetApplicatorTransform(tippoint   ,entrypoint,SourceLandmarkFileName, TargetLandmarkFileName )
      inv = transform.GetInverse()
      print inv.GetMatrix()

      # build makefile
      fileHandle.write('%s: \n' %   outputid  )
      fileHandle.write('\t %s \n' %  dmplexCmd )
      if (controlrun):
        jobList.append(outputid  )
        jobListPost.append('%s.post' % outputid  )

      # rsample back to image
      fileHandle.write('\tpython /home/ire/IrreversibleElectroporationSpine/Code/ireSolver.py --resample=%s --outputid=%s/%s\n' %  (vtkimage,jobid,outputid) )

      # avg in nerve root
      fileHandle.write('%s.post: \n' %   outputid  )
      #FIXME header accuracy causing problems
      #avgCMD = "c3d %s/%s.nii.gz  %s -lstat > %s/%s.txt"  % (jobid,outputid ,vtknerverootimage ,jobid, outputid )
      avgCMD = "c3d %s/%s.vtk  %s -lstat > %s/%s.txt"  % (jobid,outputid ,vtknerverootimage ,jobid, outputid )
      fileHandle.write('\t%s \n' %  avgCMD )
      rootCMD = 'echo root;head -n 1 %s/%s.txt; cat %s/%s.txt'  % (jobid, outputid , jobid, outputid )
      fileHandle.write('\t%s \n' %  rootCMD )
      
  # tune
  fileHandle.write('tune: \n'  )
  fileHandle.write('\t %s -petscfe_type opencl -mat_petscfe_type  opencl  -log_summary > log.block.dflt.batch.dflt.txt \n' %  (dmplexCmd ))
  for nbatch in map(lambda x:int(math.pow(2,x)),[1,2,3,4,6,7]) :
     for nblock in map(lambda x:int(math.pow(2,x)),[1,2,3,4,6,7]) :
       fileHandle.write('\t %s -petscfe_type opencl -mat_petscfe_type  opencl -petscfe_num_blocks %d  -petscfe_num_batches %d -mat_petscfe_num_blocks  %d -mat_petscfe_num_batches %d -log_summary > log.block.%04d.batch.%04d.txt \n' %  (dmplexCmd,nblock,nbatch,nblock,nbatch, nblock,nbatch ))
  # close makefile
  fileHandle.flush()
  fileHandle.close()
  
  with file(jobmakefilename  , 'r') as original: datastream = original.read()
  # FIXME subset hack
  with file(jobmakefilename  , 'w') as modified: modified.write( "#all: ZZ14S026 ZZ14S025 ZZ14S023 ZZ14S024\nall: %s \npost: %s \n" % (' '.join(jobList),' '.join(jobListPost)) + datastream)
  # run the rest of it
  runandpostCMD = 'make -f %s all post' % jobmakefilename  
  print runandpostCMD 
  os.system( runandpostCMD )

elif (options.resample != None and  options.outputid != None ):
    # resample back to image
    print "resampling..."
    vtkImageReader = vtk.vtkDataSetReader() 
    vtkImageReader.SetFileName(options.resample)
    vtkImageReader.Update() 
    
    femoutputfile = "%ssolution.0001.vtk" %  options.outputid 
    vtkFemReader = vtk.vtkDataSetReader() 
    vtkFemReader.SetFileName(femoutputfile )
    vtkFemReader.Update() 

    # FIXME  can't get this working
    ## vtkGradient = vtk.vtkGradientFilter() 
    ## vtkGradient.SetInput( vtkFemReader.GetOutput() )
    ## vtkGradient.Update()

    ## # Use an ArrayCalculator to normalize TIME_LATE
    ## calc = vtk.vtkArrayCalculator()
    ## calc.SetInput( vtkGradient.GetOutput() )
    ## # Working on point data
    ## calc.SetAttributeModeToUsePointData()
    ## # Map scalar to s. When setting function, we can use s to
    ## # represent the array scalar (TIME_LATE) 
    ## calc.AddVectorVariable("s", "Gradients", 0)
    ## # Divide scalar by max (applies division to all components of the array)
    ## calc.SetFunction("norm(s)")
    ## # The output array will be called resArray
    ## calc.SetResultArrayName("resArray")
    ## calc.Update()

    vtkResample = vtk.vtkCompositeDataProbeFilter()
    #vtkResample.SetSource( calc.GetOutput() )
    vtkResample.SetSourceData( vtkFemReader.GetOutput() )
    vtkResample.SetInputData( vtkImageReader.GetOutput() ) 
    vtkResample.Update()

    # compute gradient of resampled image
    vtkGradMagn = vtk.vtkImageGradientMagnitude()
    vtkGradMagn.SetInputData( vtkResample.GetOutput() ) 
    vtkGradMagn.Update()

    # convert efield to V/cm
    shifter = vtk.vtkImageShiftScale()
    #shifter.SetShift(shift)
    shifter.SetScale(.01)
    #shifter.SetOutputScalarTypeToUnsignedChar()
    shifter.SetInputData(vtkGradMagn.GetOutput() )
    #shifter.ReleaseDataFlagOff()
    shifter.Update()

    # write to disk
    outputimage = shifter.GetOutput() 
    #outputimage.SetScalarArrayName("arrayname")
    print outputimage 
    #outputimage.Update()
    vtkFEMImageWriter = vtk.vtkDataSetWriter() 
    vtkFEMImageWriter.SetFileTypeToBinary() 
    vtkFEMImageWriter.SetInputData( outputimage )
    vtkFEMImageWriter.SetFileName( '%s.vtk' % options.outputid )
    vtkFEMImageWriter.Update() 

    # compress
    compressCMD = "c3d %s.vtk -o %s.nii.gz; " % (options.outputid ,options.outputid )
    print compressCMD 
    os.system( compressCMD )

    ## matoutputfile = "%smaterial.vtk" %  options.outputid 
    ## vtkMatReader = vtk.vtkDataSetReader() 
    ## vtkMatReader.SetFileName(matoutputfile )
    ## vtkMatReader.Update() 
    ## print "matreader"

    ## vtkResampleMat = vtk.vtkCompositeDataProbeFilter()
    ## #vtkResample.SetSource( calc.GetOutput() )
    ## vtkResampleMat.SetSource( vtkMatReader.GetOutput() )
    ## vtkResampleMat.SetInput( vtkImageReader.GetOutput() ) 
    ## vtkResampleMat.Update()
    ## print "resample"

    ## # FIXME - hack ensure image data
    ## hackshifter = vtk.vtkImageShiftScale()
    ## #hackshifter.SetShift(shift)
    ## hackshifter.SetScale(1.0)
    ## #hackshifter.SetOutputScalarTypeToUnsignedChar()
    ## hackshifter.SetInput(vtkResampleMat.GetOutput() )
    ## #hackshifter.ReleaseDataFlagOff()
    ## hackshifter.Update()
    ## print "shift"

    ## # write to disk
    ## print hackshifter.GetOutput()
    ## vtkMatImageWriter = vtk.vtkDataSetWriter() 
    ## vtkMatImageWriter.SetFileTypeToBinary() 
    ## vtkMatImageWriter.SetInput( hackshifter.GetOutput() )
    ## vtkMatImageWriter.SetFileName( '%smat.vtk' % options.outputid )
    ## vtkMatImageWriter.Update() 

else:
  parser.print_help()
  print options
