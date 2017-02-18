import arcpy
import numpy
import csv
import math
import ViewPoint


class Visibility_Measure:
#Measures the total viewing angle
    def __init__(self, CellValues, CV_Z, CV_Slope, CV_Aspect, CV_XY, FileName, ViewPoints, Viewpoint_Z, Viewshed_Folder, scratchspace):
        self.CellValues = CellValues
        self.CV_Z = CV_Z
        self.CV_Slope = CV_Slope
        self.CV_Aspect = CV_Aspect
        self.CV_XY = CV_XY
        self.FileName = FileName
        self.ViewPoints = ViewPoints
        self.Viewpoint_Z = Viewpoint_Z
        self.Viewshed_Folder = Viewshed_Folder
        self.scratchspace = scratchspace
        self.ViewPoint_list = []
        #1st Quadrant, for visualization
        self.Q1 = []
        VPs = arcpy.SearchCursor(self.ViewPoints)
        for VP in VPs:
            self.main(VP)

    def getAdjustedCorners(self, pt):
        #Returns the four corners of the cell
        X, Y, Z, aspect, slope = pt.POINT_X, pt.POINT_Y, pt.getValue(self.CV_Z), pt.getValue(self.CV_Aspect), pt.getValue(self.CV_Slope)
        cell_res = 5
        x_topR = X + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(45-aspect))
        y_topR = Y + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(45-aspect))
        x_topL = X + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(135-aspect))
        y_topL = Y + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(135-aspect))
        x_bottomL = X + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(225-aspect))
        y_bottomL = Y + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(225-aspect))
        x_bottomR = X + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(315-aspect))
        y_bottomR = Y + math.sqrt(cell_res*cell_res/2.0)*math.cos(math.radians(315-aspect))
        z_top = Z + cell_res/2.0*math.tan(math.radians(slope))
        z_bottom = Z - cell_res/2.0*math.tan(math.radians(slope))
        return [(x_topR, y_topR, z_top), (x_topL, y_topL, z_top), (x_bottomL, y_bottomL, z_bottom), (x_bottomR, y_bottomR, z_bottom)] 

    def getSphericalCoordinates(self, pts, VP):
        spherical_coords = []
        #Q1 stands for quadrant 1, it is for pending visualization
        Q1_pending = []
        for pt in pts:
            Horiz = math.atan((VP[1]-pt[1])/(VP[0]-pt[0]))
            #vertical angle
            Adj = math.hypot(VP[0]-pt[0], VP[1]-pt[1])
            Opp = (pt[2] - VP[2])
            Vert = math.atan(Opp/Adj)
            spherical_coords.append([math.degrees(Horiz), math.degrees(Vert)])
            Q1_pending.append([int(round(10*math.degrees(Horiz))), int(round(10*math.degrees(Vert)))])
        #if in first quadrant
        if (VP[0] < pts[0][0]) and (VP[1] < pts[0][1]):
            self.Q1.append(Q1_pending)
        return spherical_coords

    def getArea(self, pts):
        #2A = (x1y2 - x2y1) + (x2y3 - x3y2) + (x3y4 - x4y3) + (x4y1 - x1y4)
        #Area of a quadrilateral on a sphere
        A = ((pts[0][0]*pts[1][1] - pts[1][0]*pts[0][1]) + (pts[1][0]*pts[2][1] - pts[2][0]*pts[1][1]) + (pts[2][0]*pts[3][1] - pts[3][0]*pts[2][1]) + (pts[3][0]*pts[0][1] - pts[0][0]*pts[3][1]))/2
        return abs(A)

    #TODO: Add a function to print visible values to a csv
    #For future visualization
    def printCellsForVisual(self, VP, output):
        #take an output value for the csv
        #print each visible cell to its own row
        pass


    def getVisiblePoints(self, VP):
        visible_pts = self.scratchspace + "\\vis_pts_" + str(VP.FID) + ".shp"
        arcpy.Clip_analysis (self.CellValues, VP.viewshed, visible_pts)
        arcpy.AddMessage("Successfully clipped FID {}".format(str(VP.FID)))
        return arcpy.SearchCursor(visible_pts)

    def printPoints(self, output):
        headings = ['ViewPoint_ID', 'RawTotal']
        outfile = open(output, 'wb')
        writer = csv.writer(outfile, delimiter = ',', quotechar = '"')
        writer.writerow(headings)
        for VP in ViewPoint_list:
            row = [str(VP.FID), VP.total]
            writer.writerow(row)

    def main(self, Viewpoint):
        #Create a viewpoint
        VP = ViewPoint.ViewPoint(Viewpoint.FID, Viewpoint.POINT_X, Viewpoint.POINT_Y, Viewpoint.getValue(self.Viewpoint_Z), self.Viewshed_Folder)
        ViewPoint_XYZ = [VP.x, VP.y, VP.z] 
        #Get visible pts       
        visible_pts_cursor = self.getVisiblePoints(VP)
        #calculate corner locations
        corners = map(self.getAdjustedCorners, visible_pts_cursor)
        #convert to spherical relative to VP
        spherical_coords = map(self.getSphericalCoordinates, corners, [ViewPoint_XYZ]*len(corners))
        #calculate areas
        areas = map(self.getArea, spherical_coords)
        #sum for the VP
        total = numpy.sum(areas)
        VP.setTotal(total)
        self.ViewPoint_list.append(VP)
        VP.setVisibleCells(self.Q1)
        self.Q1 = []
        arcpy.AddMessage("Successfully measured FID {}".format(str(VP.FID)))

         # Numbers that are written    
        
        
