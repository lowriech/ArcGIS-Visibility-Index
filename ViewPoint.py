import numpy
import arcpy

class ViewPoint:

	def __init__(self, FID, X, Y, Z, viewshed):
		self.FID = FID
		self.x = X
		self.y = Y
		self.z = Z
		self.viewshed =  viewshed + "\\poly_" + str(FID) +".shp"
		self.total = 0.0
		self.visibleCells = []

	def setVisibleCells(self, list):
		self.visibleCells = list

	def setTotal(self, number):
		self.total = number

