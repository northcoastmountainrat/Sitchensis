# -*- coding: utf-8 -*-
"""
Created on Tue May 30 11:04:14 2017

@author: rdk10
"""

import numpy as np
import pandas as pd
import Functions as f
import pdb  #for debugging
import numbers as nu

def interpTrunks(trunkDat, logFileName, interpCol = 'dist'):   
    """ This function brings in a subset of trunk data with missing values of distance or azimuth and outputs interpolated values based on nighboring measurements"""
    #INPUTS: 
    #trunkDat = trunk data from raw field data
    #interpCol = defaults to dist but can also be set to azi to interp azimuths
    
    #locate indices where there is a number in the azi or dist column
    t1 = trunkDat['{0}'.format(interpCol)].astype(object) != 'interp'  
    t2 = trunkDat['{0}'.format(interpCol)].notnull()
    test = f.vectorBool(t1,t2,'and')
    
    refInd = trunkDat[test].index.tolist()

    #Tests to see if values needing interpolation are at the base or top of a trunk, If so a warning is issued (there is nothing to calc from)
    if all([ind < trunkDat.index.max() for ind in refInd]): 
        f.print2Log(logFileName, 'The lowest measurement in the tree needs to be interpolated but there is nothing to interpolate to')
    elif all([trunkDat.index.min() < ind for ind in refInd]):
        f.print2Log(logFileName, 'The highest measurement in the tree needs to be interpolated but there is nothing to interpolate to')
 
    if all(test) == True:
        return(trunkDat)
    #refInd = trunkDat[trunkDat['{0}'.format(interpCol)] != 'interp'].index.tolist()  #locate indices where dist or azi are NA, located bordering numbers, interpolate
    else:
    #Convert distances to number if still string after operation, convert azis to int    
        for i in range(len(refInd)-1):
            rowCount = refInd[i]-refInd[i+1]-1  # number of rows needing calculation within each bounded section of interp heights
            if rowCount < 1:
                pass
            else:
                interpInd = [ x + 1 + refInd[i+1] for x in list(range(rowCount))]  #Indices of current rows to calc
                baseInd = refInd[i]
                topInd = refInd[i+1] 
                
                for j in interpInd:
                    baseDist = trunkDat['{0}'.format(interpCol)].loc[baseInd] #ref
                    baseHt = trunkDat['height'].loc[baseInd] #ref
                    topDist = trunkDat['{0}'.format(interpCol)].loc[topInd] #ref
                    topHt = trunkDat['height'].loc[topInd] #ref
                    targetHt = trunkDat['height'].loc[j] #calcRow
                    trunkDat.loc[j,'{0}'.format(interpCol)] = (targetHt-topHt)*(baseDist-topDist)/(baseHt-topHt)+topDist #interpolate
                    trunkDat.loc[j,'ref type'] = 'p2p'
        if interpCol == 'dist':    
            trunkDat.assign(dist = trunkDat['{0}'.format(interpCol)].astype(np.float64))
        else:
            trunkDat.assign(azi = trunkDat['{0}'.format(interpCol)].astype(np.float64))

        return(trunkDat)
    
def trunkRoutine(trunkDat, custRefs, logFileName):
    ##Inputs are all the trunk data, and any custom reference data
    ##Output is the trunk data with all calculations of X,Y,Z positions. 
    
    #Height-sorted Dictionary of dataframes, one for each trunk
    #1)Create subsets of data based on trunk name.    
    mainTrunks = f.breakDataByName(trunkDat)
    #interpolate values that need it. (dist, azi), locate integers between indexes where we have info and calc                           
    for trunk in mainTrunks:
        trunkDat = mainTrunks[trunk]
        
        #first change all p2f to p2p then interp where there is a value in dist
        tempTrunk = trunkDat[pd.notnull(trunkDat['dist'])].copy()   #Copy to avoid chained indexing error
        for i in tempTrunk.index:
            if trunkDat.at[i,'ref type'] == 'p2f': #if p2f convert to p2p
                trunkDat.at[i,'dist'] = trunkDat.at[i,'dist'] + trunkDat.at[i,'diam']/200   #Add in the radius in m from cm
                trunkDat.at[i,'ref type'] = 'p2p'  #Change all the labels
        
        mainTrunks[trunk] = interpTrunks(trunkDat, logFileName,'dist')
        mainTrunks[trunk] = interpTrunks(trunkDat,logFileName,'azi')  
    

    #Bring the dataframe back together and add columns
    reorder = trunkDat.columns.values
    trunkDat = pd.concat(list(mainTrunks.values()))
    trunkDat = trunkDat[reorder]
    trunkDat = pd.concat([trunkDat, pd.DataFrame(columns = ['ref x', 'ref y', 'ref z', 'ref radius','x','y','z'])], sort = False)
    reorder = np.append(reorder[reorder!='notes'],['ref x', 'ref y', 'ref z', 'ref radius','x','y','z','notes'])
    trunkDat = trunkDat[reorder]                   #resort columns
    
    #Seperate out the calculation values we'll need
    calcVals = trunkDat.loc[:,['dist','azi', 'radius','ref type']]
    
    #First calculate where refs == Ground or where refs = a custom ref, then calculate the rest in height order
    if len(trunkDat.index[trunkDat['ref'] == 'G'].tolist())>0:
        grdInd = trunkDat.index[trunkDat['ref'] == 'G'].tolist()
        refVals = [0,0,0]
        trunkDat = calcTrunkVals(trunkDat, refVals, calcVals, grdInd)
    
    #This is for all custom references
    if len(custRefs) > 0:
        for matchRef in custRefs['name']:
            if all(trunkDat['ref'].str.contains(matchRef) == False):
                print('\nMake sure the reference name in the cust refs tab and in the main trunk tab are spelled the same. There is no match for "{0}" in references for the main trunks'.format(matchRef))
                f.print2Log(logFileName, '\nMake sure the reference name in the cust refs tab and in the main trunk tab are spelled the same. There is no match for "{0}" in references for the main trunks'.format(matchRef))
            else:
                Ind = trunkDat.index[trunkDat['ref'] == matchRef]
                refVals = [custRefs['x'].iloc[0],custRefs['y'].iloc[0],custRefs['radius'].iloc[0]]  #custom reference x, y, and radius    
                trunkDat = calcTrunkVals(trunkDat, refVals, calcVals, Ind)
    
    #Now locate other references and try to calculate them. 
    #1) get indices of references with @ symbol
    if any(pd.isnull(trunkDat['ref'])):
        print('There are missing references for the main trunk, these must be filled in prior to running the program.')
        f.print2Log(logFileName, 'There are missing references for the main trunk, these must be filled in prior to running the program.')
    
    trunkSub  = trunkDat[trunkDat['ref'].str.contains("@")]
    trunkSub1 = trunkSub['ref'].str.upper()
    trunkSub1 = trunkSub1.drop_duplicates()
    
    #2)Seperate out the ref from the height
    refNames = trunkSub1.str.split('@').str.get(0)  #get the top names
    refHeights = trunkSub1.str.split('@').str.get(1) #get the height
    refNames = refNames.replace(' ','')
    refHeights = refHeights.replace(' ','')
    refHeights = refHeights.astype(float)  
    
    #################
    # break if more than 10 iterations and post error message
    # while condition might is that there are still uncalculated x and y vals for the ref locations. 
    numNan = trunkSub.loc[:,['x','y']].isnull().sum().sum()  #number of uncalculated values in the xy cols of references to other heights (e.g. M@50)
    counter = 0
    while numNan > 0 and counter < numNan/2+1: #this loops through all the refNames and calculates the x,y for each row where it matches the ref
        #i = 0
        ####################
        for i in range(len(refNames)):
            #3)locate the x,y,z of the reference
            ref = refNames.iloc[i]
            ht = refHeights.iloc[i]
            
            if ref not in mainTrunks:
                f.print2Log(logFileName, 'Double check references, reference {0} is not part of the main trunk'.format(ref))
                #pass         
            elif len(mainTrunks[ref][mainTrunks[ref]['height']== ht]) == 0:
                f.print2Log(logFileName,'There is no {0} m height on trunk {1}, double check your reference to {1}@{0}'.format(ht,ref))
                #pass
            else:
                ind = mainTrunks[ref][mainTrunks[ref]['height']== ht].index[0]                          #index of reference row
                refVals = [trunkDat['x'].loc[ind],trunkDat['y'].loc[ind],trunkDat['radius'].loc[ind]]   #reference values x,y, radius
                #test if the ref values are calculated yet, if not get them on the next go.
                if any(np.isnan(refVals)):
                    pass
                else:
                ##OK, this is the row I need, now I just need to save the info and use code from custom refs. 
                #4) calculate
                    refName = trunkDat['ref'].str.split('@').str.get(0)
                    calcInd  = list(trunkDat[refName==ref].index)  #Matching Indices in calc data with ref data
                    trunkDat = calcTrunkVals(trunkDat, refVals, calcVals, calcInd)
        #i = i + 1
        counter = counter + 1
        #print(ref + '@' + ht)
        trunkSub  = trunkDat[trunkDat['ref'].str.contains("@")]
        numNan = trunkSub.loc[:,['x','y']].isnull().sum().sum()  #caluclates the number of missing calcs
        #print(counter)
        #print(numNan)
        #print(counter)
        #print(numNan)
        #print(trunkDat.loc[:, ['name','x','y','dist','height']])
        
        if counter == 10 and numNan < 0:
            print("There is at least one trunk references using the @ symbol that was not calculateable, double check the input file for correct referencing")

    return(trunkDat)

