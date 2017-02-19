import pygame
import sys
import numpy
import csv
import time

 
# Define some colors

x_stretch = 5
y_stretch = 4
size = (360*x_stretch,180*y_stretch)
pygame.init()
screen = pygame.display.set_mode(size)

pygame.display.set_caption("VVI")
# Loop until the user clicks the close button.
done = False
GREEN = (34, 139, 34)
BLACK = (0,0,0)
BLUE = (173, 216, 230)
done = False
clock = pygame.time.Clock()
screen.fill(BLUE)

inPolygons = open('Out_2191.csv', 'r')
reader = csv.reader(inPolygons, delimiter = ',', quotechar = '"')
to_draw = []

for row in reader:
	polygon = []
	for i in row:
		i = i.replace('[', '').replace(']','').replace(' ', '').split(',')
		j = [round(x_stretch*float(i[0]),0), round(y_stretch*float(i[1]), 0)]
		polygon.append([j[0], -(j[1])+180*y_stretch/2])

	if polygon[0][0] > 5 and polygon[1][0] > 5 and polygon[2][0] > 5 and polygon[3][0] > 5 and polygon[0][0] < 360*x_stretch-5 and polygon[1][0] < 360*x_stretch-5 and polygon[2][0] < 360*x_stretch-5 and polygon[3][0] < 360*x_stretch-5:
		to_draw.append(polygon)



while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True


	for i in to_draw:
		pygame.draw.polygon(screen, GREEN, i)
		#pygame.draw.polygon(screen, BLACK, i, 1)


	pygame.display.flip()
	print('printed')







