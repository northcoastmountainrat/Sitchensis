# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 14:21:24 2017

@author: rdk10
"""
import numpy as np
import Functions as f
import pandas as pd

import pdb

def colTest(colNames, testColNames, dataType, treeName):
    
    logFileName = '{0}_ErrorScan.txt'.format(treeName)
    colTest = np.array([col in colNames for col in testColNames], dtype = bool)
            
    if any(colTest == False):
        if sum(colTest == False) == 1:
            textout = "The mandatory column '{0}' was not found in the {1} input data".format(testColNames[colTest==False][0],dataType)
            print(textout)
            f.print2Log(logFileName,textout)
        else:
            textout = 'The mandatory columns {0} were not found in the {1} input data'.format(testColNames[colTest==False],dataType)
            print(textout)
            f.print2Log(logFileName, textout)
    else:
        textout = 'All the mandatory columns are present to calculate {0} values'.format(dataType)
        print(textout)
        f.print2Log(logFileName, textout)

def trunkScan(treeData, treeName):
    
    logFileName = '{0}_ErrorScan.txt'.format(treeName)
    
    lf = open(logFileName,'a') #open a file for writing ('w') to, lf for log file
    lf.write('\n############## Trunks  ##############\n')
    lf.close()
    
    trunkDat = treeData['trunk']
    trunkDat.columns = [x.lower() for x in trunkDat.columns]
    #trunkDat.dtypes
    trunkDat['name'] = trunkDat['name'].str.upper()
    
    #Make this a function and apply to all datasets
    testDiam = 'diam' in trunkDat.columns
    testRadius = 'radius' in trunkDat.columns
    if any([testDiam,testRadius]):
        #There is at least one needed column
        if testDiam == True and any(np.isnan(trunkDat['radius'])):
            if testDiam:
                trunkDat['radius'] = trunkDat['diam']/200  #converts form m to cm
        elif testRadius == True and testDiam == False:
            if testRadius:              
                trunkDat['diam'] = trunkDat['radius'] * 200 #converts from cm to m
    else:
        f.print2Log(logFileName, 'There must be at least a diameter or radius column for trunks')

    trunkCols = trunkDat.columns.str.lower()
    testTrunkCols = np.array(['name','height','diam', 'radius', 'dist', 'azi', 'ref', 'ref type'])
    
    colTest(trunkCols, testTrunkCols, "trunk", treeName)

    if any(pd.isnull(trunkDat['ref'])):
        print('\nThere are missing references for the main trunk, these must be filled in prior to running the program.')
        f.print2Log(logFileName, '\nThere are missing references for the main trunk, these must be filled in prior to running the program.')

    treeData['trunk'] = trunkDat    
    return(treeData)             

def segScan(treeData, treeName):
    
    """Brings in a dictionary of data for trunks, segments, and brancehs """
    logFileName = '{0}_ErrorScan.txt'.format(treeName)
    
    lf = open(logFileName,'a') #open a file for writing ('w') to, lf for log file
    lf.write('\n\n############## Segments  ##############\n')
    lf.close()
    
    segs = treeData['segments']
    
    #Test for calculated radius from diameter (must have radius in meters!!!)
    testDiam = 'base diam' and 'top diam' in segs.columns
    testRadius = 'base radius' and 'top radius' in segs.columns
    if any([testDiam,testRadius]):
        #There is at least one needed column
        if any(np.isnan(segs['base radius'])) or any(np.isnan(segs['top radius'])):
            segs['base radius'] = segs['base diam']/200  #converts form cm to m
            segs['top radius'] = segs['top diam']/200  #converts form cm to m      
    else:
        f.print2Log(logFileName, 'There must be at least a diameter or radius column for segments')
    
    segCols = segs.columns.str.lower()
    testSegCols = np.array(['name','base ht','base diam', 'base radius', 'base dist', 'base azi', 'base ref', 'base ref type',
                        'top ht','top diam','top dist', 'top azi', 'top ref','top ref type', 'midsegment dist','midsegment ref'])
    
    colTest(segCols, testSegCols, "segment", treeName)
    treeData['segments'] = segs
    
    #test that base references to mid-segs are segment of origin not a node. 
    testSegs = segs[['-' in name for name in segs['base name']]]
    if any(testSegs['base name'] != testSegs['base ref']) and len(testSegs > 0):
        testSegs = testSegs[testSegs['base name'] != testSegs['base ref']]
        print('The mid-segment segment(s) {0} are referenced to something other than {1}, this may cause errors.'.format(testSegs['name'].values, testSegs['base name'].values))
        f.print2Log(logFileName, '\nThe mid-segment segment(s) {0} are referenced to something other than {1}, this may cause errors.'.format(testSegs['name'].values, testSegs['base name'].values))

    #send warning if there are references to Mtop
    if any([('M' in ref and 'top' in ref) for ref in segs['top ref']]):
        print('Warning: There are references to "Mtop," the highest row on the main trunk page will be used for the x,y locations of these segments')
        f.print2Log(logFileName, '\nWarning: There are references to "Mtop," the highest row on the main trunk page will be used for the x,y locations of these segments')
        
    return(treeData)

def brScan(treeData, treeName):
    
    logFileName = '{0}_ErrorScan.txt'.format(treeName)
    
    lf = open(logFileName,'a') #open a file for writing ('w') to, lf for log file
    lf.write('\n\n############## Branches  ##############\n')
    lf.close()
    
    branches = treeData['branches']
    brCols = branches.columns.str.lower()
    testBrCols = np.array(['name','origin','base ht','base diam', 'base radius', 'orig azi', 'cent azi', 'top diam', 'hd','slope','vd', 'midsegment dist', 'midsegment ref']) 
    
    if 'base z' not in branches.columns and 'base ht' in branches.columns:
        branches['base z'] = branches['base ht']
        treeData['branches'] = branches
     
    if 'top ht' not in branches.columns:
        branches['top ht'] = np.NaN
                
    #Test for calculated radius from diameter (must have radius in meters!!!)
    testDiam = 'base diam' and 'top diam' in branches.columns
    testRadius = 'base radius' and 'top radius' in branches.columns
    if any([testDiam,testRadius]):
        #There is at least one needed column
        if any(np.isnan(branches['base radius'])) or any(np.isnan(branches['top radius'])):
            branches['base radius'] = branches['base diam']/200  #converts form cm to m
            branches['top radius'] = branches['top diam']/200  #converts form cm to m      
    else:
        f.print2Log(logFileName, 'There must be at least a diameter or radius column for segments')
                
    colTest(brCols, testBrCols, "branch", treeName)
    
    return(treeData)

def custRefScan(custRefs, treeName):
    
    logFileName = '{0}_ErrorScan.txt'.format(treeName)
    
    lf = open(logFileName,'a') #open a file for writing ('w') to, lf for log file
    lf.write('\n\n############## Custom references  ##############\n')
    lf.close()
    
    refCols = custRefs.columns.str.lower()
    testRefCols = np.array(['name','diam','dist','azi','ref','ref diam','ref type', 'ref x', 'ref y']) 
    
    colTest(refCols, testRefCols, "custom reference", treeName)
    
    return(custRefs)