#Break up dataset into dictionary
def arrangeTrunkData(trunkDat, logFileName):
    """Brings in a dataframe of the trunk format as collected in the field and returns a dictionary of dataframes reorganized into the segment format"""
    
    mainTrunks = f.breakDataByName(trunkDat)
    
    for trunk in mainTrunks:
        #For each dataframe (trunk Name) I need to copy indices 1:n and cbind to indices 0:n-1, I also need to add a 'base', or 'top' to each col header
        #mainTrunks[trunk].columns
        trunkSub = mainTrunks[trunk].sort_values(by = 'height', ascending = False)
        rows = len(trunkSub)
        
        if rows == 1: #Check to make sure all trunks have at least two rows. 
            delTrunk = trunk
        else:
            renameCols = ['height','diam','radius','dist','azi','ref','ref radius', 'ref type','ref x', 'ref y', 'ref z','x','y', 'z']
            colIndices = [trunkSub.columns.get_loc(s) for s in renameCols]
            
            #setup and fill base infromation
            baseTrunks = trunkSub.iloc[1:rows]
            #renameColumns that need it
            newNames = ['base '+ name for name in renameCols]
            cvals = baseTrunks.columns.values
            cvals[colIndices]=newNames
            baseTrunks.columns = cvals
            
            ###Sometimes there are no notes, so I need to take that into account
            ind1 = baseTrunks['notes'].index[0]
            if  type(baseTrunks['notes'].iloc[0])==str and type(trunkSub['notes'].iloc[0])==str:
                baseTrunks.at[ind1,'notes'] = 'Base Note: ' + baseTrunks['notes'].iloc[0] + '  Top note: ' + trunkSub['notes'].iloc[0]
            elif type(baseTrunks['notes'].iloc[0])!=str and type(trunkSub['notes'].iloc[0])==str:
                baseTrunks.at[ind1,'notes'] = 'Top note: ' + trunkSub['notes'].iloc[0]
            elif type(baseTrunks['notes'].iloc[0])!=str and type(trunkSub['notes'].iloc[0])!=str:
                pass
        
            #Setup and fill top information
            topTrunks = trunkSub.iloc[0:rows-1,colIndices]
            newNames = ['top '+name for name in renameCols]
            topTrunks.columns = newNames
            
            #combind datasets
            reorderBase = baseTrunks.columns.values
            reorderTop = topTrunks.columns.values
            reorder = np.append(reorderBase[reorderBase!='notes'],np.append(reorderTop,'notes'))
            mainTrunks[trunk] = pd.concat([baseTrunks.reset_index(drop = True),topTrunks.reset_index(drop = True)], axis = 1)
            mainTrunks[trunk] = mainTrunks[trunk][reorder]
            #trunkDat = trunkDat[reorder]
    
    if 'delTrunk' in locals():   
        mainTrunks.pop(delTrunk, None)
        f.print2Log(logFileName,'Warning: trunk "{0}" only had one line of data so will be deleted\n'.format(delTrunk))    
        
    return(mainTrunks)

def calcTrunkVals (trunkDat, refVals, calcVals, indices):
    ###This function brings in a data.frame, reference values, calculation values and the indices that need calculating and outputs a data.frame with the values calculated.  
    ##there is a description of what the reference values, calculation values are in the calcPosition function. 
    ##refVals is a list, calcVals is a data.frame
    
    for ind in indices:
        cVals = calcVals.loc[ind].values.tolist()
        position  = f.calcPosition(refVals, cVals, calcType = 'trunk')
#        trunkDat.set_value(ind,'ref x',refVals[0])
        trunkDat.at[ind,'ref x'] = refVals[0]
 #       trunkDat.set_value(ind,'ref y',refVals[1])
        trunkDat.at[ind,'ref y'] = refVals[1]
  #      trunkDat.set_value(ind,'ref radius',refVals[2])
        trunkDat.at[ind,'ref radius'] = refVals[2]
   #     trunkDat.set_value(ind,'x',position['x'])
        trunkDat.at[ind,'x'] = position['x']
    #    trunkDat.set_value(ind,'y',position['y'])
        trunkDat.at[ind,'y'] = position['y']
     #   trunkDat.set_value(ind,'z',trunkDat['height'].loc[ind]) 
        trunkDat.at[ind,'z'] = trunkDat['height'].loc[ind]
    return(trunkDat)

