# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 13:59:52 2017
@author: rdk10
"""

import os
import ImportFunctions as impF   #Not functional yet
import TreeCalcs as tc
import vPythonFunctions as pf
import ErrorScan as es
import vpython as vp
import tkinter as tk
from tkinter.filedialog import askopenfilename
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt

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
suppressScatter = False
intFiles = False #Do you want to output intermediate calculation files??
runErrorScan = True
initErCheck = True

##############     IMPOROVEMENTS        ###########################################

#!!!!!!!!!!!!Check datatypes of all columns !!!!!!!!#####
#Move outlier error scan to another a function in scan functions, move appropriate import statements
#is is possible to move the plotting code to the plot functions?? I'm not sure....
#In the error scan add a catch for min segments segments not referenced to parent segment, or issue a warning and use parent segment

#Error scan should check for input types and coerce them to what I need, let user know if it can't because of differente data types in data. Also need to check for missing values in cols where they are needed
#Add in conditionals that don't run the rest of the script if there are scanning errors.
    #This could prompt the user to save and restart program instead of breaking the programming. 
#There are some miskeys that are hard to track down due to this.
#Run basic error checking and ask user to continue or not
#I need to deal with burls using a partial ellipsoid
#make this handle .xlsm files too
#User inputs names they want to use, these are then mapped to the names I've hard coded in and then remapped back at the end. This obviates the need to check for a notes column and have the specificrenameNotes function in the importFunctions functuion

#Linear interp on Azimuths needs to figure out how to deal with 360 = 0 problem. Ex interp between 358 and 4 degrees gives 270 something, it need to give something around 2, perhaps is more then 180 degrees off convert larger number to number-360 then add 360 at end if less than zero. 

#don't send error if there is raduis but not diameter
#don't send error if there is top z and base z instead of top ht and base ht
#If there is a midsegment appendage from a limb and with a  base height, decide whether to use the height or the distance and ref to node.
#This program is inflexible if the reference to ground is anything but 'G'.
#Make tree creation faster (try making a frustum class and cloning it instead of using compound objects)
#Organize files into one folder for git hub and delete camputer-specific code.
#Smooth out frusta
#stop program breaks for errors, make it continue and export all it can.
# put shperes in the junctions
#import full file name including extension so I can import .xlsm files.
#Make plotting a seperate routine outside of this script to pare down on code in the mainBodyScript
#popup box to select outputs
#dialog boxwes that ask for user input need to be in a function within the importFunctions script. It should output the chosen directory and file.
#Right now I will bump up agains a webGl limitation on the number of vertices if there are more than ~600 branches in a single tree. This can be fixed by making a list of compounded branhces, each that is no longer than 300. The code currently breaks it into two, I'd need to make it break the branches into batches of 300 and the remainder.

#I need a re-run the last tree command!!!

""" Make sure this can run on any computer, you will need to ask for a list of filenames or something of the sort """
"""Ask user to specify column names they want to use in file, you will also need to have all the needed packages in one place"""
""" make an _init_.py file and a setup.py file that load needed modules if they are not already present"""


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

def keyInput(evt):  #To improve this I need to determine a calculation vector and move scene center relative to that not to absolute x and y
    global cent, shift
    if evt.key == 'up':
        if cent < 100:
            cent = cent + 5
        vsl.value = cent
    elif evt.key == 'down':
        if cent > 0:
            cent = cent - 5
        vsl.value = cent
    elif evt.key == 'left':
        shift = shift + 2
    elif evt.key == 'right':
        shift = shift - 2
        
scene.bind('keydown', keyInput)
    
#Setup widgets (vert and horizontal slider, menue, and radio button). Different widgets are bound to functions in vPythonFunctions.py
vsl = vp.slider(pos = scene.title_anchor, vertical = True,length = 800, bind=vertSlide, value = 50, right = 5, top = 5, min = 0, max = 100)
scene.caption = "Vary the rotation speed:\n"
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
        scene.center = vp.vec(0,shift,cent)
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