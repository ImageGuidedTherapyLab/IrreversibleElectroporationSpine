SHELL := /bin/bash
ATROPOSCMD=$(ANTSPATH)/Atropos -d $(DIMENSION)  -c [3,0.0] 
C3DEXE=/rsrch2/ip/dtfuentes/bin/c3d -verbose
NTISSUE = 4
DIMENSION = 3
LUNGHU=-800
FATHU=-100
LIVERHU=60
CONTRASTHU=300

# keep tmp files
.SECONDARY: 
%/anatomymask.nii.gz: %/anatomy.nii.gz
	$(C3DEXE) $< -thresh -900 inf 1 0 -o $@
%/anatomygmm.nii.gz: %/anatomy.nii.gz %/anatomymask.nii.gz
	$(ATROPOSCMD) -d $(DIMENSION)  -c [3,0.0]  -m [0.1,1x1x1] -i kmeans[$(NTISSUE),$(LUNGHU)x$(FATHU)x$(LIVERHU)x$(CONTRASTHU)] -x $(word 2,$^) -a $<  -o $@
%/setupgmm.nii.gz: %/anatomygmm.nii.gz %/setup.nii.gz
	$(C3DEXE) $<  $(word 2,$^) -binarize  -replace 1 0 0 1 -multiply  -o $*/tmpsetup.nii.gz
	$(C3DEXE) $*/tmpsetup.nii.gz  $(word 2,$^) -add  -o $@
%/sum.nii.gz: 
	count=0; for idlabel in  $(*D)/*/label.nii.gz ; do $(C3DEXE) $*/anatomy.nii.gz -info $$idlabel -info -binarize -replace 1 $$count  -reslice-identity -o $*/tmp.$$count.nii.gz ; ((count++)); done
	$(C3DEXE) $*/tmp.*.nii.gz  -accum -add -endaccum -o $*/sum.nii.gz
%/setup.nii.gz: %/sum.nii.gz
	if [ ! -f $@  ] ; then $(C3DEXE) $< -type uchar  $*/setup.nii.gz ;fi
%/setup: 
	vglrun itksnap -s  $*/setup.nii.gz -g $*/anatomy.nii.gz -l material.txt