def segs2custRefs(segs, custRefs, logFileName, error = False):
    """Brings in segment frame, extracts rows that match any in the custom references, utilizes them to match with cust ref info to copy over to segs"""
    
    #loop through bases and tops
    for j in range(2):
        if j == 0:
            string = 'base'
        else:
            string = 'top'
        #Extract rows where ref is in cust refs
        calcSegs = segs[segs['{0} ref'.format(string)].isin(custRefs['name'])].copy()  #use a copy to avoid chained indexing, calcSegs is temporary anyway
       
        #Maps the values x,y,radius of custRefs to calcSegs with matching names in base or top ref 
        calcSegs['{0} ref x'.format(string)] = calcSegs['{0} ref'.format(string)].map(custRefs.set_index(custRefs['name'])['x'])
        calcSegs['{0} ref y'.format(string)] = calcSegs['{0} ref'.format(string)].map(custRefs.set_index(custRefs['name'])['y'])
        calcSegs['{0} ref radius'.format(string)] = calcSegs['{0} ref'.format(string)].map(custRefs.set_index(custRefs['name'])['radius'])
              
        #Go through all the needed rows and do the calculations
        for i in calcSegs.index: 
            #Calculate positional information for this row and column. 
            refVals = [calcSegs.loc[i,'{0} ref x'.format(string)], calcSegs.loc[i,'{0} ref y'.format(string)], calcSegs.loc[i,'{0} ref radius'.format(string)]]
            positionMeasures = [calcSegs.loc[i,'{0} dist'.format(string)], calcSegs.loc[i,'{0} azi'.format(string)], calcSegs.loc[i,'{0} radius'.format(string)], calcSegs.loc[i,'{0} ref type'.format(string)]]

            if 'int' in positionMeasures or any([item!=item for item in positionMeasures]): #look for 'int' or Nan
                print('There are missing values of dist, azi, or radius for segments referenced to custom references. You must provide these numbers.')
                f.print2Log(logFileName, 'There are missing values of dist, azi, or radius for segments referenced to custom references. You must provide these numbers.')
                
            calcs = f.calcPosition(refVals, positionMeasures,calcType = 'segment')
            
            #assign to original data.frame  
            segs.loc[i,'{0} x'.format(string)] = calcs['x']
            segs.loc[i,'{0} y'.format(string)] = calcs['y']
            segs.loc[i,'{0} ref x'.format(string)] = calcSegs.loc[i,'{0} ref x'.format(string)]
            segs.loc[i,'{0} ref y'.format(string)] = calcSegs.loc[i,'{0} ref y'.format(string)]
            segs.loc[i,'{0} ref radius'.format(string)] = calcSegs.loc[i,'{0} ref radius'.format(string)]
            
    return(segs)

def segs2trunks(segmentFrame,referenceFrame, custRefs, logFileName, error = False):  
    """Brings in the segment dataframe and a dictionary of reference data.frames broken up into seperate data.frames for each reference trunk name. 
    The code then looks at the reference name and matches that with the name of a reference. It then finds where a reference has a height
    on either side of the node needs reference calcuations and interpolates the reference x, y, and radius at the height of the node
    in question. There is some error logging here that opens the error log file and ourputs any errors encountered. A boolean error variable is passed 
    in from the main script that is set to False if there are no previous errors. The log file is a string of the log file name to append error information to."""
    for j in range(2):  #1 = base loop; 2 = top loop
         for i in range(len(segmentFrame.index)):  #i = all row indices
            if j == 0: #set this variable to determine if we calculate reference coordinates for base or top of segment
                string = 'base'
            else:
                string = 'top'
            
            #get name of base or top ref depending on value of "j"
            refName = str(segmentFrame['{0} ref'.format(string)].iloc[i])
            refName = refName.replace(" ","")
            refHt = segmentFrame['{0} z'.format(string)].iloc[i]
            
            if string == 'base':
                dashes = segmentFrame['name'].iloc[i].count('-')            #More than two dashes in the base name means this is a mid-segment segment 
            else:
                dashes = 1                                                 #if it is the top of a segment is shouldn't matter so long as the reference if correct        

            if dashes >2 and refName.isalpha():
                f.print2Log(logFileName, "Careful there buddy: the reference for mid-segment {0} is {1} and should probably be the segment base".format(segmentFrame['name'].iloc[i],refName))
          
            #This operates on rows with a letter ref that does not equal 'calc', is not a mid-segment segment, that does not have @ notation and that is not in cust refs
            if len(custRefs)>0: #Are there cust refs to test against?
                test = (refName.isalpha() and refName.lower() != 'calc' and dashes < 2 and not any(custRefs['name'].isin([refName]))) or (refName.count('@') > 0)
            else:
                test = (refName.isalpha() and refName.lower() != 'calc' and dashes < 2) or (refName.count('@') > 0)
            if test:
                #if refname uses the @ notation
                if refName.count('@') > 0:
                    rn = refName
                    refName = rn.split('@')[0]
                    refHt = float(rn.split('@')[1])   
                #if refName is 'Mtop' then refHt is highest top in main trunks 
                elif ('M' in refName and 'top' in refName):
                    tempFrame = referenceFrame['M']
                    refHt = round(float(tempFrame['top z'].max()),2)
                    refName = 'M'
                elif isinstance(refHt,np.float64) or isinstance(refHt, np.int64): #convert numpy.floats to native floats, not sure why but several heights are imported as numpy.float not float
                    refHt = refHt.item()
               
                if type(refHt) != float and type(refHt) != int:
                    print("Check the {0} reference height for segment {1}, it is not a number.".format(string,segmentFrame['name'].iloc[i]))
                    f.print2Log(logFileName,"Check the {0} reference height for segment {1}, it is not a number.".format(string,segmentFrame['name'].iloc[i]))
                    error = True

                if all([refName != key for key in referenceFrame]):
                    print('The refName "{0}" for the {1} of segment "{2}" does not match any of the trunk names'.format(refName, string, segmentFrame.loc[i,'name']))
                    f.print2Log(logFileName, 'The refName "{0}" for the {1} of segment "{2}" does not match any of the trunk names'.format(refName, string, segmentFrame.loc[i,'name']))
                             
                #Call appropriate rows from mainT or segment data from the reference data.frame provided 
                tRows = referenceFrame['{0}'.format(refName)]
                x=refHt >= tRows['base z']
                y=refHt <= tRows['top z']
                interpRow = tRows[[a and b for a, b in zip(x, y)]][:1] #intersection of boolean vectors is correct index
        
                #Interp x,y,r
                if interpRow.empty:
                    print("There are no main trunk sections surrounding the {0} height of the segment: {1}".format(string,segmentFrame['name'].iloc[i]))
                    f.print2Log(logFileName, "There are no main trunk sections surrounding the {0} height of the segment: {1}, if referencing the main below this segment use M@height for the ref\n".format(string,segmentFrame['name'].iloc[i]))
                    error = True
                
                else:
                    interpVals = f.linearInterp(interpRow,refHt) #dictionary of interpolated values under 'ref_X','ref_Y', and 'ref_R'
                    
                    if interpVals['errors']:
                        f.print2Log(logFileName, "Target height of {0} of segment {1} is not between reference heights".format(string, segmentFrame['name'].iloc[i]))
                        error = True
                    #Copy x,y,r to sement row
                    segmentFrame.at[i,'{0} ref x'.format(string)] = interpVals['ref_X'].iloc[0]
                    segmentFrame.at[i,'{0} ref y'.format(string)] = interpVals['ref_Y'].iloc[0]
                    segmentFrame.at[i,'{0} ref radius'.format(string)] = interpVals['ref_R'].iloc[0]  
                    
                    #Calculate positional information for this row and column as well. 
                    refVals = [interpVals['ref_X'].iloc[0],interpVals['ref_Y'].iloc[0], interpVals['ref_R'].iloc[0]]
                    positionMeasures = [segmentFrame['{0} dist'.format(string)].iloc[i],segmentFrame['{0} azi'.format(string)].iloc[i],
                                                     segmentFrame['{0} radius'.format(string)].iloc[i],segmentFrame['{0} ref type'.format(string)].iloc[i]]
                    
                    calcs = f.calcPosition(refVals, positionMeasures,calcType = 'segment')
                    
                    segmentFrame.at[i,'{0} x'.format(string)] = calcs['x']
                    segmentFrame.at[i,'{0} y'.format(string)] = calcs['y']
                    #pdb.set_trace()
                    if calcs['error'] == True:
                        f.print2Log(logFileName,'Segment {0} reference assumed to be face to pith (reference to target)'.format(segmentFrame['name'].iloc[i]))
                    error = calcs['error']
                    
    f.closingStatement(logFileName, error)
            
    return (segmentFrame) 

