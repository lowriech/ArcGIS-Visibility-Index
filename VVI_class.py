import arcpy
import numpy
import csv
import math
import ViewPoint


class Visibility_Measure:
#Measures the total viewing angle
    def __init__(self, CellValues, CV_Z, CV_Slope, CV_Aspect, CV_XY, FileName, ViewPoints, Viewpoint_Z, Viewshed_Folder, scratchspace, output):
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
        headings = ['ViewPoint_ID', 'RawTotal']
        outfile = open(output, 'wb')
        writer = csv.writer(outfile, delimiter = ',', quotechar = '"')
        writer.writerow(headings)
        
        VPs = arcpy.SearchCursor(self.ViewPoints)
        for VP in VPs:
            ID, total = self.main(VP)
            row = [ID, total]
            writer.writerow(row)

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
        pts = [(x_topR, y_topR, z_top), (x_topL, y_topL, z_top), (x_bottomL, y_bottomL, z_bottom), (x_bottomR, y_bottomR, z_bottom)] 
        #return self.getPlane(pts, X, Y, Z, cell_res)
        #self.getPlane(pts, X, Y, Z, cell_res)
        #a, b, c, d = self.getPlane(pts, X, Y, Z, cell_res) 
        #(d - a*x - b*y)/c
        #if abs(d) > 1000:
        #    try:
        #        x_R = x + cel_res/2.0
        #        x_L = x - cel_res/2.0
        #        y_T = y + cel_res/2.0
        #        y_B = y - cel_res/2.0
        #        pts = [(x_R, y_T, (d - a*x_R - b*y_T)/c), (x_L, y_T, (d - a*x_L - b*y_T)/c), (x_L, y_B, (d - a*x_L - b*y_B)/c), (x_R, y_B, (d - a*x_R - b*y_B)/c)]
        #    except:
        #        ZeroDivisionError
        return pts

    def getSphericalCoordinates(self, pts, VP):
        spherical_coords = []
        for pt in pts:
            angle = math.atan(abs((VP[1]-pt[1])/(VP[0]-pt[0])))
            if pt[0] > VP[0]:
                if pt[1] > VP[1]: #1st Quadrant
                    Horiz = angle
                else: #4th Quadrant
                    Horiz = 2*math.pi - angle
            else:
                if pt[1] > VP[1]: #2nd Quadrant
                    Horiz = math.pi - angle
                else: #3rd Quadrant
                    Horiz = math.pi + angle
            #vertical angle

            Adj = math.hypot(VP[0]-pt[0], VP[1]-pt[1])
            Opp = (pt[2] - VP[2])
            Vert = math.atan(Opp/Adj)
            spherical_coords.append([math.degrees(Horiz), math.degrees(Vert)])
        return spherical_coords

    def getArea(self, pts):
        #2A = (x1y2 - x2y1) + (x2y3 - x3y2) + (x3y4 - x4y3) + (x4y1 - x1y4)
        #Area of a quadrilateral on a sphere
        A = ((pts[0][0]*pts[1][1] - pts[1][0]*pts[0][1]) + (pts[1][0]*pts[2][1] - pts[2][0]*pts[1][1]) + (pts[2][0]*pts[3][1] - pts[3][0]*pts[2][1]) + (pts[3][0]*pts[0][1] - pts[0][0]*pts[3][1]))/2
        return abs(A)

    #TODO: Add a function to print visible values to a csv
    #For future visualization
    def printCellsForVisual(self, output):
        for VP in self.ViewPoint_list:
            output2 = output[0:-4]+ '_' +str(VP.FID) + '.csv'
            outfile = open(output2, 'wb')
            writer = csv.writer(outfile, delimiter = ',', quotechar = '"')
            for i in VP.visibleCells:
                writer.writerow(i)

    def getVisiblePoints(self, VP):
        visible_pts = self.scratchspace + "\\vis_pts_" + str(VP.FID) + ".shp"
        arcpy.AddMessage(VP.viewshed)
        arcpy.AddMessage(visible_pts)
        arcpy.Clip_analysis (self.CellValues, VP.viewshed, visible_pts)
        arcpy.AddMessage("Successfully clipped FID {}".format(str(VP.FID)))
        return visible_pts

    def getPlane(self, pts, x, y, z, cell_res):
        #Create a plane given three points
        p1 = numpy.array(pts[0])
        p2 = numpy.array(pts[1])
        p3 = numpy.array(pts[2])

        # These two vectors are in the plane
        v1 = p3 - p1
        v2 = p2 - p1

        # the cross product is a vector normal to the plane
        cp = numpy.cross(v1, v2)
        a, b, c = cp

        # This evaluates a * x3 + b * y3 + c * z3 which equals d
        #(d - a*x - b*y)/c
        d = numpy.dot(cp, p3)
        return a,b,c,d


    def printPoints(self, output):
        headings = ['ViewPoint_ID', 'RawTotal']
        outfile = open(output, 'wb')
        writer = csv.writer(outfile, delimiter = ',', quotechar = '"')
        writer.writerow(headings)
        for VP in self.ViewPoint_list:
            row = [str(VP.FID), VP.total]
            writer.writerow(row)

    def main(self, Viewpoint):
        #Create a viewpoint
        VP = ViewPoint.ViewPoint(Viewpoint.getValue("ThisID"), Viewpoint.POINT_X, Viewpoint.POINT_Y, Viewpoint.getValue(self.Viewpoint_Z), self.Viewshed_Folder)
        #TODO: Add a field tying the VPs to the viewsheds
        #This should actually be done in the viewshed model, adding a path to the VP file
        ViewPoint_XYZ = [VP.x, VP.y, VP.z] 
        #Get visible pts
        vis_pts = self.getVisiblePoints(VP)
        visible_pts_cursor = arcpy.SearchCursor(vis_pts)
        #calculate corner locations
        corners = map(self.getAdjustedCorners, visible_pts_cursor)
        #convert to spherical relative to VP
        spherical_coords = map(self.getSphericalCoordinates, corners, [ViewPoint_XYZ]*len(corners))
        #VP.setVisibleCells(spherical_coords)
        #calculate areas
        areas = map(self.getArea, spherical_coords)
        #sum for the VP
        total = numpy.sum(areas)
        VP.setTotal(total)
        self.ViewPoint_list.append(VP)
        arcpy.AddMessage("Successfully measured FID {}".format(str(VP.FID)))
        arcpy.AddMessage("FID {}: Visibility score: {}".format(str(VP.FID),str(total)))
        arcpy.Delete_management(vis_pts)
        arcpy.Delete_management(visible_pts_cursor)
        arcpy.Delete_management(spherical_coords)
        return VP.FID, total

         # Numbers that are written    
        
        
