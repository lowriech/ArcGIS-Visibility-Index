CREATE FUNCTION corners(X double precision,Y double precision, Z double precision, slope double precision, aspect double precision, cell_res double precision) RETURNS TABLE(topR double precision ARRAY[3], topL double precision ARRAY[3], bottomL double precision ARRAY[3], bottomR double precision ARRAY[3])
/*      
	X + |/(cell_res*cell_res/2.0)*cos(pi()/180*(45-aspect)) //x_topR
        Y + |/(cell_res*cell_res/2.0)*cos(pi()/180*(45-aspect)) //y_topR
        X + |/(cell_res*cell_res/2.0)*cos(pi()/180*(135-aspect)) //x_topL
        Y + |/(cell_res*cell_res/2.0)*cos(pi()/180*(135-aspect)) //y_topL
        X + |/(cell_res*cell_res/2.0)*cos(pi()/180*(225-aspect)) //x_bottomL
        Y + |/(cell_res*cell_res/2.0)*cos(pi()/180*(225-aspect)) //y_bottomL
        X + |/(cell_res*cell_res/2.0)*cos(pi()/180*(315-aspect)) //x_bottomR
        Y + |/(cell_res*cell_res/2.0)*cos(pi()/180*(315-aspect)) //y_bottomR
        Z + cell_res/2.0*tan(pi()/180*(slope)) //z_top
        Z - cell_res/2.0*tan(pi()/180*(slope)) //z_bottom
pts = [(x_topR, y_topR, z_top), (x_topL, y_topL, z_top), (x_bottomL, y_bottomL, z_bottom), (x_bottomR, y_bottomR, z_bottom)] 
*/
AS $$ SELECT 
ARRAY[$1 + |/($6*$6/2.0)*cos(pi()/180*(45-$5)),$2 + |/($6*$6/2.0)*cos(pi()/180*(45-$5)),$3 + $6/2.0*tan(pi()/180*($4))],
ARRAY[$1 + |/($6*$6/2.0)*cos(pi()/180*(135-$5)),$2 + |/($6*$6/2.0)*cos(pi()/180*(135-$5)),$3 + $6/2.0*tan(pi()/180*($4))],
ARRAY[$1 + |/($6*$6/2.0)*cos(pi()/180*(225-$5)),$2 + |/($6*$6/2.0)*cos(pi()/180*(225-$5)),$3 - $6/2.0*tan(pi()/180*($4))],
ARRAY[$1 + |/($6*$6/2.0)*cos(pi()/180*(315-$5)),$2 + |/($6*$6/2.0)*cos(pi()/180*(315-$5)),$3 - $6/2.0*tan(pi()/180*($4))]
$$
LANGUAGE SQL;