def segs2nodes(segs, logFileName, error = False):
    """inputs a segment dataframe, brings in references that were calculated, and calculates x,y, and z values for base and top"""
    """ If no rows need calculating the code skips the calculation process and outputs the input dataframe, this is to be efficient when while looping through all the routines"""

    #This tests for rows that need calculating
    calcSegs = f.isnumber(segs) #Segments referenced to nodes that may need calculations 

    if len(calcSegs) == 0: # There must be some rows that need calculation otherwise nothing is calculated
        return(segs)                                    
    #only do calculations if we need to (there must be unclculated values in the base or top of the segment)
    elif calcSegs['baseTest'].sum() + calcSegs['topTest'].sum() > 0:
        #If base x,y,or z = NA AND ref is numeric and only only one number 
                          
        refSegs = segs[pd.isnull(segs['top x'])==False] #segments that have calculations for referencing

        #Move references over to ref cols and calculate x,y positions, copy complete rows to refSegs and repeat
        for i in calcSegs.index: #for each row that needs a caluclation if referenced to nodes
            for j in range(2):  #this is for base vs top
                if j == 0:
                    string = 'base'
                else:
                    string = 'top'
                #If this is a node that needs calculating (is a node number depending on if base or top)    
                if calcSegs.loc[i,'{0}Test'.format(string)] :   #test variable asks if node is numeric using column created by f.isnumber above
                    findName = calcSegs.loc[i,'{0} ref'.format(string)]
                    if type(findName)!=str: #sometimes import from excel produces mixed variable types, need to convert to string
                        findName = str(findName)
                        calcSegs.at[i,'{0} ref'.format(string)] = findName
                        if type(findName)==str:
                            print("Reference variable at {0} of segment {1} converted to string".format(string,calcSegs.loc[i,'name']))
                            f.print2Log(logFileName,"\nReference variable at {0} of segment {1} converted to string".format(string,calcSegs.loc[i,'name']))
                            error = True
                        else:
                            print("Attempeted and failed to convert {0} of segment {1} to string".format(string,calcSegs.loc[i,'name']))
                            f.print2Log(logFileName,"\nAttempeted and failed to convert {0} of segment {1} to string".format(string,calcSegs.loc[i,'name']))
                            error = True
                    
                    nodeRow = refSegs[refSegs['top name'] == findName]

                    if len(nodeRow) != 0: #skip if there is not matching node row and get it on the next pass
                        if len(nodeRow)==1:
                            nodeRow = nodeRow
                        elif len(nodeRow) >1:
                            #If they do match and none are 'mid' position then use top supplemental row 
                            if all(nodeRow['name'] == nodeRow['name'].iloc[0]) and sum(nodeRow['position']=='mid') > 0:
                                midSegOuts = f.midSegTopLocator(nodeRow, logFileName, error)  #get the most distal of the midsegment rows
                                nodeRow =  midSegOuts[0]
                                error = midSegOuts[2]
                                                                   
                                if len(nodeRow)==0:
                                    f.print2Log(logFileName,'Make sure that you lebelled supplemental measurements "mid" in the position column for segment {0}.'.format(findName))
                            #If the node names do not match
                            else: 
                                nodeRow = nodeRow.iloc[0]
                                f.print2Log(logFileName,'\nWarning: There were more than one node matches the ref "{2}" for the {0} of segment {1}, the first was used. If refencing to a segment with a supplemental measurement, make sure the position column says "mid" for supplemewntal rows'.format(string, calcSegs['name'].loc[i], nodeRow['top name'])) #.values
                                error = True
                            
                        #Assign Referenece values
                        RefX = float(nodeRow['top x'])
                        RefY = float(nodeRow['top y'])
                        RefRad = float(nodeRow['top radius'] )
                                                                  
                        #set refs and position to node location baseded on top node of origin segment 
                        segs.loc[i,['{0} ref x'.format(string),'{0} x'.format(string)]] = RefX
                        segs.loc[i,['{0} ref y'.format(string),'{0} y'.format(string)]] = RefY
                        segs.at[i,'{0} ref radius'.format(string)] = RefRad
                        
                        #Calc x and y based on refs, dist, and azi
                        posMeasures = [segs.loc[i,'{0} dist'.format(string)],segs.loc[i,'{0} azi'.format(string)],
                                       segs.loc[i,'{0} radius'.format(string)],segs.loc[i,'{0} ref type'.format(string)]]
                        
                        calcs = f.calcPosition(refVals = (RefX, RefY, RefRad), calcVals = posMeasures, calcType = 'segment')
                        segs.at[i,'{0} x'.format(string)] = calcs['x']
                        segs.at[i,'{0} y'.format(string)] = calcs['y']
                        
                        Z_offset = 0
                        if string == 'base' and isinstance(calcSegs['notes'].loc[i], str): #If there is a note
                            if 'from top' in calcSegs['notes'].loc[i]:
                                Z_offset = float(RefRad)
                            elif 'from bot' in calcSegs['notes'].loc[i]:
                                Z_offset = -float(RefRad)

                            segs.at[i,'base z'] = segs.loc[i,'base z'] + Z_offset
                        
                        if calcs['error'] == True:
                            f.print2Log(logFileName,'Segment {0} reference assumed to be face to pith (reference to target)'.format(segs['name'].iloc[i]))
                        error = calcs['error']                    

    f.closingStatement(logFileName, error)                      
    return(segs)

