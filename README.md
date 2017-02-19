# ArcGIS-Visibility-Index
Designed to calculate the visibility of bluespace from a set of ViewPoints

Takes 9 inputs:

1) Terrain Point Values: the bluespace values we are interested in measuring.  They should have Z, Slope, and Aspect fields

2) Z Field

3) Slope Field

4) Aspect

5) Do the slopes already have XY coordinates (if not will be calculated)

6) Filename to output a csv of each VPs visibility

7) Viewpoints to analyze

8) Folder of precalculated viewsheds

9) A scratchspace for intermediate points - will be deprecated with on-the-fly deletes

10 - pending) Add cell resolution

For each point visible from a viewpoint:
- calculates the corner values of each cell in 3D space, using the cells Z, Slope, and Aspect.
- projects those points to a spherical coordinate system, relative to the viewpoint
- calculates the area on that coordinate system that the cell occupies*, aka the visibility
- It sums the cells, to calculate total visibility

*This means there is currently some distortion to account for, but this should be minimal since it is at the poles and most cells will be near the centerline.  

The tool outputs a csv of each FID with its total visibility.  

-- Graphics --
It also outputs csvs of the cells, relative to the viewer.  This can be used to visualize the location, see screenshots.  Currently this won't work on the remote lab computer since it requires a library called pygame.
