# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 12:55:16 2017

@author: rdk10
"""
import pandas as pd
import numpy as np
import Functions as f
#import ScanFunctions as sf

treeName = 'HohT2'
logFile = '{0}_ErrorScan.txt'.format(treeName)


#Open a text file to print error screening and error log to
lf = open('{0}_ErrorScan.txt'.format(treeName),'w') #open a file for writing ('w') to, lf for log file
lf.write('##################################################\n')
lf.write('############## Basic Error Checking ##############\n')
lf.write('##################################################\n')
lf.close()

#Check for correct column label names, including distType, and dist to ref on midsegment segments
#1) are the appropriate column headers there?
    #base ref type, top ref type especially. 
    
#2) Do midsegment appendages have refs and distances?, if not output a warning that states they will be assumed to come from the midpoint

#Check for proper references, make sure they exist and are in right height range. 

#Check for base diamters that are more than 2 times larger than top diameters

#Check for ref type for all rows.
 
#Check for matching references in midsegments with name of nodes in segment name.

#Correct for declination, Assumes there is a declination tab in each excel file. 

#Open a text file to print error screening and error log to


#############  Functions below #############################################

def importExcelTree(fileName):
    """This section assumed one excel file per tree with a tabe for each type of measurements (trunk, segment, or branch)"""
    
    #Import data all at once
    treeData = pd.read_excel("{0}.xlsx".format(fileName), sheetname = None) #,converters={'name':str,'ref':str, 'referenceType':str})
    
    #list of dictionary keys
    keys = [key for key in treeData]
    
    #The key for each tab
    trunkKey = keys[[i for i, key in enumerate(keys) if 'trunk' in key.lower()][0]]
    segKey = keys[[i for i, key in enumerate(keys) if 'seg' in key.lower()][0]]
    brKey = keys[[i for i, key in enumerate(keys) if 'branch' in key.lower()][0]]
    
    #Assign cust refs to dataFrame
    if len([i for i, key in enumerate(keys) if 'cust' in key.lower()])>0:
        custKey = keys[[i for i, key in enumerate(keys) if 'cust' in key.lower()][0]]
        custRefs = pd.read_excel("{0}.xlsx".format(fileName), sheetname = custKey ,converters={'name':str})
        custRefs.columns = [x.lower() for x in custRefs.columns]
        custRefs = f.calcCustRefs(custRefs)
    else:
        custRefs = []
    
    #Assign declination to variable
    if len([i for i, key in enumerate(keys) if 'declin' in key.lower()])>0:
        declinKey = keys[[i for i, key in enumerate(keys) if 'declin' in key.lower()][0]]
        declinRefs = pd.read_excel("{0}.xlsx".format(fileName), sheetname = custKey ,converters={'name':str})
        declinRefs.columns = [x.lower() for x in declinRefs.columns]
        declination = declinRefs['declination'].iloc[0] #extract number
        declination = declination.item() # convert to python float from numpy.float64
    else:
        declination = 0.00
    
    #This tests for types of data present
    trunkBool = any(['trunk' in t.lower() for t in treeData])
    segBool = any(['segment' in t.lower() for t in treeData] )
    branchBool = any(['branch' in t.lower() for t in treeData] )
    
    #Saves the data if it exists and makes changes to columns so they work in the program
    if trunkBool:
        trunkDat = pd.read_excel("{0}.xlsx".format(fileName), sheetname = trunkKey, converters={'name':str,'ref':str})#, 'ref type':str})
        trunkDat.columns = [x.lower() for x in trunkDat.columns] 
        trunkDat['name'] = trunkDat['name'].str.upper()
        trunkDat['azi'] = trunkDat['azi'] + declination
    
    if segBool:
        segs = pd.read_excel("{0}.xlsx".format(fileName),parse_dates = False, sheetname = segKey, converters={'name':str,'base ref':str, 'top ref':str,'midsegment ref':str})
        segs.columns = [x.lower() for x in segs.columns]
        segs['base z'] = segs['base ht']
        segs[ 'top z'] = segs['top ht']
        segs['base azi'] = segs['base azi'] + declination
        segs['top azi'] = segs['top azi'] + declination
    
    if branchBool:
        branches = pd.read_excel("{0}.xlsx".format(fileName),parse_dates = False , sheetname = brKey, converters={'name':str,'base ref':str, 'top ref':str,'midsegment ref':str})
        branches.columns = [x.lower() for x in branches.columns]
        branches['base z'] = branches['base ht']
        branches['top z'] = branches['top ht']
        branches['orig azi'] = branches['orig azi'] + declination
        branches['cent azi'] = branches['cent azi'] + declination
                
    if trunkBool == True:
        if segBool == False and branchBool == False:
            mapType = 'trunk map'
            treeData = {'trunk':trunkDat}
        elif segBool == True and branchBool == False: #There are trunks only
            mapType = 'segement map'
            treeData = {'trunk':trunkDat, 'segments':segs}    
        elif segBool == False and branchBool == True:
            mapType = 'trunk and branch map'
            treeData = {'trunk':trunkDat, 'branches':branches}
        elif segBool == True and branchBool == True:
            mapType = 'full map'
            treeData = {'trunk':trunkDat, 'segments':segs, 'branches': branches}    
    else:
        print('There were not trunk data specified')
    return(treeData, custRefs,  mapType)


####################################
#####  Trunks  #####################
####################################

#trunkDat = pd.read_excel("HohT2MainRaw.xlsx",converters={'name':str,'ref':str, 'referenceType':str})
#trunkDat.columns = [x.lower() for x in trunkDat.columns]
#trunkDat.dtypes
#trunkDat['name'] = trunkDat['name'].str.upper()
#
#Make this a function and apply to all datasets
#def isRadiusCalced(trunkDat):
#    testDiam = 'diam' in trunkDat.columns
#    testRadius = 'radius' in trunkDat.columns
#    if any([testDiam,testRadius]):
#        #There is at least one needed column
#        if testDiam and testRadius == False:
#            if all(np.isnan(trunkDat['radius'])):
#                trunkDat['radius'] = trunkDat['diam']/200  #converts form cm to m
#        #elif testRadius and testDiam == False:
#            elif all(np.isnan(trunkDat['diam'])):              
#                trunkDat['diam'] = trunkDat['radius'] * 200 #converts from m to cm
#            return(trunkDat)
#    else:
        f.print2Log(logFile, 'There must be at least a diameter or radius column for trunks')
#
#
#trunkCols = trunkDat.columns.str.lower()
#testTrunkCols = np.array(['name','height','diam', 'radius', 'dist', 'azi', 'ref', 'ref type'])
#sf.colTest(trunkCols, testTrunkCols, "trunk")
#
#######################################
######  Segments  #####################
#######################################
#
#segCols = segs.columns.str.lower()
#testSegCols = np.array(['names','base ht','base diam', 'base radius', 'base dist', 'base azi', 'base ref', 'base ref type',
#                        'top ht','top diam','top dist', 'top azi', 'top ref','top ref type', 'midsegment dist','midsegment ref'])
#sf.colTest(segCols, testSegCols, "segment")
#        
#######################################
######  Branches  #####################
#######################################
#
#
#brCols = branches.columns.str.lower()
#testBrCols = np.array(['name','origin','base ht','base diam', 'base radius', 'orig azi', 'cent azi', 'top diam', 'hd','slope','vd', 'midsegment dist', 'midsegment ref']) 
#sf.colTest(brCols, testBrCols, "branch")  
#
#
#
#
#br = pd.read_excel("HohT2branches.xlsx",converters={'name':str,'base ref':str, 'top ref':str,'midsegment ref':str})
#br.columns = [x.lower() for x in br.columns]
#br['base z'] = branches['base ht']
#br['top z'] = branches['top ht']
#
#br.loc[1:3,['slope','vd','top ht']] = None
#
##Test to make sure there is enough info to calculate top heights of branches
#test = ~np.isnan(br[['slope','vd','top ht']])
#test = test.sum(axis = 1)
#if any(test == 0):
#    missingIndex = test[test==0].index
#    if len(missingIndex) == 1:
#        missingNames = br.loc[missingIndex,'name'].iloc[0]
#        f.print2Log(logFile,'Branch "{0}" is missing slope, vertical distance, and top height so it\'s top Z cannot be calculated'.format(missingNames))
#    else:
#        missingNames = br.loc[missingIndex,'name'].values
#        f.print2Log(logFile,'Branches {0} are missing slope, vertical distance, and top height so their top Z\'s cannot be calculated'.format(missingNames))
#