def segs2reits(segs, logFileName, error = False):
    
    #Get values for interpolation
    for j in range(2):
        if j == 0: #set this variable to determine if we calculate reference coordinates for base or top of segment
            string = 'base'
        else:
            string = 'top'
            
        refs = segs['{0} ref'.format(string)]
        names = segs['name']
        heights = segs['{0} z'.format(string)]
        types = segs['type']
        
        ##Anything referenced to a trunk segment###
        segsFromReitIndex = f.refSegType(refs, names, heights, types,'t').tolist()
                            
        ##Only do the routine if there are rows that need calculations                                
        calcSegs = segs.loc[segsFromReitIndex]
       # pdb.set_trace()
        if np.isnan(calcSegs.loc[:,['{0} x'.format(string), '{0} y'.format(string)]]).sum().sum() > 0: #if there are any empty cells
            
            for i in calcSegs.index: #find indices of test and cycle over
                refName = calcSegs['{0} ref'.format(string)].loc[i]
                refRow = segs[segs['name']==refName] #Index of segs to look in for base and top information
                
                #Deals with supplemental rows and extracts correct row
                if len(refRow)==0:
                    f.print2Log(logFileName,'There are no reiterationed trunks matching the origin of {0} for segment {1}'.format(refName,calcSegs.loc[i,'name']))
                    error = True
                #Need to locate correct row if we have multiple rows
                elif len(refRow)> 1:
                    refHt = calcSegs.loc[i,'{0} z'.format(string)]
                    
                    if isinstance(refHt,np.float64) or isinstance(refHt, np.int64): #convert numpy.floats to native floats, not sure why but several heights are imported as numpy.float not float
                        refHt = refHt.item()
                    
                    x=refHt >= refRow['base z']
                    y=refHt <= refRow['top z']
                    refRow = refRow[[a and b for a, b in zip(x, y)]][:1] #intersection of boolean vectors is correct index               

                    if len(refRow) == 0:
                        pdb.set_trace()
                        print("The height of the {0} of segment {1} is not between the reiterated trunk {2} heights".format(string, calcSegs['name'].loc[i], refName))
                        f.print2Log(logFileName,"The height of the {0} of segment {1} is not between the reiterated trunk {3} heights".format(string, calcSegs['name'].loc[i], refName))
                
                #Calculate ref vals, pass to function to calc final x,y, and radius
                refValues = f.linearInterp(refRow, calcSegs['{0} z'.format(string)].loc[i], logFileName) #pass in the reference row and the reference Height
                
                refVals = [None]*3
                refVals[0] = refValues['ref_X']
                refVals[1] = refValues['ref_Y']
                refVals[2] = refValues['ref_R']
                
                posMeasures = [None]*4
                posMeasures [0] = calcSegs['{0} dist'.format(string)].loc[i]
                posMeasures [1] = calcSegs['{0} azi'.format(string)].loc[i]
                posMeasures [2] = calcSegs['{0} radius'.format(string)].loc[i]
                posMeasures [3] = calcSegs['{0} ref type'.format(string)].loc[i] 
             
                calcs = f.calcPosition(refVals, posMeasures, 'segment')  
                segs.at[i,'{0} ref x'.format(string)] = refVals[0]
                segs.at[i,'{0} ref y'.format(string)] = refVals[1]
                segs.at[i,'{0} ref radius'.format(string)] = refVals[2]
                
                segs.at[i,'{0} x'.format(string)] = calcs['x']
                segs.at[i,'{0} y'.format(string)] = calcs['y']
                
                if calcs['error'] == True:
                    f.print2Log(logFileName,'Segment {0} reference assumed to be face to pith (reference to target)'.format(segs['name'].iloc[i]))
                    error = calcs['error']
                elif refValues['errors'] == True:
                    f.print2Log(logFileName, "Target height of {0} of segment {1} is not between reference heights".format(string, calcSegs['name'].loc[i]))
                    error = True
                else:
                    error = False 
    f.closingStatement(logFileName, error)
        
    return(segs)

