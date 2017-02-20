CREATE FUNCTION getArea(pt1 double precision ARRAY[3], pt2 double precision ARRAY[3], pt3 double precision ARRAY[3], pt4 double precision ARRAY[3]) RETURNS integer
AS $$ SELECT
abs((pt1[1]*pt2[2] - pt2[1]*pt1[2]) + (pt2[1]*pt3[2] - pt3[1]*pt2[2]) + (pt3[1]*pt4[2] - pt4[1]*pt3[2]) + (pt4[1]*pt1[2] - pt1[1]*pt4[2]))/2
$$
LANGUAGE SQL;