# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:46:27 2017

@author: rdk10
"""

import numpy as np
import pandas as pd
#import Routines as rt
#import os, sys
import pdb  #for debugging

#os.chdir('C:/Users/rdk10/Desktop/ComputerProgramming/Python/TreeCalcs')           #use this to nav to where files are stored                         #This adds the directory of the CrownMapFunctions module to the search path
#sys.path.append('C:/Users/rdk10/Desktop/ComputerProgramming/Python/TreeCalcs')

def closingStatement(logFileName, error):
    if error:
        print2Log(logFileName, "\nThere were no more errors during this process")
    else:
        print2Log(logFileName, "There were no errors during this process")

def print2Log(logFile,text):
    lf=open(logFile, 'a')
    lf.write('\n{0}'.format(text))
    lf.close()

def splitName(nameSeries, delimiter = '-'):
    """returns indices base and top names from a pandas series as a series"""
    nameSeries = nameSeries.replace(' ','')
    dashIndex = nameSeries.str.rfind(delimiter) #reverse index finds last occurance of "-"
    topNames = pd.Series([None]*len(nameSeries),index = nameSeries.index, dtype = str)
    baseNames = pd.Series([None]*len(nameSeries),index = nameSeries.index, dtype = str)
    for i in range(len(nameSeries)):
        topNames.iloc[i] = nameSeries.iloc[i][dashIndex.iloc[i]+1:len(nameSeries.iloc[i])]
        baseNames.iloc[i] = nameSeries.iloc[i][:dashIndex.iloc[i]] 
                
    topNames.astype(str)
    baseNames.astype(str)
    
    out = {'topNames':topNames,'baseNames':baseNames}
        
    return(out)

def vectorBool(test1, test2, intType):
    """ input two boolean vectors retun on with intercetion"""
    if intType == 'or':
        test = [a or b for a, b in zip (test1,test2)]
    elif intType == 'and':
        test = [a and b for a, b in zip (test1,test2)]
    return(test)

#Interp x,y, and radius
def linearInterp(TrunkRow,targetHt, logFileName = None):
    basex = TrunkRow['base x']
    basey = TrunkRow['base y']
    basez = TrunkRow['base z']
    baser = TrunkRow['base radius']
    topx = TrunkRow['top x']
    topy = TrunkRow['top y']
    topz = TrunkRow['top z']
    topr = TrunkRow['top radius']

    if (topz-basez).iloc[0] == 0:
        print2Log(logFileName, 'The interpolation trunk {0} has the same base and top height yet is labelled as a trunk'.format(TrunkRow['name']))
    #interp x, y, r
    x = (targetHt-topz)*(basex-topx)/(basez-topz)+topx    
    y = (targetHt-topz)*(basey-topy)/(basez-topz)+topy
    r = (targetHt-topz)*(baser-topr)/(basez-topz)+topr
    

    #error output, catch if I passed in a dataframe versus a list
    if isinstance(basez,pd.Series) or isinstance(basez, np.float64): #convert numpy.floats to native floats, not sure why but several heights are imported as numpy.float not float

        if basez.shape == (0,):
            print('check the error log!!!')
        else:
            basez = basez.item()
            topz = topz.item()

    test = [basez,topz,targetHt]
    test.sort()
    if test[1]==targetHt: #Testing to see if taget ht is between or equal to base and top z
       er = False
       #store in a dictionary
       interps={'ref_X':x,'ref_Y':y,'ref_R':r,'errors':er}
    else:
        er = True
        interps = {'ref_X':np.nan,'ref_Y':np.nan,'ref_R':np.nan,'errors':er}
        
    return interps

def breakDataByName (trunkDat):
    mainTNames = trunkDat['name'].unique()
    mainTrunks = {}
    for name in mainTNames:
        mainTrunks['{0}'.format(name)] = trunkDat.query('name == "{0}"'.format(name))
        mainTrunks['{0}'.format(name)] = mainTrunks['{0}'.format(name)] .sort_values('height')
    return(mainTrunks)

def refSegType(refs, segNames, heights, segTypes, refType):
    """Inputs are a list vector of references, a vector of names, heights, and a vector of types"""
    """returns indices of reference segments of refType"""
    
    #strip white space from series
    for i in range(len(segNames)):
        refs.iat[i] = refs.iat[i].replace(' ','')    #This doesn't seem to give the warning. 
        segNames.iat[i] = segNames.iat[i].replace(' ','')
        
        #refs.set_value(i, refs.iloc[i].replace(' ',''))  #These give depreciation of set_value warning
        #segNames.set_value(i, segNames.iloc[i].replace(' ',''))
        
       # refs.loc[i] = refs.iloc[i].replace(' ','')    #These give a set value to slice warning
       # segNames.loc[i] = segNames.iloc[i].replace(' ','')

    segTypes = segTypes.str.lower()
    
    #If ref is to a segment and the matching segment names corresponds to a type "t" 
    refTest = refs.str.contains('-')
    heightTest = heights.map(np.isreal)  
    refs2Segs = refs[[a and b for a, b in zip(refTest, heightTest)]]  #The ref is to a segment and there is a height recoded for the element in question               
    calcVec = pd.Series([False]*len(refs2Segs), index = refs2Segs.index)
    
    #segments that are also trunks
    segNames = segNames[segTypes == refType]
    
    for i in range(len(refs2Segs)):
        ref2test = refs2Segs.iloc[i]
        if any(ref2test == segNames):
            calcVec.iloc[i] = True

    return(calcVec[calcVec == True].index)

#Calculate values based on reference position and measurements
def calcPosition(refVals, calcVals, calcType, error = False, refName = None): #pass a vector of reference locations and position measures 
#This will calculate the x,y,z postition of any location given either cylindrical or polar coordinates. It also takes in calcType,
# the type of calculation needed, options are 'trunk', 'segment', or 'branch'

#For segments and trunks refVals is a vector = [refX,refY, refRadius], for branches it = [refX,refY, refRadius, refZ] 
#For segments and trunks calcVals is a vectory = [dist, azimuth, target radius, refType], for branches it is [dist, azimuth, slope]     

#refType is how the reference was taken, (reference 2 tartet), either p2p, p2f, f2p, or f2f. p = pith, f = face

#All units in meters!!

    RefX = refVals[0]
    RefY = refVals[1]
    RefRadius = refVals [2] 

    dist = calcVals[0]
    azi = calcVals[1] 
    
    #Change the distance according to the reference style (p2p, etc....)                                                                     
    if calcType == 'trunk' or calcType == 'segment':
        targetRadius = calcVals[2]
        refType = calcVals[3]
        if refType == 'p2p':
            dist = dist
        elif refType == 'p2f':
            dist = dist + targetRadius
        elif refType == 'f2p':
            dist = dist + RefRadius
        elif refType == 'f2f':
            dist = dist + RefRadius + targetRadius
        else:
            dist = dist + RefRadius  #if nothing is given use face to pith
            error = True
            
        x = RefX + dist * np.sin(np.pi/180 * azi)
        y = RefY + dist * np.cos(np.pi/180 * azi)
        calcs = {'x':x,'y':y, 'error':error}                                    

    elif calcType == 'branchBase': #For branches
        RefZ = refVals[3]
        dist = RefRadius  # I input a distance of zero for all branch bases, so this will have to be just the reference radius
        
        x = RefX + dist * np.sin(np.pi/180 * azi)
        y = RefY + dist * np.cos(np.pi/180 * azi)
        z = RefZ
        calcs = {'x':x,'y':y,'z':z, 'error':error}
        
    elif calcType == 'branchTop': #For branches
        RefZ = refVals[3]
        #slope = calcVals[2]
        
        x = RefX + dist * np.sin(np.pi/180 * azi)
        y = RefY + dist * np.cos(np.pi/180 * azi)
        #z = RefZ + dist * np.tan(np.pi/180 * slope)

        calcs = {'x':x,'y':y,'error': error}    
    return (calcs)   

def calcCustRefs(custRefs):
    if len(custRefs) > 0:
        for i in range(len(custRefs['name'])):
            if custRefs['ref'][i] == 'G':
                refx = 0
                refy = 0
            else:
                refx = custRefs['ref x'][i]
                refy = custRefs['ref y'][i]
            refR = custRefs['ref diam'][i]/200.0 #convert to m from cm
            if refR > 3:  #units are likely in cm and need conversion to m
                refR = refR/100

            refType = custRefs['ref type'][i]
            azi = custRefs['azi'][i]
            dist = custRefs['dist'][i]
            radius = custRefs['diam'][i]/200.0
            if radius > 3:  #units are likely in cm and need conversion to m
               radius = radius/100
            refVals = [refx, refy, refR]
            calcVals = [dist, azi, radius, refType]
        
            calcs = calcPosition(refVals, calcVals, calcType = 'trunk', error = False)
            custRefs.loc[i,'x'] = calcs['x']
            custRefs.loc[i,'y'] = calcs['y']
            custRefs.loc[i,'radius'] = radius
    return(custRefs)

def midSegTopLocator(nodeRow, logFileName, error):
    """Brings in a series of segment rows with base and mid seg positions on the same segment for when there are supplemental measurements"""
    """Outputs the most distal row of the series of segments with the same name (many supplementals), a list of the indices in Proximal to distal order, and an errorcode"""
    prox2distIndices = []
    for i in range(len(nodeRow)):
        if i == 0:
            currentRow = nodeRow[nodeRow['position']=='base']
            if len(currentRow)==0:
                print('One of the segment {0} positions is not labelled "base"'.format(nodeRow['name'].iloc[0]))
                print2Log(logFileName,'One of the segment {0} positions is not labelled "base"'.format(nodeRow['name'].iloc[0]))
                error = True
            findHt = float(currentRow['top ht'])
            findDist = float(currentRow['top dist'])
            prox2distIndices.append(currentRow.index[0])
        else:
            sameHtAndDist = vectorBool(nodeRow['base ht']==findHt, nodeRow['base dist']==findDist,'and')
            currentRow = nodeRow[sameHtAndDist]
            if len(currentRow)==0:
                print('The top height of {0} or distance of {1} for a supplemental on segment "{2}" does not match the base height of another supplemental for this segment'.format(findHt,findDist, nodeRow['name'].iloc[0]))
                print2Log(logFileName,'The top height of {0} or distance of {1} for a supplemental on segment "{2}" does not match the base height of another supplemental for this segment'.format(findHt,findDist, nodeRow['name'].iloc[0]))
                error = True
            elif len(currentRow) > 1:
                print2Log(logFileName,'There are more than one supplemental rows sharing both both a height and distance along segment {0}'.format(nodeRow['name'].iloc[0]))
                error = True
            findHt = float(currentRow['top ht'])
            findDist = float(currentRow['top dist'])
            prox2distIndices.append(currentRow.index[0])
    return([currentRow, prox2distIndices, error])

def calcMidLoc(refSeg, dist2pt, ref4Dist2pt,appendageName, logFileName, azi = None, appendageType = "segment"):
    """Function takes in the segment of origin, if the segment has base and top info, then it calculates
    the interpolated x,y,z, and r for the segment origin, otherwise it prints an error stating that the reference 
    segment is not yet calculated
    
    It also handles the case where more than one row has the same origin segment name as happens with supplemental measurements
    the script uses the summulative lengh along the supplemental arc to find which row to reference to"""
    
    #INPUTS: 
    #refSegs - must be a dataframe, if slicing one row frame a dataframe for input be sure to use df.iloc[[0]] rather than df.iloc[0], the former = dataframe the latter = series so won't work
    #        - This is a dataframe with the reference segment or segments if there are multiple rows with the same name in the case of supplemental measurements
    #dist2pt - float, distance in meters from a node that the midsegment segment attaches to, distance can be None if None was recorded
    #ref4Dist2pt - This is the reference node for the location of mid-seg seg or midseg branch, input can be None if None was recorded
    #appendageName- pass in the name of the segment or *branch* for the printout commands
    #Azi - Include azi if you want to offset midsegment appendages by the radius of their origin segment
    #appendageType - defaults to segment, 
    """I need to make this more generic to handle branches as well, mostly this means changing the print commands to substitute "segment" for "branch" if that is what we are looking for"""
    
    refSeg = refSeg.loc[:,['name','position','base name','top name','base x', 'base y', 'base z','base ht','base dist', 'base radius', 'top x', 'top y', 'top z', 'top ht','top dist', 'top radius']]
    ref4Dist2pt = str(ref4Dist2pt)   #Not sure why but something keeps converting red4Dist2pt to an int from an str, so I'm coercing it back gaddammit
                              
    if refSeg.isnull().values.any():
        print2Log(logFileName, "There are missing values in the base or top of the reference segment {0}".format(refSeg['name'].iloc[0]))
    elif len(refSeg)>1: #This is if there are supplemental rows.
    
        #Reorder refSegs from proximal to distal if they are not already in this order, also reindex it
        midSegOuts = midSegTopLocator(refSeg, logFileName, error = False)
        refSeg = refSeg.loc[midSegOuts[1]]                             
        refSeg = refSeg.reset_index() 
            
        #These will be vectors
        bX = refSeg['base x']
        bY = refSeg['base y']
        bZ = refSeg['base z']
        bR = refSeg['base radius']
        tX = refSeg['top x']
        tY = refSeg['top y']
        tZ = refSeg['top z']
        tR = refSeg['top radius']
        l = ((bX-tX)**2+(bY-tY)**2+(bZ-tZ)**2)**0.5  #Length of each segment
        
        cumL = np.cumsum(l)                          #cummulative length from base to top of each supplemental
        revCumL = np.cumsum(l[::-1])                 #cummulative length from top to base of each supplemental
        totL = sum(l)
        
        #Extract base and top name
        baseName = refSeg['base name'].iloc[0]
        topName = refSeg['top name'].iloc[0]      
               
        if ref4Dist2pt == None or (ref4Dist2pt != topName and ref4Dist2pt != baseName):   
            ref4Dist2pt = topName
            dist2pt = 'mid'
            dist2pt = totL/2.0
            print("{0} {1} assumed to originate from middle of segment {2} because there was no reference node recorded or the recorded node is not from the origin segment".format(appendageType.capitalize(),appendageName,refSeg["name"].iloc[0]))
            print2Log(logFileName,"{0} {1} assumed to originate from middle of segment {2} because there was no reference node recorded or the recorded node is not from the origin segment".format(appendageType.capitalize(),appendageName,refSeg["name"].iloc[0]))
            
        if ref4Dist2pt == baseName:#referenced to the base            
            if dist2pt == 'mid' or dist2pt == None:
                dist2pt = totL/2.0  #This is for the case where not distance is given in notes. 
                print2Log(logFileName,"Warning: {0} {1} assumed to originate from middle of segment {2} because there was no recoded distance from a node".format(appendageType.capitalize(),appendageName,refSeg["name"].iloc[0]))
            
            testVec = float(dist2pt) <= cumL #[l for l in cumL]
#            if isinstance(testVec, np.ndarray):
#                pdb.set_trace()
#                testVec = testVec.tolist
            if all(testVec):    #if value is smaller than any of the cumL distances then the first supplemental row is the one we need
                refSeg = refSeg.iloc[[0],]  
                dist2pt = dist2pt
            elif all(testVec == False):
                refSeg = None
                dist2pt = None
                print2Log(logFileName,"The distance given for the {0} {1} is longer than the origin segment {2}".format(appendageType, appendageName, refSeg["name"].iloc[0]))  #This error need to be passed out of the funtion somehow, or input of segment name needs to be given
            elif any(testVec==False):  #There is at least one False meaning that all rows before this are smaller distances than the dist2pt
                ind = testVec[testVec==False].index[-1]+1 # locate the last False
                refSeg = refSeg.loc[[ind],]
                dist2pt = dist2pt - cumL[ind-1]   #cummulative distance to this cupplemental - distance from basal node
        elif ref4Dist2pt == topName:                #referenced to top or midsegment
            if dist2pt == 'mid' or dist2pt == None:
                dist2pt = totL/2.0  #This is for the case where not distance is given in notes. 
                print2Log(logFileName,"Warning: {0} {1} assumed to originate from middle of segment {2} because there was no recorded distance from a node".format(appendageType.capitalize(), appendageName,refSeg["name"].iloc[0])) 
                
            testVec = float(dist2pt) <= revCumL # [l for l in revCumL]
            
            if all(testVec):    #if value is smaller than any of the revCumL distances then the last supplemental row is the one we need
                refSeg = refSeg.iloc[[len(testVec)-1],]   
                dist2pt = dist2pt
            elif all(testVec == False):
                refSeg = None
                print("The distance given for the {0} {1} is longer than the origin segment {2}".format(appendageType, appendageName,refSeg["name"].iloc[0]))
                print2Log(logFileName,"The distance given for the {0} {1} is longer than the origin segment {2}".format(appendageType, appendageName,refSeg["name"].iloc[0]))
            elif any(testVec==False):  #There is at least one False meaning that all rows before this are smaller distances than the dist2pt
                ind = testVec[testVec==False].index[-1]-1 # locate the last False
                refSeg = refSeg.loc[[ind],]
                dist2pt = dist2pt - revCumL[ind+1]
            
    #This is if there is only one row with a matching origin for the base of the mid-seg seg. 
    bX = refSeg['base x']
    bY = refSeg['base y']
    bZ = refSeg['base z']
    bR = refSeg['base radius']
    tX = refSeg['top x']
    tY = refSeg['top y']
    tZ = refSeg['top z']
    tR = refSeg['top radius']
    
#    if float(tZ)-float(bZ) == 0:
#        print(refSeg)
        
     #Slpit name into refs
    baseName = refSeg['base name'].iloc[0]
    topName = refSeg['top name'].iloc[0]
     
    #calc hypotenuse
    hyp = ((tX-bX)**2+(tY-bY)**2+(tZ-bZ)**2)**0.5
    hyp = hyp.iloc[0]   #Extract just a number from the data.frame
     
    if str(dist2pt) == 'mid': #if we forgot to collect data on where segment originates
        dist2pt = hyp/2.0
        print2Log(logFileName,"Warning: {0} {1} assumed to originate from middle of segment {2} because there was no recoded distance from a node".format(appendageType.capitalize(),appendageName,refSeg["name"].iloc[0]))
    #calc distance along(if from top then hyp-dist, it from bottom, then dist)
    if ref4Dist2pt == baseName:  
        dist = dist2pt
    elif ref4Dist2pt == topName:
        dist = hyp - dist2pt
    else:
        dist = hyp/2.0
        print2Log(logFileName,"Warning: The reference name for the mid-segment {0} {1} does not match a base or top node of segment {2} or they are not of the same data type, so {0} {1} assumed to be from the middle of segment {2}".format(appendageType, appendageName, refSeg['name'].iloc[0]))
        
    #Find ratio
    ratio = dist/hyp
     
    #calculate x,y,z (diff in each *ratio)+base
    refX = bX + (tX-bX)*ratio
    refY = bY + (tY-bY)*ratio
    z = bZ + (tZ-bZ)*ratio
    
    if tZ.iloc[0] != bZ.iloc[0]:
        #Interpolate radius
        refR = (z-bZ)*(tR-bR)/(tZ-bZ) + bR
    else:           
        refR = (refX-bX)*(tR-bR)/(tX-bX) + bR  #using x here because a segment with the same base and top height will not interpolate b/c divide by zero problem
             
    #use top azi to offset location by radius, I'm not doing this b/c steve doesn't but I probably will once working on my own data
    x = refX  #refX+refR*np.sin(np.pi/180*azi)
    y = refY  #refY+refR*np.cos(np.pi/180*azi)
             
    #output final x,y,z
    out = {'ref_X':refX,'ref_Y':refY,'ref_R':refR,'X':x,'Y':y,'Z':z}        
    return(out)
        
def isnumber (dataframe):
    '''determins if either of two rows formatted as strings have a number value, return boolean vector. '''
    testTop = [None]*len(dataframe)
    testBase = [None]*len(dataframe)
    for i in range(len(dataframe)):
        if type(dataframe['base ref'].iloc[i]) == str:
            testBase[i] = dataframe['base ref'].iloc[i].isnumeric()
        elif type(dataframe['base ref'].iloc[i])==int:
            testBase[i]=True
        else:
            print("The base reference of row {0} was imported as something other than an int or a string by pandas".format(i))
        if type(dataframe['top ref'].iloc[i])==str:
            testTop[i] = dataframe['top ref'].iloc[i].isnumeric()
        elif type(dataframe['top ref'].iloc[i])==int:
            testTop[i]=True
        else:
            print("The top reference of row {0} was imported as something other than an int or a string by pandas".fprmat(i))
        
    dataframe['baseTest'] = testBase #append these as columns so I know which specific base or top rows do or do not need calcs
    dataframe['topTest'] = testTop
    calcSegs = dataframe[[a or b for a, b in zip(testBase, testTop)]] #intersection of boolean vectors is correct index  
     
    #Now we have segs reffed to nodes, this finds segs that still need calcs                    
    testBaseX = np.isnan(calcSegs['base x'])  #These assume that is the base or top x is calculated, so is the base and top y. 
    testTopX = np.isnan(calcSegs['top x']) 
    calcSegs = calcSegs[[a or b for a, b in zip(testBaseX, testTopX)]] #intersection of boolean vectors is correct index                 
                        
    return(calcSegs)
    
def topNameFromSegName (refFrame):
    '''parses the segment name and returns vector of the top node name for referencing'''
    supTopNames = [None]*len(refFrame)                    
    for i in range(len(refFrame['name'])):
        dashIndex = refFrame['name'].iloc[i].rindex('-')
        supTopNames[i] = refFrame['name'].iloc[i][dashIndex+1:len(refFrame['name'].iloc[i])]
    return(supTopNames)

def supOrNotRefs(findName, k, supTopNames, suppRefs, refSegs):
    if findName in supTopNames:
        row = suppRefs.iloc[supTopNames.index(findName)]
        RefX = row['top x']
        RefY = row['top y']
        RefRad = row['top radius'] 
        RefZ = row['top z']
    else:    #for non supplementals
        RefX = refSegs.loc[k,'top x']
        RefY = refSegs.loc[k,'top y']
        RefRad = refSegs.loc[k,'top radius']
        RefZ = refSegs.loc[k,'top z']
    return(RefX,RefY,RefRad,RefZ)


    