def segs2midsegs(segs, logFileName, error = False):
    #Test for references to segments without height measurements
    test1 = segs['base name'].str.contains('-') & segs['base z'].map(lambda x: not isinstance(x, (int, float)))  #This works for the T2 and prez (calc instead of missing), doesn't sork for missing numbers
    test2 = segs['base name'].str.contains('-') & pd.isnull(segs['base z'])  #Works for fin, runs for T2, runs for prez
    test = f.vectorBool(test1,test2,'or')
    #test = segs['base ref'].str.contains('-') & [not i for i in segs['base z'].map(np.isreal)] #Test for references to segments without height measurements
    calcSegs = segs[test]
    
    if sum(test) > 0: #Only run through this if there are rows that even need it. 
    
        #Separate name into node names for later searching.
        #nodeNames = f.splitName(segs['name'])
        
        for i in calcSegs.index:
            if isinstance(calcSegs['base azi'].loc[i],nu.Number): #Sometimes the data will say "calc" here, this tests for that
                azi = calcSegs['base azi'].loc[i] #use base azi if there is one specified
            elif isinstance(calcSegs['top azi'].loc[i],nu.Number):
                azi = calcSegs['top azi'].loc[i] #otherwise use the top azi
                print("Warning: There a missing base azimuth for segment {0}, top azi taken as base".format(calcSegs['name'].loc[i]))
                f.print2Log(logFileName,"Warning: There a missing base azimuth for segment {0}, top azi taken as base".format(calcSegs['name'].loc[i]))
                error = True
            
            dist2pt = calcSegs['midsegment dist'].loc[i]
            #if dist2pt is nan assign to middle of segment
            if np.isnan(dist2pt):
                dist2pt = 'mid'
                f.print2Log(logFileName, "Warning: No length to node given for midsegment {0}, origin assumed to be from middle of {1}".format(calcSegs['name'].loc[i],segs['base name'].loc[i]))
                error = True
            
            #Assign ref4Dist2pt, if there is one recorded use it otherwise use the top node from origin segment, will calc to center of orig segment
            if pd.notnull(calcSegs['midsegment ref'].loc[i]):
                ref4Dist2pt = calcSegs['midsegment ref'].loc[i]
            else:#if there is no ref4Dist 2 pt then 
                origName = calcSegs['base name'].loc[i]
                dashIndex = origName.rfind('-')
                ref4Dist2pt = origName[dashIndex+1:len(origName)] #return the top name of orig seg
                f.print2Log(logFileName, "Warning: No reference node given for midsegment {0}, origin assumed to be from middle of {1}".format(calcSegs['name'].loc[i],segs['base name'].loc[i]))
                error = True
                
            #Find segment with name matching base name of calc seg
            refSeg = segs[segs['name'] == calcSegs['base name'].loc[i]]
            if refSeg.empty:
                print("{0} matches no segment names for the origin name of segment {1}".format(calcSegs['base name'].loc[i].capitalize(),segs['name'].loc[i]))
                f.print2Log(logFileName,"{0} matches no segment names for the origin name of segment {1}".format(calcSegs['base name'].loc[i].capitalize(),segs['name'].loc[i]))
                error = True
        
            #Pass to midSegment calculator, this returns the x,y,z, refx, refy, and refR. Adds refR to refX and refY in direction of azi
            ##This handles the case where dist2pt doesn't exist and lets user know it is using midpoint of segment of origin.
            if ref4Dist2pt != refSeg['base name'].iloc[0] and ref4Dist2pt != refSeg['top name'].iloc[0]:
                f.print2Log(logFileName, 'The midsegment reference node {0} does not match a node from the reference "{1}" for segment {2} and will be skipped'.format(ref4Dist2pt,refSeg['name'].iloc[0], calcSegs['name'].loc[i]))
                error = True
            else:
                midVals = f.calcMidLoc(refSeg, dist2pt, ref4Dist2pt,calcSegs['base name'].loc[i], logFileName, azi, appendageType = "segment")
                
                segs.at[i,'base ref x'] = float(midVals['ref_X'])
                segs.at[i,'base ref y'] = float(midVals['ref_Y'])
                segs.at[i,'base ref radius'] = float( midVals['ref_R'])
                
                segs.at[i,'base x'] = float(midVals['X'])
                segs.at[i,'base y'] = float(midVals['Y'])
                
                Z_offset = 0
                if isinstance(calcSegs['notes'].loc[i], str): #If there is a note
                    if 'from top' in calcSegs['notes'].loc[i]:
                        Z_offset = float( midVals['ref_R'])
                    elif 'from bot' in calcSegs['notes'].loc[i]:
                        Z_offset = -float( midVals['ref_R'])

                segs.at[i,'base z'] = float(midVals['Z']) + Z_offset
            
    f.closingStatement(logFileName, error) 
    return(segs)

def brBase2Trunks(branches, mainTrunks, logFileName, error = False):
    
    """  Pass in dataframe of all branches and a distionary of main trunks with a different entry for each trunk """
         
    calcBr = branches[branches['origin'].str.isalpha()]
        
    for i in calcBr.index:  #i = all row indices
        #get name of base or top ref depending on value of "j"
        
        origin = calcBr['origin'].loc[i].upper()  #make reference upper case just for safety. 
        origin = origin.replace(' ','')
        brHt = float(calcBr['base ht'].loc[i])
    
        #Call appropriate rows from mainT or segment data 
        #print(i)
        #if i == 193:
            #pdb.set_trace()
            
        tRows = mainTrunks[origin]
        x = brHt >= tRows['base z']
        y = brHt <= tRows['top z']
        interpRow = tRows[[a and b for a, b in zip(x, y)]][:1] #intersection of boolean vectors is correct index
        
        #Interp x,y,r
        if interpRow.empty:
            print("There are no main trunk sections surrounding the base height of the branch: {0}".format(calcBr['name'].loc[i]))
            f.print2Log(logFileName, "There are no main trunk sections surrounding the base height of the branch: {0}".format(calcBr['name'].loc[i]))
            error = True
            
        else:
            interpVals = f.linearInterp(interpRow,brHt) #dictionary of interpolated values under 'ref_X','ref_Y', and 'ref_R'
            
            if interpVals['errors']:
                f.print2Log(logFileName, "Base height of branch {1} is not between reference heights".format(calcBr['name'].loc[i]))
                error = True
           
            #Create a 'base z' column if it doesn't already exist
            #if 'base z' not in branches.columns:
                #branches['base z'] = np.nan
   
            #Set reference values
            branches.at[i,'ref x'] = interpVals['ref_X'].iloc[0]
            branches.at[i,'ref y'] = interpVals['ref_Y'].iloc[0]
            branches.at[i,'ref radius'] = interpVals['ref_R'].iloc[0]
            branches.at[i,'ref z'] = branches['base z'].loc[i]
           
            #Calculate positional information for this row and column as well. 
            refVals = [interpVals['ref_X'].iloc[0],interpVals['ref_Y'].iloc[0], interpVals['ref_R'].iloc[0],branches['base z'].loc[i]]
            positionMeasures = [0, branches['orig azi'].iloc[i],branches['slope'].iloc[i]]
            
            calcs = f.calcPosition(refVals, positionMeasures, calcType = 'branchBase')
            
            branches.at[i,'base x'] = float(calcs['x'])
            branches.at[i,'base y'] = float(calcs['y'])
            
    f.closingStatement(logFileName, error)   
    
    return (branches) 

