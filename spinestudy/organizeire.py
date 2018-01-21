import MySQLdb
import os
""" Organize IRE Data
"""

sqldb = MySQLdb.connect(host="scrdep2.mdanderson.org",    # your host, usually localhost
                        read_default_file="~/.my.cnf",    # username password
                        db="DFElectroporation")        # name of the data base
sqlcur = sqldb.cursor()
# :set syntax=sql          :set syntax=python
querydata= """ 
select concat(concat_ws('/',replace(rf.mrn,' ','_'),REPLACE(rf.StudyDate, '-', ''),rf.StudyUID,rf.seriesuid),'/CT.',rf.imageuid,'.annotationSignature.nii.gz') uid from DFElectroporation.metadata rf where rf.studyuid not like "%control%";
"""
sqlcur.execute(querydata)
queryNames= [description[0] for description in sqlcur.description]
datalist = [dict(zip(queryNames,x)) for x in sqlcur]
print queryNames #, queryDict

for iddata in datalist:
   uidinfo =  iddata['uid'].split('/')
   datadir = uidinfo [0]
   localdir = 'spinestudy/' + '/'.join(uidinfo[:-1]) + '/' + uidinfo[-1].replace('.annotationSignature.nii.gz','')
   seriesdir = "/FUS4/IPVL_research_anno/" + "/".join(uidinfo [:-1])
   imageuid = uidinfo [4].replace('.annotationSignature.nii.gz','')
   imagenumber = int(imageuid.split('.')[-1])
   print datadir,localdir, seriesdir ,imageuid ,imagenumber
   filelist = []
   for sliceid in  range(imagenumber-5,imagenumber+5) :
       slicefile = seriesdir + '/' + '.'.join(imageuid.split('.')[:-1]) + '.%d' % sliceid
       filelist.append( slicefile)
   createlocaldir = 'mkdir -p %s/dicom; cp %s %s/dicom; DicomSeriesReadImageWrite2 %s/dicom %s/anatomy.nii.gz' %(localdir,' '.join(filelist),localdir,localdir,localdir)
   print createlocaldir 
   # FIXME check if file exists
   #os.system( createlocaldir )
   copyannotation = "c3d %s/anatomy.nii.gz /FUS4/IPVL_research_anno/%s -pad 0x0x5vox 0x0x4vox  0 -copy-transform -info -type uchar -o %s/applicator.nii.gz" % (localdir, iddata['uid'],localdir)
   print copyannotation 
   # FIXME check if file exists
   #os.system( copyannotation )

