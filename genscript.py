import HFSS as hfss
import numpy as np
import Helper as hp
#import initGlobal as init
import geopandas as gpd
from shapely.geometry import Polygon
import geopandas.geoseries as geose
import math


def genscript(Substrate,polygons,centroid,tmpScriptFile,outFile,hfssFile,poly_list,poly_list_type, i, gen):
	import initGlobal as init 
	anten =  init.AnT()
	sub = init.Sub()
	# this function create the vbs file.
	# input arguments:
	#			- Substrate: the list of edges of the substrate.
	#			- polygons: the list of all coordinates to help draw the patch. Got from the second output of
	#							Helper.get_all_para_for_hfss() function.

	if init.Re_trainning:
		import update_state as us
		anten = init.AnT()
		sub = init.Sub()
		L   = init.L()
		U   = init.U()
		low = init.lowlevel()
		GP = init.GP()
		us.update_all_saved_parameters(anten, sub, L, U, GP, low)

	addition_number = sub.addition # increase the range of substrate.
	# frequency 
	c = anten.c
	fC = anten.fC
	fStart = anten.fStart
	fStop  = anten.fStop
	npoints = anten.npoints
	Lambda = (c/fC)*1000

	# radiation boundaries.
	#AirX = Nx*dAnt + Lambda/2
	#AirY = Ny*dAnt + Lambda/2
	AirZ = Lambda + Substrate[2] + 5 # 5 is the length of the coaxial cable.
	
	# solution parameters (GHz)
	
	radius = sub.radius
	list_point = [(0,radius*math.sqrt(3)/2), (radius/2, 0), (radius/2 + radius, 0), (radius*2, radius*math.sqrt(3)/2), (radius/2 + radius\
	, radius*math.sqrt(3)), (radius/2, radius*math.sqrt(3))]
	Center = [radius, radius*math.sqrt(3)/2, -Substrate[2]]
	Start = [0, radius*math.sqrt(3)/2, -Substrate[2]]

	polys = gpd.GeoSeries(Polygon(list_point))
	polygon_checking = gpd.GeoDataFrame({'geometry': polys})
	# df.plot()

	list_discard = [] # search for any sub_polygon that is outside of substrate layer.
	for i in range(len(polygons)):
		temp_check = False
		for ii in range(len(polygons[i])):
			temp_point = geose.Point(polygons[i][ii][0] ,polygons[i][ii][1])
			if not polygon_checking.intersects(temp_point)[0]:
				temp_check = True
		if temp_check:
			list_discard.append(i)

	#print(list_discard)



	########### checking whether exist any sub_polygon that is outside of substrate.
	#for i_check in range(polygons):





	# define some attributes of substrate.
	startX = centroid[0] - ((Substrate[0]+addition_number)/2) # the X original coordinate helps to draw the substrate.
	startY = centroid[1] - ((Substrate[1]+addition_number)/2) # the Y original coordinate helps to draw the substrate.
	length_W = Substrate[0] + addition_number # imply that it is the width_ox
	length_L = Substrate[1] + addition_number # imply that it is the length_oy
	centroidX_substrate = startX + length_W/2 # is the ox centroid coordinate of the substrate.
	centroidY_substrate = startY + length_L/2 # is the oy centroid coordinate of the substrate.
	####
	x_coaxial_cable_coordinate = Center[0]
	y_coaxial_cable_coordinate = Center[1]
	coaxial_check = geose.Point(x_coaxial_cable_coordinate,y_coaxial_cable_coordinate)
	checking = 0
	for i in range(len(polygons)):
		if poly_list[i].intersects(coaxial_check)[0]:
			checking = checking + 1

	if (checking == 0):
		if poly_list_type[0] == 'L1'  or poly_list_type[0] == 'L4' or poly_list_type[0] == 'U2' or poly_list_type[0] == 'U4':
			x_coaxial_cable_coordinate = (polygons[0][0,0] + polygons[0][2,0])/2
			y_coaxial_cable_coordinate = (polygons[0][0,1] + polygons[0][2,1])/2
		elif poly_list_type[0] == 'L2':
			x_coaxial_cable_coordinate = (polygons[0][5,0] + polygons[0][1,0])/2
			y_coaxial_cable_coordinate = (polygons[0][5,1] + polygons[0][1,1])/2
		elif poly_list_type[0] == 'U1' or poly_list_type[0] == 'L3':
			x_coaxial_cable_coordinate = (polygons[0][1,0] + polygons[0][3,0])/2
			y_coaxial_cable_coordinate = (polygons[0][1,1] + polygons[0][3,1])/2
		elif poly_list_type[0] == 'U3':
			x_coaxial_cable_coordinate = (polygons[0][7,0] + polygons[0][1,0])/2
			y_coaxial_cable_coordinate = (polygons[0][7,1] + polygons[0][1,1])/2

	if len(poly_list_type) > 1:
		x_shorting_pin = 0
		y_shorting_pin = 0 
		if poly_list_type[1] == 'L1' or poly_list_type[1] == 'L3' or poly_list_type[1] == 'L4' or poly_list_type[1] == 'U2' or poly_list_type[1] == 'U4':
			x_shorting_pin = (polygons[1][0,0] + polygons[1][2,0])/2
			y_shorting_pin = (polygons[1][0,1] + polygons[1][2,1])/2
		elif poly_list_type[1] == 'L2':
			x_shorting_pin = (polygons[1][5,0] + polygons[1][1,0])/2
			y_shorting_pin = (polygons[1][5,1] + polygons[1][1,1])/2
		elif poly_list_type[1] == 'U1':
			x_shorting_pin = (polygons[1][1,0] + polygons[1][3,0])/2
			y_shorting_pin = (polygons[1][1,1] + polygons[1][3,1])/2
		elif poly_list_type[1] == 'U3':
			x_shorting_pin = (polygons[1][7,0] + polygons[1][1,0])/2
			y_shorting_pin = (polygons[1][7,1] + polygons[1][1,1])/2

	if len(poly_list_type) > 2:
		x_shorting_pin_2 = 0
		y_shorting_pin_2 = 0 
		if poly_list_type[2] == 'L1' or poly_list_type[2] == 'L3' or poly_list_type[2] == 'L4' or poly_list_type[2] == 'U2' or poly_list_type[2] == 'U4':
			x_shorting_pin_2 = (polygons[2][0,0] + polygons[1][2,0])/2
			y_shorting_pin_2 = (polygons[2][0,1] + polygons[1][2,1])/2
		elif poly_list_type[2] == 'L2':
			x_shorting_pin_2 = (polygons[2][5,0] + polygons[1][1,0])/2
			y_shorting_pin_2 = (polygons[2][5,1] + polygons[1][1,1])/2
		elif poly_list_type[2] == 'U1':
			x_shorting_pin_2 = (polygons[2][1,0] + polygons[1][3,0])/2
			y_shorting_pin_2 = (polygons[2][1,1] + polygons[1][3,1])/2
		elif poly_list_type[2] == 'U3':
			x_shorting_pin_2 = (polygons[2][7,0] + polygons[1][1,0])/2
			y_shorting_pin_2 = (polygons[2][7,1] + polygons[1][1,1])/2



	'''
	#### check wheather the feed point is in range of patch.
	polygon_boundary = hp.getBoundary(polygons) # get the boundary of the patch.
	try:
		range_edges = hp.get2_suitable_edges_for_coaxial_cable(polygon_boundary,(centroidX_substrate,centroidY_substrate))
	except:
		pass

	#print(x_coaxial_cable_coordinate)
	#print(range_edges[1][1][1])
	
	# fix the coaxial point. 
	if range_edges != []:
		if len(range_edges) == 2:
			if (x_coaxial_cable_coordinate > range_edges[1][1][0]):
				# NOTE: this needs to revise because it does not include all of the case.
				#print(outFile)
				#print('__________')
				#x_coaxial_cable_coordinate = x_coaxial_cable_coordinate - (x_coaxial_cable_coordinate - range_edges[1][1][1]) - 2
				x_coaxial_cable_coordinate = (range_edges[1][1][0] - range_edges[0][1][0])/2
		else:
			if (x_coaxial_cable_coordinate > range_edges[-1][1][0]) or (x_coaxial_cable_coordinate > range_edges[-3][1][0] and x_coaxial_cable_coordinate < range_edges[-2][1][0]):
				x_coaxial_cable_coordinate = (range_edges[-1][1][0] - range_edges[-2][1][0])/2
	'''
	# open a temporary script file.
	# tmpScriptFile = 'tempPatch.vbs'
	fid = open(tmpScriptFile, 'w')


	# create a new HFSS project.
	hfss.hfssNewProject(fid)
	hfss.hfssInsertDesign(fid, 'NxN_uStrip_Patch'+str(i)+str(gen))
	
	# Create substrate.
	# hfss.hfssBox(fid, 'Substrate', [startX , startY , 0], [length_W, length_L, -Substrate[2]], 'mm')
	hfss.hfssCreateRegularPolyhedron(fid, 'Substrate', Center, Start, Substrate[2], 6, 'Z', 'mm')


	hfss.hfssAssignMaterial(fid,'Substrate',anten.substrate_material)
	name_all_polys = [] # to save all valid polygon name.
	first_i = [False,1] # to save the first valid polygon.
	for i in range(len(polygons)):
		# draw each polygon.
		if i not in list_discard:
			if not first_i[0]:
				first_i[0] = True
				first_i[1] = i + 1
			hfss.hfssPolyline1(fid,'polygon'+str(i+1),polygons[i],'mm')
			name_all_polys.append('polygon' + str(i+1))

	if len(name_all_polys) != 1:
		hfss.hfssUnite(fid,name_all_polys)
	hfss.hfssRename(fid,'polygon'+str(first_i[1]),'patch') 
	hfss.hfssAssignPE(fid, 'Perf1', ['patch'], False)
	# draw a ground plane.
	hfss.hfssCreateRegularPolygon(fid, 'GroundPlane', Center, Start, 6, 'Z', 'mm')
	#hfss.hfssAssignPE(fid, 'GND', ['GroundPlane']);


	# if len(poly_list_type)>1:
	# 	hfss.hfssCylinder(fid, 'shortingpin', 'Z', [x_shorting_pin, y_shorting_pin,\
	# 	-Substrate[2]], 0.3, Substrate[2], 'mm')
	# 	hfss.hfssAssignMaterial(fid,'shortingpin','copper')
	# if len(poly_list_type)>2:
	# 	hfss.hfssCylinder(fid, 'shortingpin_2', 'Z', [x_shorting_pin_2, y_shorting_pin_2,\
	# 	-Substrate[2]], 0.3, Substrate[2], 'mm')
	# 	hfss.hfssAssignMaterial(fid,'shortingpin_2','copper')

	# get the suitable coordinate of the coaxial cable.
	
	# draw the coaxial cable.
	hfss.hfssCircle(fid, 'Groundcir', 'Z', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate, -Substrate[2]], 1, 'mm')
	hfss.hfssSubtract(fid,['GroundPlane'],['Groundcir'])
	hfss.hfssAssignPE(fid, 'GND', ['GroundPlane'],False);

	hfss.hfssCylinder(fid, 'Cyl1', 'Z', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate,\
	 -Substrate[2]], 0.3, Substrate[2], 'mm')
	hfss.hfssAssignMaterial(fid,'Cyl1','copper')
	hfss.hfssCoaxialCable(fid, ['Cyl1_In', 'Cyl1_Er','Cyl1_Out'], 'Z', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate,\
	 -Substrate[2]-5], [0.3, 0.7, 1], 5, 'mm')
	hfss.hfssAssignMaterial(fid,'Cyl1_In','copper')
	hfss.hfssAssignMaterial(fid,'Cyl1_Er','air')
	hfss.hfssAssignMaterial(fid,'Cyl1_Out','copper')

	# feed.
	hfss.hfssCircle(fid,'feed','Z',[x_coaxial_cable_coordinate, y_coaxial_cable_coordinate, -Substrate[2]-5],0.7,'mm')
	
	hfss.hfssAssignLumpedPort(fid, 'Port1','feed', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate+0.7,\
	 -Substrate[2]-5], [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate+0.3, -Substrate[2]-5], 'mm')

	# draw radiation boundaries.
	hfss.hfssBox(fid, 'AirBox', [startX - Lambda/4, startY - Lambda/4, -5 - Lambda/2 - Substrate[2]], [length_W + Lambda/2,\
	 length_L + Lambda/2, AirZ], 'mm'); 
	hfss.hfssAssignRadiation(fid, 'ABC', 'AirBox');
	hfss.hfssSetTransparency(fid, ['AirBox'], 0.95);

	############################ insert solution.
	hfss.hfssInsertSolution(fid, 'Solution1', fC/1e9)
	hfss.hfssInterpolatingSweep(fid, 'Sweep1', 'Solution1',fStart, fStop, npoints)

	# Create return loss report (new HFSS-API)
	hfss.hfssCreateReport1(fid,'ReturnLoss',1,1,'Solution1',\
	    ['Freq'],['Freq','db(S(Port1,Port1))'],'Sweep1','NULL','Sweep')
	    # Save the project to a temporary file and solve it.
	
	#hfss.hfssSolveSetup(fid, 'Solution1');
	
	#Export the S11 report to .tab file

	# solve. 
	hfss.hfssSolveSetup(fid, 'Solution1')
	#hfss.hfssSaveProject(fid, hfssFile, anten.hfss_save);
	hfss.hfssExportToFile(fid, 'ReturnLoss', outFile, 'tab')

	fid.close()