def brBase2nodes(branches, segs, logFileName, error = False):
    """inputs a branch and segment dataframe, brings in references that were calculated, and calculates x,y, and z values for branch base"""
    """ If no rows need calculating the code skips the calculation process and outputs the input dataframe, this is to be efficient when while looping through all the routines"""
    
    #This tests for rows that need calculating (ref is not letters of alphabet or a segment (contains a "-"))    
    notAlphaRef = ~branches['origin'].str.isalpha()
    notSegRef = ~branches['origin'].str.contains("-")
    calcBr = branches[[a and b for a, b in zip(notAlphaRef,notSegRef)]]
                                    
    #only do calculations if we need to (there must be unclculated values in the base or top of the segment)
    if np.isnan(calcBr['base x']).sum() + np.isnan(calcBr['base y']).sum() > 0:
        #If base x,y,or z = NA AND ref is numeric and only only one number                  
        refSegs = segs[pd.isnull(segs['top x'])==False] #segments that have calculations for referencing
        refSegs = refSegs[refSegs['position'].str.contains('butt') == False] # Exclude buttress rows
                  
        #Move references over to ref cols and calculate x,y positions, copy complete rows to refSegs and repeat
        for i in calcBr.index: #for each row that needs a caluclation if referenced to nodes
            #If this is a node that needs calculating (is a node number depending on if base or top)    
            findName = calcBr.loc[i,'origin']
            if type(findName)!=str: #sometimes import from excel produces mixed variable types, need to convert to string
                findName = str(findName)
                calcBr.at[i,'origin'] = findName
                if type(findName)==str:
                    print("Origin at base of branch {0} converted to string".format(calcBr.loc[i,'name']))
                    f.print2Log(logFileName,"\nOrigin at base of branch {0} converted to string".format(calcBr.loc[i,'name']))
                    error = True
                else:
                    print("Attempeted and failed to convert base of branch {0} to string".format(calcBr.loc[i,'name']))
                    f.print2Log(logFileName,"\nAttempeted and failed to convert base of branch {0} to string".format(calcBr.loc[i,'name']))
                    error = True
            
            #search in top nodes of the refSegs for the name of the ref from calcSegs     
            nodeRow = refSegs[refSegs['top name'] == findName]
                                        
            if len(nodeRow) == 0:
                f.print2Log(logFileName, 'There is no mathcing segment node for branch {0} with origin {1}'.format(branches.loc[i,'name'], findName))
                error = True
            elif len(nodeRow)==1:
                nodeRow = nodeRow
            elif len(nodeRow) >1:
                #If they do match and none are 'mid' position then use top supplemental row 
                if all(nodeRow['name'] == nodeRow['name'].iloc[0]) and sum(nodeRow['position']=='mid') > 0:
                    midSegOuts = f.midSegTopLocator(nodeRow, logFileName, error)  #get the most distal of the midsegment rows
                    nodeRow =  midSegOuts[0]
                    error = midSegOuts[2]
                                                       
                    if len(nodeRow)==0:
                        f.print2Log(logFileName,'Make sure that you lebelled supplemental measurements "mid" in the position column for segment {0}.'.format(nodeRow['name'])) 
                #If the node names do not match
                else: 
                    #pdb.set_trace()
                    #nodeRow = nodeRow.iloc[[0]]
                    f.print2Log(logFileName,'Warning: There were more than one node matches for the base of branch {0}, the first was used. The matching segments are {1}, double check the data'.format(branches.loc[i,'name'],[k for k in nodeRow['name']])) #.values
                    nodeRow = nodeRow.iloc[[0]]
                    error = True
                    
            if len(nodeRow)==1:
                #Set references to node locations, add 0.1 if from top or from bottom in notes
                RefX = float(nodeRow['top x'])
                RefY = float(nodeRow['top y'])
                RefRad = float(nodeRow['top radius'] )
                
                       
                #set refs and position to node location based on top node of origin segment                     
                branches.loc[i,['ref x','base x']] = RefX
                branches.loc[i,['ref y', 'base y']] = RefY
                branches.loc[i,'ref radius'] = RefRad
                
                ##If z does not equal branch z send error flag
                if float(nodeRow['top z']) != branches.loc[i,'base ht']:
                    f.print2Log(logFileName,'Warning: The base height of branch {0} does not match the height of the origin node (node {1}).\nThe node height was used instead of the branch height'.format(branches.loc[i,'name'],findName))
                    error = True
                
                Z_offset = 0 
                if isinstance(calcBr['notes'].loc[i], str): #If there is a note
                    if 'from top' in calcBr['notes'].loc[i]:
                        Z_offset = RefRad
                    elif 'from bot' in calcBr['notes'].loc[i]:
                        Z_offset = -1*RefRad
                
                RefZ = float(nodeRow['top z']) + Z_offset
                branches.loc[i,['ref z', 'base z']] = RefZ
            
    f.closingStatement(logFileName, error)                    
    return(branches)

def brBase2reits(branches, segs , logFileName, error = False):
    
    refs = branches['origin']
    segNames = segs['name']
    heights = branches['base z']
    segTypes = segs['type']
    
    ##Anything referenced to a trunk segment###
    test = f.refSegType(refs, segNames, heights, segTypes, 't').tolist()
              
    ##Only do the routine if there are rows that need calculations                                
    calcBr = branches.loc[test]

   # pdb.set_trace()
    if np.isnan(calcBr.loc[:,['base x', 'base y']]).sum().sum() > 0:
        
        for i in calcBr.index: #find indices of test and cycle over
            refName = calcBr.loc[i, 'origin']
            refRow = segs[segs['name']==refName] #Index of segs to look in for base and top information
            
            #Need to deal with reits with supplemental rows and get right row!!!
            if len(refRow)==0:
                f.print2Log(logFileName,'There are no trunk segments matching the origin of {0} for branch {1}'.format(refName,calcBr.loc[i,'name']))
                error = True
            #Need to locate correct row if we have multiple rows
            elif len(refRow)> 1:
                refHt = float(calcBr.loc[i,'base z'])
                
                if isinstance(refHt,np.float64) or isinstance(refHt, np.int64): #convert numpy.floats to native floats, not sure why but several heights are imported as numpy.float not float
                    refHt = refHt.item()
                
                x=refHt >= refRow['base z']
                y=refHt <= refRow['top z']
                refRow = refRow[[a and b for a, b in zip(x, y)]][:1] #intersection of boolean vectors is correct index   
                
                if (all(x == True) and all(y==False)) or (all(x==False)and all(y==True)):
                    f.print2Log(logFileName, "Target branch base height of branch {0} is not between reference heights, calculations will not proceed until this is fixed".format(calcBr['name'].loc[i]))

            #Calculate ref vals, pass to function to calc final x,y, and radius
            refValues = f.linearInterp(refRow, calcBr.loc[i,'base z'], logFileName) #pass in the reference row and the reference Height
            
            refVals = [None]*4
            refVals[0] = float(refValues['ref_X'])
            refVals[1] =float(refValues['ref_Y'])
            refVals[2] = float(refValues['ref_R'])
            refVals[3] = float(branches.loc[i,'base z'])
            
            posMeasures = [None]*4
            posMeasures [0] = 0
            posMeasures [1] = calcBr.loc[i,'orig azi'] 
         
            calcs = f.calcPosition(refVals, posMeasures, 'branchBase') 
    
            branches.at[i,'ref x'] = float(refVals[0])
            branches.at[i,'ref y'] = float(refVals[1])
            branches.at[i,'ref radius'] = float(refVals[2])
            branches.at[i,'ref z'] = float(refVals[3])
            branches.at[i,'base x'] = float(calcs['x'])
            branches.at[i,'base y'] = float(calcs['y'])
            
            if calcs['error'] == True:
                f.print2Log(logFileName,'Warning: Segment {0} reference assumed to be face to pith (reference to target)'.format(segs['name'].iloc[i]))
                error = calcs['error']
            elif refValues['errors'] == True:
                f.print2Log(logFileName, "Target branch base height of branch {0} is not between reference heights".format(calcBr['name'].loc[i]))
                error = True
    
    f.closingStatement(logFileName, error)         
            
    return(branches)

