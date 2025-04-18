import nrrd


fileList = ['dog_1_final_needle_center.seg.nrrd',  'Dog 2 Final_4_8_25.seg.nrrd','dog3_final_segmentation_corrected.seg.nrrd',]

# Read the NRRD file
for myfile in fileList:
  print("%s@########################################################### " %myfile )
  data, header = nrrd.read('dog3_final_segmentation_corrected.seg.nrrd')
  
  labeldictionary = {}
  
  # Access header information, including label fields
  if 'Segment0_Name' in header:
      i = 0
      while f'Segment{i}_Name' in header:
          segment_name = header[f'Segment{i}_Name']
          segment_label_value = header[f'Segment{i}_LabelValue']
          print(f"Segment {i}: Name = {segment_name}, Label Value = {segment_label_value}")
          labeldictionary[segment_name ] = segment_label_value 
          i += 1
  else:
      print("No label field found in the NRRD header.")

print("tissue_replace = %s 1 %s 2 %s 3 %s 3 %s 3 %s 4 %s 5 %s 6  %s 6 %s 6" % (labeldictionary['L5_muscle'], labeldictionary['L5_bone'], labeldictionary['L5_needle'], labeldictionary['L5_needle_tip'], labeldictionary['L5_needle_bottom'], labeldictionary['L5_bone_tumor'], labeldictionary['CSF'], labeldictionary['L5_cord'], labeldictionary['L5_root_left'], labeldictionary['L5_nerve_root_right']) )

