# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 12:55:16 2017

@author: rdk10
"""
#import pandas as pd
#import numpy as np
#import Functions as f
import sitchensis.ScanFunctions as sf
import sitchensis.ImportFunctions as impF
#import pdb
#########################################

######## This will be a routine that calls on functions fromt he ScanFunctions file #####################

###########################################
###Improvements############################
###########################################

#Check for correct column label names, including distType, and dist to ref on midsegment segments
#1) are the appropriate column headers there?
    #base ref type, top ref type especially. 
    
#2) Do midsegment appendages have refs and distances?, if not output a warning that states they will be assumed to come from the midpoint

#Check for proper references, make sure they exist and are in right height range. 

#Check for base diamters that are more than 2 times larger than top diameters

#Check for ref type for all rows. 
#Check for matching references in midsegments with name of nodes in segment name.

#Open a text file to print error screening and error log to

#Check data types of all columns********

########Inputs  ##################

def screenData(treeData, mapType, custRefs, outPath, treeName):
    
    #treeData, custRefs, mapType = impF.importExcelTree(treeName)
    treeName = outPath + '/' + treeName
    
    #Open a text file to print error screening and error log to
    lf = open('{0}_ErrorScan.txt'.format(treeName),'w') #open a file for writing ('w') to, lf for log file
    lf.write('##################################################\n')
    lf.write('############## Basic Error Checking ##############\n')
    lf.write('##################################################\n')
    lf.close()
    
    ####################################
    #####  Trunks  #####################
    ####################################
    
    #Scan for necessary column headers
    sf.trunkScan(treeData, treeName)
    
    #######################################
    ######  Segments  #####################
    #######################################
    if mapType == 'segment map' or mapType == 'full map':
        #Scan for necessary column headers
        treeData = sf.segScan(treeData, treeName)
            
    #######################################
    ######  Branches  #####################
    #######################################
    if mapType == 'trunk and branch map' or mapType == 'full map':
        #Scan for necessary column headers
        treeData = sf.brScan(treeData, treeName)
    
    ##################################
    ####  Custom references  #########
    ##################################
    
    if len(custRefs) > 0:
        custRefs = sf.custRefScan(custRefs, treeName)
        
    ##################################
    ####  Note column changes   ######
    ##################################
    
    treeData, noteColChanges = impF.renameNotesCol(treeData, treeName)
        
    
    lf = open('{0}_ErrorScan.txt'.format(treeName),'a') #open a file for writing ('w') to, lf for log file
    lf.write('\n\n############################################################\n')
    lf.write('############## Basic Error Checking Complete  ##############\n')
    lf.write('############################################################\n')
    lf.close()
    return(treeData, noteColChanges)