'''
if __name__ == '__main__':
	x = [24.814, 24.0252, 1.1262]
	y = [np.array([[ 5.0874975 ,  6.48009658,  0.        ],[10.4336975 ,  6.48009658,  0.        ]\
	,[10.4336975 , 12.90749658,  0.        ],[15.8314975 , 12.90749658,  0.        ],\
	[15.8314975 , 19.57639658,  0.        ],[ 5.0874975 , 19.57639658,  0.        ],[ 5.0874975 ,  6.48009658,  0.        ]])]
	z = [10.4594975, 13.028246584999998]
	testgen(x,y,z)'''


def genscript_short_pin(Substrate,polygons,centroid,tmpScriptFile,outFile,hfssFile,poly_list,poly_list_type, shortting_pin):
	import initGlobal as init 
	anten =  init.AnT()
	sub = init.Sub()
	# this function create the vbs file.
	# input arguments:
	#			- Substrate: the list of edges of the substrate.
	#			- polygons: the list of all coordinates to help draw the patch. Got from the second output of
	#							Helper.get_all_para_for_hfss() function.

	if init.Re_trainning:
		import update_state as us 
		anten = init.AnT()
		sub = init.Sub()
		L   = init.L()
		U   = init.U()
		low = init.lowlevel()
		GP = init.GP()
		us.update_all_saved_parameters(anten, sub, L, U, GP, low)

	addition_number = sub.addition # increase the range of substrate.
	# frequency 
	c = anten.c
	fC = anten.fC
	fStart = anten.fStart
	fStop  = anten.fStop
	npoints = anten.npoints
	Lambda = (c/fC)*1000

	# radiation boundaries.
	#AirX = Nx*dAnt + Lambda/2
	#AirY = Ny*dAnt + Lambda/2
	AirZ = Lambda + Substrate[2] + 5 # 5 is the length of the coaxial cable.
	
	# solution parameters (GHz)
	

	# define some attributes of substrate.
	startX = centroid[0] - ((Substrate[0]+addition_number)/2) # the X original coordinate helps to draw the substrate.
	startY = centroid[1] - ((Substrate[1]+addition_number)/2) # the Y original coordinate helps to draw the substrate.
	length_W = Substrate[0] + addition_number # imply that it is the width_ox
	length_L = Substrate[1] + addition_number # imply that it is the length_oy
	centroidX_substrate = startX + length_W/2 # is the ox centroid coordinate of the substrate.
	centroidY_substrate = startY + length_L/2 # is the oy centroid coordinate of the substrate.
	####
	x_coaxial_cable_coordinate = centroidX_substrate + (length_W/2)/3.5
	y_coaxial_cable_coordinate = centroidY_substrate
	coaxial_check = geose.Point(x_coaxial_cable_coordinate,y_coaxial_cable_coordinate)
	checking = 0
	for i in range(len(polygons)):
		if poly_list[i].intersects(coaxial_check)[0]:
			checking = checking + 1

	if (checking == 0):
		if poly_list_type[0] == 'L1' or poly_list_type[0] == 'L3' or poly_list_type[0] == 'L4' or poly_list_type[0] == 'U2' or poly_list_type[0] == 'U4':
			x_coaxial_cable_coordinate = (polygons[0][0,0] + polygons[0][2,0])/2
			y_coaxial_cable_coordinate = (polygons[0][0,1] + polygons[0][2,1])/2
		elif poly_list_type[0] == 'L2':
			x_coaxial_cable_coordinate = (polygons[0][5,0] + polygons[0][1,0])/2
			y_coaxial_cable_coordinate = (polygons[0][5,1] + polygons[0][1,1])/2
		elif poly_list_type[0] == 'U1':
			x_coaxial_cable_coordinate = (polygons[0][1,0] + polygons[0][3,0])/2
			y_coaxial_cable_coordinate = (polygons[0][1,1] + polygons[0][3,1])/2
		elif poly_list_type[0] == 'U3':
			x_coaxial_cable_coordinate = (polygons[0][7,0] + polygons[0][1,0])/2
			y_coaxial_cable_coordinate = (polygons[0][7,1] + polygons[0][1,1])/2

	
	# open a temporary script file.
	# tmpScriptFile = 'tempPatch.vbs'
	fid = open(tmpScriptFile, 'w')


	# create a new HFSS project.
	hfss.hfssNewProject(fid)
	hfss.hfssInsertDesign(fid, 'NxN_uStrip_Patch')
	
	# Create substrate.
	hfss.hfssBox(fid, 'Substrate', [startX , startY , 0], [length_W, length_L, -Substrate[2]], 'mm')
	hfss.hfssAssignMaterial(fid,'Substrate',anten.substrate_material)
	name_all_polys = [] 
	for i in range(len(polygons)):
		# draw each polygon.
		hfss.hfssPolyline1(fid,'polygon'+str(i+1),polygons[i],'mm')
		name_all_polys.append('polygon' + str(i+1))
	if len(name_all_polys) != 1:
		hfss.hfssUnite(fid,name_all_polys)
	hfss.hfssRename(fid,'polygon1','patch') 
	hfss.hfssAssignPE(fid, 'Perf1', ['patch'], False)
	# draw a ground plane.
	hfss.hfssRectangle(fid, 'GroundPlane', 'Z', [startX,startY,-Substrate[2]], Substrate[0] + addition_number, Substrate[1]\
	 + addition_number, 'mm');
	#hfss.hfssAssignPE(fid, 'GND', ['GroundPlane']);


	hfss.hfssCylinder(fid, 'shortingpin', 'Z', [shortting_pin[0], shortting_pin[1],\
	-Substrate[2]], 0.3, Substrate[2], 'mm')
	hfss.hfssAssignMaterial(fid,'shortingpin','copper')
	# if len(poly_list_type)>2:
	# 	hfss.hfssCylinder(fid, 'shortingpin_2', 'Z', [x_shorting_pin_2, y_shorting_pin_2,\
	# 	-Substrate[2]], 0.3, Substrate[2], 'mm')
	# 	hfss.hfssAssignMaterial(fid,'shortingpin_2','copper')

	# get the suitable coordinate of the coaxial cable.
	
	# draw the coaxial cable.
	hfss.hfssCircle(fid, 'Groundcir', 'Z', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate, -Substrate[2]], 1, 'mm')
	hfss.hfssSubtract(fid,['GroundPlane'],['Groundcir'])
	hfss.hfssAssignPE(fid, 'GND', ['GroundPlane'],False);

	hfss.hfssCylinder(fid, 'Cyl1', 'Z', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate,\
	 -Substrate[2]], 0.3, Substrate[2], 'mm')
	hfss.hfssAssignMaterial(fid,'Cyl1','copper')
	hfss.hfssCoaxialCable(fid, ['Cyl1_In', 'Cyl1_Er','Cyl1_Out'], 'Z', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate,\
	 -Substrate[2]-5], [0.3, 0.7, 1], 5, 'mm')
	hfss.hfssAssignMaterial(fid,'Cyl1_In','copper')
	hfss.hfssAssignMaterial(fid,'Cyl1_Er','air')
	hfss.hfssAssignMaterial(fid,'Cyl1_Out','copper')

	# feed.
	hfss.hfssCircle(fid,'feed','Z',[x_coaxial_cable_coordinate, y_coaxial_cable_coordinate, -Substrate[2]-5],0.7,'mm')
	
	hfss.hfssAssignLumpedPort(fid, 'Port1','feed', [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate+0.7,\
	 -Substrate[2]-5], [x_coaxial_cable_coordinate, y_coaxial_cable_coordinate+0.3, -Substrate[2]-5], 'mm')

	# draw radiation boundaries.
	hfss.hfssBox(fid, 'AirBox', [startX - Lambda/4, startY - Lambda/4, -5 - Lambda/2 - Substrate[2]], [length_W + Lambda/2,\
	 length_L + Lambda/2, AirZ], 'mm'); 
	hfss.hfssAssignRadiation(fid, 'ABC', 'AirBox');
	hfss.hfssSetTransparency(fid, ['AirBox'], 0.95);

	############################ insert solution.
	hfss.hfssInsertSolution(fid, 'Solution1', fC/1e9)
	hfss.hfssInterpolatingSweep(fid, 'Sweep1', 'Solution1',fStart, fStop, npoints)

	# Create return loss report (new HFSS-API)
	hfss.hfssCreateReport1(fid,'ReturnLoss',1,1,'Solution1',\
	    ['Freq'],['Freq','db(S(Port1,Port1))'],'Sweep1','NULL','Sweep')
	    # Save the project to a temporary file and solve it.
	
	#hfss.hfssSolveSetup(fid, 'Solution1');
	
	#Export the S11 report to .tab file

	# solve. 
	hfss.hfssSolveSetup(fid, 'Solution1')
	#hfss.hfssSaveProject(fid, hfssFile, anten.hfss_save);
	hfss.hfssExportToFile(fid, 'ReturnLoss', outFile, 'tab')

	fid.close()

