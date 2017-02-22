import numpy
import arcpy

class ViewPoint:
	def __init__(self, FID, X, Y, Z, viewshed):
		self.FID = FID
		self.x = X
		self.y = Y
		self.z = Z + 2
		self.viewshed =  viewshed + "\\poly_" + str(FID) +".shp"
		arcpy.AddMessage('Viewshed from Viewpoints.py: {}'.format(self.viewshed))
		self.total = 0.0
		self.visibleCells = []

	def setVisibleCells(self, cells):
		self.visibleCells = cells

	def setTotal(self, number):
		self.total = number

