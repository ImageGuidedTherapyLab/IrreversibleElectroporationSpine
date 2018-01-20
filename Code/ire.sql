-- CREATE DATABASE `DFElectroporation` CHARACTER SET utf8 COLLATE utf8_unicode_ci;
-- select * from DFElectroporation.metadata;
-- set db
use DFElectroporation;

DROP TABLE IF EXISTS DFElectroporation.metadata;
CREATE TABLE DFElectroporation.metadata( 
   id    bigint(20) NOT NULL AUTO_INCREMENT,
   MRN                 VARCHAR( 64) NOT NULL  COMMENT 'patient uid',
   StudyUID            VARCHAR(256) not NULL  COMMENT 'study UID'  ,
   SeriesUID           VARCHAR(256) not NULL  COMMENT 'series UID' ,
   ImageUID            VARCHAR(256) not NULL  COMMENT 'image UID'  ,
   StudyDate                   DATE         NULL COMMENT 'Study Date',
   data                        JSON         NULL ,
   PRIMARY KEY (id) 
   ) select JSON_UNQUOTE(eu.data->"$.""MRN""") mrn,
   JSON_UNQUOTE(eu.data->"$.""Date""") studydate,
   JSON_UNQUOTE(eu.data->"$.""STUDY UID""")  studyuid,
   JSON_UNQUOTE(eu.data->"$.""SERIES UID""") seriesuid,
   JSON_UNQUOTE(eu.data->"$.""IMAGE UID""")  imageuid, eu.data data
   FROM ClinicalStudies.excelUpload eu where eu.uploadID = 81 and JSON_UNQUOTE(eu.data->"$.""MRN""") is not null;


select concat(concat_ws('/',replace(rf.mrn,' ','_'),REPLACE(rf.StudyDate, '-', ''),rf.StudyUID,rf.seriesuid),'/CT.',rf.imageuid,'.annotationSignature.nii.gz') uid from DFElectroporation.metadata rf where rf.studyuid not like "%control%";