def Find_feed_point(Substrate,polygons,centroid,poly_list,poly_list_type):
	import initGlobal as init 
	anten =  init.AnT()
	sub = init.Sub()
	# this function create the vbs file.
	# input arguments:
	#			- Substrate: the list of edges of the substrate.
	#			- polygons: the list of all coordinates to help draw the patch. Got from the second output of
	#							Helper.get_all_para_for_hfss() function.

	if init.Re_trainning:
		import update_state as us 
		anten = init.AnT()
		sub = init.Sub()
		L   = init.L()
		U   = init.U()
		low = init.lowlevel()
		GP = init.GP()
		us.update_all_saved_parameters(anten, sub, L, U, GP, low)

	addition_number = sub.addition # increase the range of substrate.
	# frequency 
	c = anten.c
	fC = anten.fC
	fStart = anten.fStart
	fStop  = anten.fStop
	npoints = anten.npoints
	Lambda = (c/fC)*1000

	# radiation boundaries.
	#AirX = Nx*dAnt + Lambda/2
	#AirY = Ny*dAnt + Lambda/2
	AirZ = Lambda + Substrate[2] + 5 # 5 is the length of the coaxial cable.
	
	# solution parameters (GHz)
	

	# define some attributes of substrate.
	startX = centroid[0] - ((Substrate[0]+addition_number)/2) # the X original coordinate helps to draw the substrate.
	startY = centroid[1] - ((Substrate[1]+addition_number)/2) # the Y original coordinate helps to draw the substrate.
	length_W = Substrate[0] + addition_number # imply that it is the width_ox
	length_L = Substrate[1] + addition_number # imply that it is the length_oy
	centroidX_substrate = startX + length_W/2 # is the ox centroid coordinate of the substrate.
	centroidY_substrate = startY + length_L/2 # is the oy centroid coordinate of the substrate.
	####
	x_coaxial_cable_coordinate = centroidX_substrate + (length_W/2)/3.5
	y_coaxial_cable_coordinate = centroidY_substrate
	coaxial_check = geose.Point(x_coaxial_cable_coordinate,y_coaxial_cable_coordinate)
	checking = 0
	for i in range(len(polygons)):
		if poly_list[i].intersects(coaxial_check)[0]:
			checking = checking + 1

	if (checking == 0):
		if poly_list_type[0] == 'L1' or poly_list_type[0] == 'L3' or poly_list_type[0] == 'L4' or poly_list_type[0] == 'U2' or poly_list_type[0] == 'U4':
			x_coaxial_cable_coordinate = (polygons[0][0,0] + polygons[0][2,0])/2
			y_coaxial_cable_coordinate = (polygons[0][0,1] + polygons[0][2,1])/2
		elif poly_list_type[0] == 'L2':
			x_coaxial_cable_coordinate = (polygons[0][5,0] + polygons[0][1,0])/2
			y_coaxial_cable_coordinate = (polygons[0][5,1] + polygons[0][1,1])/2
		elif poly_list_type[0] == 'U1':
			x_coaxial_cable_coordinate = (polygons[0][1,0] + polygons[0][3,0])/2
			y_coaxial_cable_coordinate = (polygons[0][1,1] + polygons[0][3,1])/2
		elif poly_list_type[0] == 'U3':
			x_coaxial_cable_coordinate = (polygons[0][7,0] + polygons[0][1,0])/2
			y_coaxial_cable_coordinate = (polygons[0][7,1] + polygons[0][1,1])/2


	return (x_coaxial_cable_coordinate, y_coaxial_cable_coordinate)