def brBase2midsegs(branches, segs, logFileName):
    
    error = False
    
    #test = branches['origin'].str.contains('-') & [i for i in branches['base z'].map(np.isnan)] #Test for references to segments without height measurements
    test1 = branches['origin'].str.contains('-') & branches['base z'].map(lambda x: not isinstance(x, (int, float)))  #This works for the T2 and prez (calc instead of missing), doesn't sork for missing numbers
    test2 = branches['origin'].str.contains('-') & pd.isnull(branches['base z'])  #Works for fin, runs for T2, runs for prez
    test = f.vectorBool(test1,test2,'or')

    calcBr = branches[test]

    if sum(test) > 0: #Only run through this if there are rows that even need it. 
        for i in calcBr.index:
            if isinstance(calcBr['orig azi'].loc[i],nu.Number): #Sometimes the data will say "calc" here, this tests for that
                azi = calcBr['orig azi'].loc[i] #use base azi if there is one specified
            elif isinstance(calcBr['cent azi'].loc[i],nu.Number):
                azi = calcBr['cent azi'].loc[i] #otherwise use the top azi
                f.print2Log(logFileName,"There is no base azimuth for branch {0}, the top azimuth was used for calculations".format(calcBr['name'].loc[i]))
                error = True
                
            dist2pt = calcBr['midsegment dist'].loc[i]
            #if dist2pt is nan assign to middle of segment
            if np.isnan(dist2pt):
                dist2pt = 'mid'
                #f.print2Log(logFileName, "No length to node given for midsegment branch {0}, origin assumed to be from middle of segment {1}".format(branches['name'].loc[i],branches['origin'].loc[i]))
                error = True
            
            origName = calcBr['origin'].loc[i]
            origName = origName.replace(' ','')
            #Assign ref4Dist2pt, if there is one recorded use it otherwise use the top node from origin segment, will calc to center of orig segment
            if pd.notnull(calcBr['midsegment ref'].loc[i]):
                ref4Dist2pt = calcBr['midsegment ref'].loc[i]
            else:#if there is no ref4Dist 2 pt then 
                dashIndex = origName.rfind('-')
                ref4Dist2pt = calcBr['origin'].loc[i][dashIndex+1:len(origName)] #return the top name of orig seg
                #f.print2Log(logFileName, "No reference node given for midsegment branch {0}, origin assumed to be from middle of segment {1}".format(calcBr['name'].loc[i],origName))
                error = True
            
            #Find segment with name matching base name of calc seg
            refSeg = segs[segs['name'] == origName]
            
            if refSeg.empty:
                f.print2Log(logFileName,"Branch origin of {0} matches no segment names and will be skipped".format(origName))
                error = True
            else:  
                #Pass to midSegment calculator, this returns the x,y,z, refx, refy, and refR. Adds refR to refX and refY in direction of azi
                ##This handles the case where dist2pt doesn't exist and lets user know it is using midpoint of segment of origin.
                brName = calcBr.loc[i,"name"]
                if ref4Dist2pt != refSeg['base name'].iloc[0] and ref4Dist2pt != refSeg['top name'].iloc[0]:
                    f.print2Log(logFileName, 'The midsegment reference node "{0}" does not match a node from the reference "{1}" for branch {2} and will be skipped'.format(ref4Dist2pt,refSeg['name'].iloc[0], brName))
                    error = True
                else:
                    midVals = f.calcMidLoc(refSeg, dist2pt, ref4Dist2pt,brName, logFileName, azi, appendageType = "branch")
                    
                    branches.at[i,'ref x'] = float(midVals['ref_X'])
                    branches.at[i,'ref y'] = float(midVals['ref_Y'])
                    branches.at[i,'ref radius'] = float( midVals['ref_R'])
                    branches.at[i,'ref z'] = float(midVals['Z'])
                    
                    branches.at[i,'base x'] = float(midVals['X'])
                    branches.at[i,'base y'] = float(midVals['Y'])

                    Z_offset = 0.0
                    if isinstance(calcBr['notes'].loc[i], str): #If there is a note
                        if 'from top' in calcBr['notes'].loc[i]:
                            Z_offset = float( midVals['ref_R'])
                        elif 'from bot' in calcBr['notes'].loc[i]:
                            Z_offset = -float( midVals['ref_R'])
           
                    branches.at[i,'base z'] = float(midVals['Z']) + Z_offset
            
    f.closingStatement(logFileName, error)
    return(branches)

def brTops(branches, logFileName, error = False):
    #First calculate vd if there is not a top height  
    calcBr = branches[np.isnan(branches['top ht'])]
    
    #First calc vd where needed if there is not a vd
    calcBr = calcBr[np.isnan(calcBr['vd'])]
    #calcBr = calcBr[calcBr['vd']!=calcBr['vd']]  #NaN test. NaN is the only thing that doen't = itself. 
    slope = calcBr['slope']
    if slope.dtype == object:  #sometimes this is imported as a string, likely because I had written calc in the slope column where I had a VD, better to leave it empty.  
        slope = slope.astype(float)
    ext = calcBr['hd']

    branches.at[calcBr.index,'vd'] = ext * np.tan((np.pi/180 * slope))

    if any(np.isnan(slope)):
        ind = np.isnan(slope)
        f.print2Log(logFileName,'There are some missing slopes for branche(s) {0} where there is not a vertical distance or top height, they will be assumed to be 0'.format(calcBr['name'][ind].tolist()))
        calcBr.at[ind,'slope'] = 0 
        branches.at[calcBr.index,'slope'] = calcBr['slope']  
        error = True
        
    #use vd to calc top ht
    calcBr = branches[np.isnan(branches['top ht'])]
    test = [isinstance(t,(int,float)) for t in calcBr['base z']]
    calcBr[[isinstance(t,(int,float))==False for t in calcBr['vd']]]
    topHt = calcBr['base z'][test] + calcBr['vd'][test]  
    branches.loc[topHt.index, ['top ht', 'top z']] = topHt

    #Take out rows where branches don't have base calculations
    test = pd.isnull(branches['base x'])  #
    calcBr = branches[test == False]
    missingBases = branches['name'].loc[test].tolist()
    if len(missingBases) >0:
         f.print2Log(logFileName,'Warning: Branch tops from branches {0} were not calcualted because their base locations are unresolved.'.format(missingBases))
        
    #feed into calcposition function
    refVals = [calcBr['base x'], calcBr['base y'],None, calcBr['base z']] #base positions
    calcVals = [calcBr['hd'], calcBr['cent azi']] #horizontal extention and slope
    topPos = f.calcPosition(refVals, calcVals, 'branchTop')
    
    #Assign new rows to just the ones needed
    calcBr.loc[:,'top x'] = topPos['x']
    calcBr.loc[:,'top y'] = topPos['y']
    calcBr.loc[:,'top z'] = branches['top ht']  #reassign in case there were branches with recorded top heights
    
    branches.at[calcBr.index,'top x'] = calcBr['top x']
    branches.at[calcBr.index,'top y'] = calcBr['top y']
    branches.at[calcBr.index,'top z'] = calcBr['top z']
    
    f.closingStatement(logFileName, error)
    return(branches)