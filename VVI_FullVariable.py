import arcpy
import numpy
import csv
import math

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

arcpy.env.parallelProcessingFactor = "100%"
arcpy.env.overwriteOutput = True


def ViewAngle (a, b, c):
    "calculates the viewing angle of each visible cell"
    a2 = a*a
    b2 = b*b
    c2 = c*c
    VA = (a2-b2+c2)/ (2.0 * (a*c))
    rads = math.acos(VA)
    return math.degrees(rads)


def Cell_Loc (VP_X, VP_Y, cent_x, cent_y, aspect, cell_res):
    AspectTan = math.tan(math.radians(aspect))
    Opposite = (AspectTan * cell_res)
    LowCornerX = cent_x - 2.5
    LowCornerY = cent_y - (Opposite/2.0)
    HiCornerX = cent_x + 2.5
    HiCornerY = cent_y + (Opposite/2.0)
    ViewPoint_X = VP_X
    ViewPoint_Y = VP_Y
    
    dist1 = math.hypot(ViewPoint_X-LowCornerX, ViewPoint_Y-LowCornerY)
    dist2 = math.hypot(ViewPoint_X-HiCornerX, ViewPoint_Y-HiCornerY)
    dist3 = math.hypot(LowCornerX-HiCornerX, LowCornerY-HiCornerY)
    
    return dist1, dist2, dist3


def Vert_Angle (VP_X, VP_Y, VP_Z, cent_x, cent_y, cent_z):
    #incorrectly named, should be called the hypotenuse or distance...
    Adj = math.hypot(VP_X-cent_x, VP_Y-cent_y)
    Opp = (cent_z - VP_Z)
    AngleTan = math.atan(Opp/Adj)
    return math.degrees(AngleTan), Adj, Opp, cent_z, VP_Z


    

def AspectSector (VP_X, VP_Y, cent_x, cent_y):
    asp = 180  + math.atan2((VP_X - cent_x), (VP_Y - cent_y)) * (180 / math.pi)
    if asp > 180:
        return asp - 180.0
    else:
        return asp + 180
    


#CellValues with elevation, slope, and aspect data
CellValues = arcpy.GetParameterAsText(0)
#the elevation field
CV_Z = arcpy.GetParameterAsText(1)
#the slope field
CV_Slope = arcpy.GetParameterAsText(2)
#the aspect field
CV_Aspect = arcpy.GetParameterAsText(3)
#does the data already have XY data in its table?  If not it will be calculated
CV_XY = arcpy.GetParameterAsText(4)
#name for the output CSV
FileName = arcpy.GetParameterAsText(5)
#the VP shapefile
ViewPoints = arcpy.GetParameterAsText(6)
#the vp elevation field
Viewpoint_Z = arcpy.GetParameterAsText(7)
#folder containing precalculated viewsheds
Viewshed_Folder = arcpy.GetParameterAsText(8)
#scratchspace for intermediate points, will be deprecated
scratchspace = arcpy.GetParameterAsText(9)

if not CV_XY:
    arcpy.AddXY_management(CellValues)

#will be deprecated if there is a native way of selecting to save a csv file
if FileName[-4:] != '.csv':
    FileName = str(FileName) + ".csv"

# Open up the CSV writer
headings = ['ViewPoint_ID', 'RawTotal', 'AdjustTotal', 'No_Err', 'Folder_Dir', 'AspectErrors', 'SlopeErrors', 'Success', '300', 'CloseCellsSlope', '3000', 'MidcellsSlope', '6000', 'FarCellsSlope', '6000_plus', 'DistCellsSlope', 'VP_X', 'VP_Y']
outfile = open(FileName, 'wb')
writer = csv.writer(outfile, delimiter = ',', quotechar = '"')
writer.writerow(headings)

#currently only analyzing bluespace.  However, this could be changed by point to analyze both blue and greenspace
environment = 'bluespace'


VPs = arcpy.SearchCursor(ViewPoints)


