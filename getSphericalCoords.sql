CREATE FUNCTION getSphericalCoordinates(VP double precision ARRAY[3], pt1 double precision ARRAY[3], pt2 double precision ARRAY[3], pt3 double precision ARRAY[3], pt4 double precision ARRAY[3])
/*
theta = atan((VP[2]-pt[2])/(VP[1]-pt[1]))
Adj = sqrt((VP[1]-pt[1])^2.0 + (VP[2]-pt[2])^2.0)
Opp = (pt[3] - VP[3])
phi = atan(Opp/Adj)
phi = atan((pt[3] - VP[3])/sqrt((VP[1]-pt[1])^2.0 + (VP[2]-pt[2])^2.0))
*/
AS $$ SELECT 
ARRAY[atan((VP[2]-pt1[2])/(VP[1]-pt1[1])), atan((pt1[3] - VP[3])/sqrt((VP[1]-pt1[1])^2.0 + (VP[2]-pt1[2])^2.0))],
ARRAY[atan((VP[2]-pt2[2])/(VP[1]-pt2[1])), atan((pt2[3] - VP[3])/sqrt((VP[1]-pt2[1])^2.0 + (VP[2]-pt2[2])^2.0))],
ARRAY[atan((VP[2]-pt3[2])/(VP[1]-pt3[1])), atan((pt3[3] - VP[3])/sqrt((VP[1]-pt3[1])^2.0 + (VP[2]-pt3[2])^2.0))],
ARRAY[atan((VP[2]-pt4[2])/(VP[1]-pt4[1])), atan((pt4[3] - VP[3])/sqrt((VP[1]-pt4[1])^2.0 + (VP[2]-pt4[2])^2.0))]
$$
LANGUAGE SQL;