# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 13:59:52 2017
@author: rdk10
"""

import os
import tkinter as tk
from tkinter.filedialog import askopenfilename

import sitchensis.ImportFunctions as impF   #Not functional yet
import sitchensis.TreeCalcs as tc
import sitchensis.vPythonFunctions as pf
import sitchensis.ErrorScan as es
import vpython as vp


from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt


def main():
	###################################
	####   USER INPUTS   ##############
	###################################
	cwd = os.getcwd()
	root = tk.Tk()
	fullFileName = askopenfilename(initialdir=cwd, title="select a tree file to error check", filetypes=[("Excel", "*.xlsx")])        #Ask user to pick files
	root.withdraw()
	workingDir = os.path.dirname(fullFileName) #path to file
	fileName = fullFileName.rsplit('/')[-1] #Excludes path to file
	treeName = fileName.rsplit('.')[0] #For input file (excludes '.xlsx')

	#Output options
	suppressScatter = True
	intFiles = False #Do you want to output intermediate calculation files??
	runErrorScan = True
	initErCheck = True

	###################################
	#### Create output directory ######
	###################################

	if not os.path.exists(workingDir + '/StichensisOutputs'):
		os.makedirs(workingDir + '/StichensisOutputs')
	outPath =  workingDir + '/StichensisOutputs'

	#################################
	########  Import data ###########
	#################################

	treeData, custRefs, mapType = impF.importExcelTree(fullFileName)

	##########################################################################################
	############  Run Preliminary Error Scan #################################################
	##########################################################################################
	#if runErrorScan ==True:
	treeData, noteColChanges = es.screenData(treeData, mapType, custRefs, outPath, treeName)  #This scheck for basic naming errors and renames note columns so they will work in the script, the columns are reverted to old names later.

	#############################################################################
	############  Run tree calculations #########################################
	#############################################################################

	treeData = tc.calculateTree(treeData, custRefs, mapType, treeName, outDir=outPath, intermediateFiles=intFiles)

	##############################################################
	############ Outlier errorscan  ##############################
	##############################################################

	if suppressScatter == False:
		color_wheel = {1: "#00ff00",
					   2: "#000000"}
		if mapType == 'segment map' or mapType == 'full map':
			colors = treeData['segments']['% dead'].map(lambda x: color_wheel.get(1) if x < 89 else color_wheel.get(2))
			if len(treeData['segments']) > 1:
				scatter_matrix(treeData['segments'][['base z', 'base radius', 'top z', 'top radius']], figsize=(10,10), color=colors, alpha=0.5, diagonal='kde')
				plt.suptitle('segments\nblack is > 89% dead')
				plt.show()
			else:
				print('There is only one segment so no scatter matrix for segments was produced')

		colors = treeData['branches']['% dead'].map(lambda x: color_wheel.get(1) if x < 89 else color_wheel.get(2))
		if treeData['branches']['base z'].dtype == 'O': #if it is formatted as a string
			treeData['branches']['base z'] = treeData['branches']['base z'].astype(dtype = float)
		scatter_matrix(treeData['branches'][['base z', 'base radius', 'hd', 'slope']], figsize=(10,10), color=colors, alpha=0.5, diagonal='kde')
		plt.suptitle('branches\nblack is > 89% dead')
		plt.show()

	########################################################
	##########      Save data ##############################
	#########################################################

	treeData, noteColChanges = impF.renameNotesCol(treeData, treeName, newname=noteColChanges['oldNoteName'])

	#segs.name = segs.name.apply(repr)
	#branches.origin = branches.origin.apply(repr)
	#branches.to_csv("brFromNode.csv")

	#rename the notes columns back to their old name using the
	impF.excelExport(treeData, outPath, treeName)

	#############################################################################
	############ Run Plotting Routine ###########################################
	#############################################################################

	scene = vp.canvas(title='Tree: {0}'.format(treeName), width=800, height=800, center=vp.vec(0,0,50), background=vp.color.white, fov = 0.01, range = 60, forward = vp.vec(-1,0,0), up = vp.vec(0,0,1))
	scene.select()

	vp.distant_light(direction = vp.vec(1,1,0.5), color = vp.color.white)
	vp.distant_light(direction = vp.vec(-1,-1,0.5), color = vp.color.white)

	running = True #This allows widgets to dynamically update display (see bottom of code)
	cent = 40   #Set the default camera center
	shift = 0   #for moving around image
	speed = 0  #Set the default rotation speed for the tree
	mapChoice = 'full map'
		
	#Define what the widgets will do
	def vertSlide(c):  #This controls where the camera points
		global cent
		cent = c.value
	def setSpeed(s):  #This controls the rotation speen of the tree
		global speed
		speed = s.value
	def treeDisplay(m):  #This controls what parts of the tree are displayed
		global trunk, segments, branches, mapChoice, radBut, labelButton
		
		#clear labels if they are shown and set variable "labsChecked" to reset at end
		if radBut.checked == True:
			radBut.checked = False
			labelButton(radBut)
			labsChecked = True
		else:
			labsChecked = False
		
		if m.selected == 'trunk map':
			trunk.visible = True
			segments.visible = False
			for branch in branches:
				branch.visible = False
		elif m.selected == 'segment map':
			trunk.visible = True
			segments.visible = True
			for branch in branches:
				branch.visible = False
		elif m.selected == 'full map':
			trunk.visible = True
			#if there are segments plot them otherwise skip
			segments.visible = True
			for branch in branches:
				branch.visible = True
		#reset mapChoice, selects item in list and passes correct lebels to section below
		mapChoice = m.selected
		#reset labels if they were on previously
		if labsChecked == True:
			radBut.checked = True
			labelButton(radBut)


	def labelButton(r): #This controls whether or not to display labels
		global trunkLabs, segLabs,brLabs, mapChoice
		if r.checked == True:
			if mapChoice == 'trunk map':
				for label in trunkLabs:
					label.visible = True
				for label in segLabs:
					label.visible = False
				for label in brLabs:
					label.visible = False
			elif mapChoice == 'segment map':
				for label in trunkLabs:
					label.visible = False
				for label in segLabs:
					label.visible = True
				for label in brLabs:
					label.visible = False
			elif mapChoice == 'full map':
				for label in trunkLabs:
					label.visible = False
				for label in segLabs:
					label.visible = False
				for label in brLabs:
					label.visible = True
			   #I need conditions in here for trees without segments or without branches
		elif r.checked == False:
			for label in trunkLabs:
				label.visible = False
			for label in segLabs:
				label.visible = False
			for label in brLabs:
				label.visible = False
	   
	#Setup widgets (Horizontal slider, menu, and radio button). Different widgets are bound to functions in vPythonFunctions.py
	scene.caption = "\nVary the rotation speed:\n"
	hsl = vp.slider(pos = scene.caption_anchor, min = 0, max = 500, value = 0.001, length = 800, bind=setSpeed, right=15)
	scene.append_to_caption('\nSelect the tree map to display\n')     
	scene.append_to_caption('           ')

	#There needs to be a condition here to eliminate options if a tree has no segments or no branches
	if mapType == "trunk map":
		mapChoices = vp.menu(choices=['trunk map'], selected = 'trunk map',index = 0, bind=treeDisplay )
	elif mapType == "trunk and branch map":
		mapChoices = vp.menu(choices=['trunk map', 'full map'], selected = 'full map',index = 0, bind=treeDisplay )
	elif mapType == "trunk and segment map":
		mapChoices = vp.menu(choices=['trunk map', 'segment map'], selected = 'segment map',index = 0, bind=treeDisplay )
	elif mapType == "full map":
		mapChoices = vp.menu(choices=['trunk map', 'segment map', 'full map'], selected = 'full map', index = 0, bind=treeDisplay )
	scene.append_to_caption('                 ')              
	radBut = vp.radio(bind=labelButton, text='display labels') # text to right of button

	scene.append_to_caption('            Scroll to zoom, shift + left click to pan!\n')   

	###Maybe make a button that moves tree back to zero rotation.####

	colors = {'trunk':vp.color.black,'segments':vp.color.red,'branches':vp.color.green, 'dead':vp.color.gray(0.2)}
	#mapType = 'full map'

	#This is where we decide what to plot: I could add in an option here to not make visible those portions that are not initiall selected. 
	trnk, trunkLabs = pf.plotFrusta(treeData, 'trunk', colors) #trunkSpheres,, trunkLabs
	trunk = vp.compound(trnk, texture = vp.textures.wood_old, visible = True)

	if mapType == 'segment map' or mapType == 'full map':
		sgmnts, segLabs = pf.plotFrusta(treeData, 'segments', colors) #segSpheres,
		segments = vp.compound(sgmnts, visible = True)  #Take a look at the branches code below, I may have to do that for trees with more than 250 segments. 
	if mapType == 'trunk and branch map' or mapType == 'full map': 
		brnchs, brLabs = pf.plotFrusta(treeData, 'branches', colors) # brSpheres,     
		mid = round(len(brnchs)/2)
		end = len(brnchs)
		br1 = vp.compound(brnchs[0:mid], visible = True)   #I split up branches into two objects instead of one so they don't exceed the display limits of webGl. This require loops in the rotation and display sections of the code for branches to alter each object in the list. 
		br2 = vp.compound(brnchs[mid:end], visible = True)
		branches = [br1,br2]
		#branches = vp.compound(brnchs, visible = True)
		
	#Draw axes
	pf.axes((-5,-5,0))

	#This allows dynamic updating based on widgets
	while True:
		vp.rate(100)
		if running:
			trunk.rotate(angle=speed*1e-4, axis=vp.vec(0,0,1), origin=vp.vector(0,0,0)) 
			for tr in trunkLabs:
				tr.rotate(angle=speed*1e-4, axis=vp.vec(0,0,1), origin=vp.vector(0,0,0))
			if mapType == 'segment map' or mapType == 'full map':
				segments.rotate(angle=speed*1e-4, axis=vp.vec(0,0,1), origin=vp.vector(0,0,0))
				for seg in segLabs:
					seg.rotate(angle=speed*1e-4, axis=vp.vec(0,0,1), origin=vp.vector(0,0,0))
			if mapType == 'trunk and branch map' or mapType == 'full map': 
				for branch in branches:
					branch.rotate(angle=speed*1e-4, axis=vp.vec(0,0,1), origin=vp.vector(0,0,0))
				for br in brLabs:
					br.rotate(angle=speed*1e-4, axis=vp.vec(0,0,1), origin=vp.vector(0,0,0))
					
if __name__ == '__main__':
	main()