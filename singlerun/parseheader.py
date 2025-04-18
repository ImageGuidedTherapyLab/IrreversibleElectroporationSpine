import nrrd


fileList = ['dog_1_final_needle_center.seg.nrrd',  'Dog 2 Final_4_8_25.seg.nrrd','dog3_final_segmentation_corrected.seg.nrrd',]

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

print("dog1L1.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog1L3.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog1L5.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog1T11.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog1T12.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )


print("dog2L1.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog2L3.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog2L5.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog2T12.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )

print("dog3L3.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog3L5.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )
print("dog3T12.ini: tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary[3]['L5_muscle'], labeldictionary[3]['L5_bone'], labeldictionary[3]['L5_needle'], labeldictionary[3]['L5_needle_tip'], labeldictionary[3]['L5_needle_bottom'], labeldictionary[3]['L5_bone_tumor'], labeldictionary[3]['CSF'], labeldictionary[3]['L5_cord'], labeldictionary[3]['L5_root_left'], labeldictionary[3]['L5_nerve_root_right']) )

