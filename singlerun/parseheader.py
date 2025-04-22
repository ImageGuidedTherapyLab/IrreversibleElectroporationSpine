import nrrd
import csv

fileList = ['dog1.nrrd',  'dog2.nrrd','dog3.nrrd']

labeldictionary = {}
# Read the NRRD file
for iddog,myfile in enumerate(fileList):
  print("%s@########################################################### " %myfile )
  data, header = nrrd.read(myfile)
  labeldictionary[iddog+1] = {}
  
  # Access header information, including label fields
  if 'Segment0_Name' in header:
      i = 0
      while f'Segment{i}_Name' in header:
          segment_name = header[f'Segment{i}_Name']
          segment_label_value = header[f'Segment{i}_LabelValue']
          print(f"Segment {i}: Name = {segment_name}, Label Value = {segment_label_value}")
          labeldictionary[iddog+1][segment_name ] = segment_label_value 
          i += 1
  else:
      print("No label field found in the NRRD header.")

initemplate = """
[tissue]
; create uniform tissues for simulation
%s
#
tissue_types = {  6:'cord' , 5:'csf' , 3:'applicator', 0:'default' ,1:'muscle' , 2:'bone' , 4:'tumor' }
#S/m; 
electric_conductivity    = { 'csf':2.0, 'cord':0.23 , 'applicator':2.0 ,'default':0.1  ,'muscle':0.1 , 'bone':0.02  , 'fat':0.012 , 'tumor':1.0 }
electric_conductivity_lb = { 'csf':1.0, 'cord':0.08 , 'applicator':1.0 ,'default':0.04 ,'muscle':0.04, 'bone':0.002 , 'fat':0.002 }
electric_conductivity_ub = { 'csf':3.0, 'cord':0.53 , 'applicator':3.0 ,'default':0.18 ,'muscle':0.18, 'bone':0.024 , 'fat':0.022 }
[setup]
# volts (labels)
; "applicator tip" is the centroid of the positve and negative electrodes. Should be 1.1cm  from the applicator end/tip seen in the image
%s
imagefile = '%s/segmentation.nii.gz'
sed = %s
meshfile  = meshIREmidres.e
"""


with open('dog1L1.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['L1_muscle'], labeldictionary[1]['L1_bone'], labeldictionary[1]['L1_needle'], labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end'], labeldictionary[1]['L1_bone_tumor'], labeldictionary[1]['L1_CSF'], labeldictionary[1]['L1_cord'], labeldictionary[1]['L1_nerve_root_left'], labeldictionary[1]['L1_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog1L1,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog1L1/electric_conductivity.2700.%s.%s.txt >  dog1L1/electric_conductivity.2700.%s.%s.csv' %(labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end'],labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogone',sedcmd ))


