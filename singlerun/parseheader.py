import nrrd


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

print("dog1L1.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['L1_muscle'], labeldictionary[1]['L1_bone'], labeldictionary[1]['L1_needle'], labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end'], labeldictionary[1]['L1_bone_tumor'], labeldictionary[1]['L1_CSF'], labeldictionary[1]['L1_cord'], labeldictionary[1]['L1_nerve_root_left'], labeldictionary[1]['L1_nerve_root_right']) )
print("dog1L1.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end']) )
print(' sed "s/^\s\+/dog1L1,/g;s/\s\+/,/g;s/LabelID/InstanceUID,LabelID/g;s/Vol(mm^3)/Vol.mm.3/g;s/Extent(Vox)/ExtentX,ExtentY,ExtentZ/g"  dog1L1/electric_conductivity.2700.%s.%s.txt' %(labeldictionary[1]['L1_needle_tip'], labeldictionary[1]['L1_needle_end']))

print("dog1L3.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['L3_muscle'], labeldictionary[1]['L3_bone'], labeldictionary[1]['L3_needle'], labeldictionary[1]['L3_needle_tip'], labeldictionary[1]['L3_needle_end'], labeldictionary[1]['L3_muscle_tumor'],labeldictionary[1]['L3_bone_tumor'], labeldictionary[1]['L3_CSF'], labeldictionary[1]['L3_cord'], labeldictionary[1]['L3_nerve_root_left'], labeldictionary[1]['L3_nerve_root_right']) )
print("dog1L3.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['L3_needle_tip'], labeldictionary[1]['L3_needle_end']) )

print("dog1L5.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['L5_muscle'], labeldictionary[1]['L5_bone'], labeldictionary[1]['L5_needle'], labeldictionary[1]['L5_needle_tip'], labeldictionary[1]['L5_needle_end'], labeldictionary[1]['L5_muscle_tumor'],labeldictionary[1]['L5_bone_tumor'], labeldictionary[1]['L5_CSF'], labeldictionary[1]['L5_cord'], labeldictionary[1]['L5_nerve_root_left'], labeldictionary[1]['L5_nerve_root_right']) )
print("dog1L5.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['L5_needle_tip'], labeldictionary[1]['L5_needle_end']) )

print("dog1T11.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['T11_muscle'], labeldictionary[1]['T11_bone'], labeldictionary[1]['T11_needle'], labeldictionary[1]['T11_needle_tip'], labeldictionary[1]['T11_needle_end'], labeldictionary[1]['T11_muscle_tumor'], labeldictionary[1]['T11_bone_tumor'], labeldictionary[1]['T11_CSF'], labeldictionary[1]['T11_cord'], labeldictionary[1]['T11_nerve_root_left'], labeldictionary[1]['T11_nerve_root_right']) )
print("dog1T11.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['T11_needle_tip'], labeldictionary[1]['T11_needle_end']) )

print("dog1T12.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[1]['T12_muscle'], labeldictionary[1]['T12_bone'], labeldictionary[1]['T12_needle'], labeldictionary[1]['T12_needle_tip'], labeldictionary[1]['T12_needle_end'], labeldictionary[1]['T12_bone_tumor'], labeldictionary[1]['T12_CSF'], labeldictionary[1]['T13_cord'], labeldictionary[1]['T12_nerve_root_left'], labeldictionary[1]['T12_nerve_root_right']) )
print("dog1T12.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[1]['T12_needle_tip'], labeldictionary[1]['T12_needle_end']) )


print("dog2L1.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['L1_muscle'], labeldictionary[2]['L1_bone'], labeldictionary[2]['L1_needle'], labeldictionary[2]['L1_needle_midpoint'], labeldictionary[2]['L1_needle_end'], labeldictionary[2]['L1_bone_tumor'], labeldictionary[2]['L1_CSF'], labeldictionary[2]['L1_spinal_cord'], labeldictionary[2]['L1_nerve_root_left'], labeldictionary[2]['L1_nerve_root_right']) )
print("dog2L1.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['L1_needle_midpoint'] , labeldictionary[2]['L1_needle_end']) )

print("dog2L3.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['L3_muscle'], labeldictionary[2]['L3_bone'], labeldictionary[2]['L3_needle'], labeldictionary[2]['L3_needle_midpoint'], labeldictionary[2]['L3_needle_end'], labeldictionary[2]['L3_bone_tumor'], labeldictionary[2]['L3_CSF'], labeldictionary[2]['L3_spinal_cord'], labeldictionary[2]['L3_nerve_root_left'], labeldictionary[2]['L3_nerve_root_right']) )
print("dog2L3.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['L3_needle_midpoint'] , labeldictionary[2]['L3_needle_end']) )

print("dog2L5.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['L5_muscle'], labeldictionary[2]['L5_bone'], labeldictionary[2]['L5_needle'], labeldictionary[2]['L5_needle_midpoint'], labeldictionary[2]['L5_needle_end'], labeldictionary[2]['L5_bone_tumor'], labeldictionary[2]['L5_CSF'], labeldictionary[2]['L5_spinal_cord'], labeldictionary[2]['L5_nerve_root_left'], labeldictionary[2]['L5_nerve_root_right']) )
print("dog2L5.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['L5_needle_midpoint'] , labeldictionary[2]['L5_needle_end']) )

print("dog2T12.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[2]['T12_muscle'], labeldictionary[2]['T12_bone'], labeldictionary[2]['T12_needle'], labeldictionary[2]['T12_needle_midpoint'], labeldictionary[2]['T12_needle_end'], labeldictionary[2]['T12_bone_tumor'], labeldictionary[2]['T12_CSF'], labeldictionary[2]['T12_spinal_cord'], labeldictionary[2]['T12_nerve_root_left'], labeldictionary[2]['T12_nerve_root_right']) )
print("dog2T12.ini: voltageList = [  (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[2]['T12_needle_midpoint'], labeldictionary[2]['T12_needle_end']) )

print("dog3L3.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L3_muscle'], labeldictionary[3]['L3_bone'], labeldictionary[3]['L3_needle'], labeldictionary[3]['L3_needle_center'], labeldictionary[3]['L3_needle_end'], labeldictionary[3]['L3_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L3_cord'], labeldictionary[3]['L3_nerve_root_left'], labeldictionary[3]['L3_nerve_root_right']) )
print("dog3L3.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[3]['L3_needle_center'] , labeldictionary[3]['L3_needle_end']) )

print("dog3L5.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_center'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog3L5.ini: voltageList = [   (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[3]['L5_needle_center'] , labeldictionary[3]['L5_needle_bottom']) )

print("dog3T12.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['T12_muscle'], labeldictionary[3]['T12_bone'], labeldictionary[3]['T12_needle'], labeldictionary[3]['T12_needle_center'], labeldictionary[3]['T12_needle_end'], labeldictionary[3]['T12_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['T12_cord'], labeldictionary[3]['T12_nerve_root_left'], labeldictionary[3]['T11_nerve_root_right']) )
print("dog3T12.ini: voltageList = [  (2700,{'tip':%s, 'entry':%s, 'root':6, 'cord':6}) ]" % (labeldictionary[3]['T12_needle_center'], labeldictionary[3]['T12_needle_end']) )


print('sqlite3 $(SQLITEDB)  -init .loadcsvsqliterc ".import $< lstat"')