for Viewpoint in VPs:
    #Create a single point shapefile
    #This can likely be shortened
    whereClause = '"FID" = ' + str(Viewpoint.FID)
    arcpy.MakeFeatureLayer_management(ViewPoints, "in_memory\\curVP" + str(Viewpoint.FID), whereClause)
    arcpy.CopyFeatures_management(("in_memory\\curVP" + str(Viewpoint.FID)), scratchspace + "\\curVP" + str(Viewpoint.FID) + ".shp") 
    ViewPoint = scratchspace + "\\curVP" + str(Viewpoint.FID) + ".shp"
    arcpy.AddXY_management(ViewPoint)
    ViewPointSearch = arcpy.SearchCursor(ViewPoint)
    #The search cursor only runs through one point, hence this can likely be shortened
    for row in ViewPointSearch:
        ViewPoint_XYZ = row.POINT_X, row.POINT_Y, row.getValue(Viewpoint_Z)
    
    #path to the viewshed file
    #ideally this could also link into the table of VPs
    view_extent = Viewshed_Folder + "\\poly_" + str(Viewpoint.FID) +".shp"
    arcpy.RepairGeometry_management (view_extent)
    
    #Clip the Cell Values using the view extent
    visible_pts = scratchspace + "\\vis_pts_" + str(Viewpoint.FID) + ".shp"
    arcpy.Clip_analysis (CellValues, view_extent, visible_pts)
    
    #reset the counts
    count, runningtotal, runningtotal2, aspectcount, AngleCount, successcount, CloseCells, MidCells, FarCells, DistCells = 0,0,0,0,0,0,0,0,0,0
    CloseCellsSlope, MidCellsSlope, FarCellsSlope, DistCellsSlope = [], [], [], []
    VisibleCellsSearch = arcpy.SearchCursor(visible_pts) 
    
    for cell in VisibleCellsSearch:
        # 0 1 2 3     4
        # X Y Z Slope Aspect
        Cell_Props = cell.POINT_X, cell.POINT_Y, cell.getValue(CV_Z), cell.getValue(CV_Slope), cell.getValue(CV_Aspect)
            
        # calculate the verticle angle between observor and cell
        # If verticle angle is negative then viewpoint below obdservor and therefore influnce of aspect needs to be modified.;
        
        #vertical angle, hypotenuse, delta_z, cell_z, VP_z
        #Currently returning a bunch of unused, redundant variables
        VerticalAngle = Vert_Angle(ViewPoint_XYZ[0], ViewPoint_XYZ[1], ViewPoint_XYZ[2], Cell_Props[0], Cell_Props[1], Cell_Props[4])
            
        '''If cell slope greater than vertical angle continue, else break'''
        if VerticalAngle[0] <= Cell_Props[2]:
            '''calculate distances between cells and viewpoint for use in calculating the degrees of visibility''' 
            distances = Cell_Loc (ViewPoint_XYZ[0], ViewPoint_XYZ[1], Cell_Props[0], Cell_Props[1], Cell_Props[2], 5)
                
            Hyp = max(distances)
            Adj = numpy.median(distances)
            Opp = distances[2]    

            
            '''Add the influence of aspect here'''
            
            
            aspect = AspectSector(ViewPoint_XYZ[0], ViewPoint_XYZ[1], Cell_Props[0], Cell_Props[1])
            RelativeAspect = Cell_Props[3] - aspect
                
                
            passcheck = 0
            '''Only conduct analysis if slope is facing (witihin 180 degrees) of viewpoint'''
            if -90.0 <= RelativeAspect <= 90.0:
                passcheck =1
            else:
                if Cell_Props[2] <= 5.0: #Ignores cells if they are not facing within 180 degress of viewer and have a slope above 5 degrees. i.e. flat slopes 'facing' the wrong way will still be included in analysis.
                    passcheck = 1
                else:
                        
                    aspectcount+=1 

            if passcheck == 1:

                try:
                    degrees = ViewAngle(Adj, Opp, Hyp)
                    runningtotal += degrees
                    
                    if Cell_Props[2] >= 5.0:
                        AdjustedDegrees = (float(degrees) * (1-(abs(RelativeAspect/90.0))))
                    else:
                        AdjustedDegrees = float(degrees)

                    runningtotal2 += AdjustedDegrees
                    successcount +=1
                        
                    if 0 <= Adj <= 300:
                        CloseCells =+1                            
                        CloseCellsSlope.append(Cell_Props[2])

                    elif 300.1 <= Adj <= 3000:
                        MidCells +=1
                        MidCellsSlope.append(Cell_Props[2])
                    elif 1000.1 <= Adj <= 6000:
                        FarCells +=1
                        FarCellsSlope.append(Cell_Props[2])
                    else:
                        DistCells +=1
                        DistCellsSlope.append(Cell_Props[2])                               
                
                except:
                    'ValueError: math domain error'
                    count +=1
                        
 
        else:
                
            AngleCount +=1
    
    row = [Viewpoint.FID, runningtotal, runningtotal2, count, str(environment), aspectcount, AngleCount, successcount, str(CloseCells), numpy.mean(CloseCellsSlope), str(MidCells), numpy.mean(MidCellsSlope), str(FarCells), numpy.mean(FarCellsSlope), str(DistCells), numpy.mean(DistCellsSlope), str(ViewPoint_XY[0]), str(ViewPoint_XY[1])] # Numbers that are written    
    writer.writerow(row)
    print('x')
    #arcpy.Delete_management("C:\\Users\\lowriech\\Documents\\ArcGIS\\curPoint_A.shp") 
    #arcpy.Delete_management("D:\\Bluespace\\curPoint.shp")
writer.close()