with open('dog1L3.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['L3_muscle'], labeldictionary[1]['L3_bone'], labeldictionary[1]['L3_needle'], labeldictionary[1]['L3_needle_tip'], labeldictionary[1]['L3_needle_end'], labeldictionary[1]['L3_muscle_tumor'],labeldictionary[1]['L3_bone_tumor'], labeldictionary[1]['L3_CSF'], labeldictionary[1]['L3_cord'], labeldictionary[1]['L3_nerve_root_left'], labeldictionary[1]['L3_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['L3_needle_tip'], labeldictionary[1]['L3_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog1L3,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog1L3/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[1]['L3_needle_tip'], labeldictionary[1]['L3_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogone',sedcmd ))
    
with open('dog1L5.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['L5_muscle'], labeldictionary[1]['L5_bone'], labeldictionary[1]['L5_needle'], labeldictionary[1]['L5_needle_tip'], labeldictionary[1]['L5_needle_end'], labeldictionary[1]['L5_muscle_tumor'],labeldictionary[1]['L5_bone_tumor'], labeldictionary[1]['L5_CSF'], labeldictionary[1]['L5_cord'], labeldictionary[1]['L5_nerve_root_left'], labeldictionary[1]['L5_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['L5_needle_tip'], labeldictionary[1]['L5_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog1L5,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog1L5/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[1]['L5_needle_tip'], labeldictionary[1]['L5_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogone',sedcmd ))
    
with open('dog1T11.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['T11_muscle'], labeldictionary[1]['T11_bone'], labeldictionary[1]['T11_needle'], labeldictionary[1]['T11_needle_tip'], labeldictionary[1]['T11_needle_end'], labeldictionary[1]['T11_muscle_tumor'], labeldictionary[1]['T11_bone_tumor'], labeldictionary[1]['T11_CSF'], labeldictionary[1]['T11_cord'], labeldictionary[1]['T11_nerve_root_left'], labeldictionary[1]['T11_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['T11_needle_tip'], labeldictionary[1]['T11_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog1T11,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog1T11/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[1]['T11_needle_tip'], labeldictionary[1]['T11_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogone',sedcmd ))
    
with open('dog1T12.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['T12_muscle'], labeldictionary[1]['T12_bone'], labeldictionary[1]['T12_needle'], labeldictionary[1]['T12_needle_tip'], labeldictionary[1]['T12_needle_end'], labeldictionary[1]['T12_bone_tumor'], labeldictionary[1]['T12_CSF'], labeldictionary[1]['T13_cord'], labeldictionary[1]['T12_nerve_root_left'], labeldictionary[1]['T12_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['T12_needle_tip'], labeldictionary[1]['T12_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog1T12,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog1T12/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[1]['T12_needle_tip'], labeldictionary[1]['T12_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogone',sedcmd ))
    
    
with open('dog2L1.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['L1_muscle'], labeldictionary[2]['L1_bone'], labeldictionary[2]['L1_needle'], labeldictionary[2]['L1_needle_midpoint'], labeldictionary[2]['L1_needle_end'], labeldictionary[2]['L1_bone_tumor'], labeldictionary[2]['L1_CSF'], labeldictionary[2]['L1_spinal_cord'], labeldictionary[2]['L1_nerve_root_left'], labeldictionary[2]['L1_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['L1_needle_midpoint'] , labeldictionary[2]['L1_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog2L1,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog2L1/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[2]['L1_needle_midpoint'], labeldictionary[2]['L1_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogtwo',sedcmd ))
    
with open('dog2L3.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['L3_muscle'], labeldictionary[2]['L3_bone'], labeldictionary[2]['L3_needle'], labeldictionary[2]['L3_needle_midpoint'], labeldictionary[2]['L3_needle_end'], labeldictionary[2]['L3_bone_tumor'], labeldictionary[2]['L3_CSF'], labeldictionary[2]['L3_spinal_cord'], labeldictionary[2]['L3_nerve_root_left'], labeldictionary[2]['L3_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['L3_needle_midpoint'] , labeldictionary[2]['L3_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog2L3,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog2L3/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[2]['L3_needle_midpoint'], labeldictionary[2]['L3_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogtwo',sedcmd ))
    
with open('dog2L5.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['L5_muscle'], labeldictionary[2]['L5_bone'], labeldictionary[2]['L5_needle'], labeldictionary[2]['L5_needle_midpoint'], labeldictionary[2]['L5_needle_end'], labeldictionary[2]['L5_bone_tumor'], labeldictionary[2]['L5_CSF'], labeldictionary[2]['L5_spinal_cord'], labeldictionary[2]['L5_nerve_root_left'], labeldictionary[2]['L5_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['L5_needle_midpoint'] , labeldictionary[2]['L5_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog2L5,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog2L5/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[2]['L5_needle_midpoint'], labeldictionary[2]['L5_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogtwo',sedcmd ))
    
with open('dog2T12.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['T12_muscle'], labeldictionary[2]['T12_bone'], labeldictionary[2]['T12_needle'], labeldictionary[2]['T12_needle_midpoint'], labeldictionary[2]['T12_needle_end'], labeldictionary[2]['T12_bone_tumor'], labeldictionary[2]['T12_CSF'], labeldictionary[2]['T12_spinal_cord'], labeldictionary[2]['T12_nerve_root_left'], labeldictionary[2]['T12_nerve_root_right']) 
    voltagelist   = "voltageList = [  (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['T12_needle_midpoint'], labeldictionary[2]['T12_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog2T12,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog2T12/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[2]['T12_needle_midpoint'], labeldictionary[2]['T12_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogtwo',sedcmd ))
    
with open('dog3L3.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L3_muscle'], labeldictionary[3]['L3_bone'], labeldictionary[3]['L3_needle'], labeldictionary[3]['L3_needle_center'], labeldictionary[3]['L3_needle_end'], labeldictionary[3]['L3_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L3_cord'], labeldictionary[3]['L3_nerve_root_left'], labeldictionary[3]['L3_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[3]['L3_needle_center'] , labeldictionary[3]['L3_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog3L1,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog3L1/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[3]['L3_needle_center'], labeldictionary[3]['L3_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogthree',sedcmd ))
    
with open('dog3L5.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_center'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) 
    voltagelist   = "voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[3]['L5_needle_center'] , labeldictionary[3]['L5_needle_bottom']) 
    sedcmd        = 'sed "s/^\s\+/dog3L5,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog3L5/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogthree',sedcmd ))
    
with open('dog3T12.ini', 'w', encoding="utf-8") as f:
    tissuereplace = "tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['T12_muscle'], labeldictionary[3]['T12_bone'], labeldictionary[3]['T12_needle'], labeldictionary[3]['T12_needle_center'], labeldictionary[3]['T12_needle_end'], labeldictionary[3]['T12_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['T12_cord'], labeldictionary[3]['T12_nerve_root_left'], labeldictionary[3]['T11_nerve_root_right']) 
    voltagelist   = "voltageList = [  (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[3]['T12_needle_center'], labeldictionary[3]['T12_needle_end']) 
    sedcmd        = 'sed "s/^\s\+/dog3T12,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog3T12/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[3]['T12_needle_tip'], labeldictionary[3]['T12_needle_end'])
    f.write(initemplate %(tissuereplace, voltagelist, 'dogthree',sedcmd ))


with open('labeldictionary.csv', 'w', newline='') as csvfile:
    fieldnames = ['UID', 'labelID', 'label']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for iddog in [1,2,3]:
      for key, value in labeldictionary[iddog].items():
        print(f"Key: {key}, Value: {value}")
        writer.writerow({'UID': 'dog%d' % iddog, 'labelID': key, 'label':labeldictionary[iddog][key]})


print('sqlite3 $(SQLITEDB)  -init .loadcsvsqliterc ".import $< lstat"')
