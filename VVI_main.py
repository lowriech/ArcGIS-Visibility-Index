import arcpy
import numpy
import csv
import math
import VVI_class


#load spatial and 3d analyst extensions
try:
    if arcpy.CheckExtension("3D") == "Available":
        arcpy.CheckOutExtension("3D")
    else:
        raise LicenseError
    from arcpy.sa import *
    arcpy.CheckOutExtension("spatial")   
    arcpy.CheckOutExtension("analysis") 
    
except LicenseError:
    print "3D Analyst or Spatial Analyst license is unavailable"
except:
    print arcpy.GetMessages(2)

#TODO: How does this conflict (or not) with multiprocessing
arcpy.env.parallelProcessingFactor = "100%"
arcpy.env.overwriteOutput = True

#Get Parameters
CellValues = arcpy.GetParameterAsText(0)
CV_Z = arcpy.GetParameterAsText(1)
CV_Slope = arcpy.GetParameterAsText(2)
CV_Aspect = arcpy.GetParameterAsText(3)
CV_XY = arcpy.GetParameterAsText(4)
FileName = arcpy.GetParameterAsText(5)
ViewPoints = arcpy.GetParameterAsText(6)
Viewpoint_Z = arcpy.GetParameterAsText(7)
Viewshed_Folder = arcpy.GetParameterAsText(8)
scratchspace = arcpy.GetParameterAsText(9)




if not CV_XY:
    arcpy.AddXY_management(CellValues)

#TODO: deprecate with native way to select to save as a csv using ArcGIS interface
if FileName[-4:] != '.csv':
    FileName = str(FileName) + ".csv"

# Open up the CSV writer
headings = ['ViewPoint_ID', 'RawTotal']
outfile = open(FileName, 'wb')
writer = csv.writer(outfile, delimiter = ',', quotechar = '"')
writer.writerow(headings)


VVI = VVI_class.Visibility_Measure(CellValues, CV_Z, CV_Slope, CV_Aspect, CV_XY, FileName, ViewPoints, Viewpoint_Z, Viewshed_Folder, scratchspace, writer)
    
outfile.close()