# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 12:46:48 2017
@author: rdk10
"""

import numpy as np
import pandas as pd                            #For storing data as a data.frame
#import os, sys
##import numpy as np
#os.chdir('C:/Users/rdk10/Desktop/ComputerProgramming/Python/TreeCalcs')           #use this to nav to where files are stored                         #This adds the directory of the CrownMapFunctions module to the search path
#sys.path.append('C:/Users/rdk10/Desktop/ComputerProgramming/Python/TreeCalcs')
#sys.path.append('C:/Users/rdk10/Desktop/ComputerProgramming/Python/TreeViz')
import Functions as f    #This accesses the file with function definitions
import Routines as rt
#import numbers as n
import pdb
#import temp as tmp
#import numbers

def calculateTree(treeData, custRefs, mapType,  treeName, outDir, intermediateFiles = False):
    
    ##This is a giant function that brings in a dictionary of tree data and does all the calculations on it, 
    #
    #Inputs: dictionary of Trunk, segment, and trunk data, a dictionary with any custom references, a treeName and a logFileName
    #Outputs a dictionary with calculated Trunks, Segments, Branches, a logFile written to the current directory
    #The calculated dictioary can be directly input to the Plot tree routine. 
    
    treePathAndName = outDir + '/' + treeName
    logFileName = '{0}_ProcessLog.txt'.format(treePathAndName)
    treeName = logFileName.split('_')[0]
    
    lf = open(logFileName,'w') #open a file for writing ('w') to, lf for log file
    lf.write('\n#####################################################\n')
    lf.write('############## Main Trunk Calculations ##############\n')
    lf.write('#####################################################\n')
    lf.close()
    
    """Section for calculating things on the main trunk, this includes arranging the trunk
    into a segment-like form, it also calculates reference x,y locations, other locations 
    on the trunk with the @ symbol, and x,y of each section location"""
    
    #Calculates trunk values, resorts columns, not sure if I need to correct this as program looks for col names anyway. 
    #Row sorted by names then by height
    #pdb.set_trace()
    
    trunkDat = treeData['trunk']
    trunkDat = rt.trunkRoutine(trunkDat, custRefs, logFileName)  
    
    #####For testing ###########################################
    #trunkDat.loc[:,['name','height','ref','ref type','ref x','ref y','x','y']]
    ################################################################
    
    #Rearranges the trunk data into segment form
    mainTrunks = rt.arrangeTrunkData(trunkDat, logFileName)
    trunks = pd.concat(list(mainTrunks.values()),ignore_index = True)
    
    if intermediateFiles:
        trunks.to_csv('{0}_trunks.csv'.format(treeName), date_format = False, index = False) 
    
    """#################################################################################################"""
    """This section will do all the calculations on segments, starting with determining reference x,y
    locations on references main trunks and other trunk segments. """
    """#################################################################################################"""
    
    ###This is the log file I'll use to help error check. 
    lf = open(logFileName,'a')  #'a' stands for append
    lf.write('\n##################################################\n')
    lf.write('############## Segment calculations ##############\n')
    lf.write('##################################################\n')
    lf.close()

    if mapType == 'trunk map' or mapType == 'trunk and branch map': 
        f.print2Log(logFileName,'There are no segments in this tree') 

    if mapType == 'segment map' or mapType == 'full map':
        
        segs = treeData['segments']
        branches = treeData['branches']
        
        #######################################################################
        ########  Segments to Custom References  ##############################
        #######################################################################
        if len(custRefs)>0 and (any(segs['base ref'].isin(custRefs['name'])) or any(segs['top ref'].isin(custRefs['name']))):
            segs = rt.segs2custRefs(segs, custRefs, logFileName) 
    
        #######################################################################
        ######  References to Main Trunks   ###################################
        #######################################################################
        f.print2Log(logFileName,'\n############# Segments referenced to main trunks ############\n')

        ####This code calcualates the x,y values for segment bases and tops referenced to the main trunk. 
        segs = rt.segs2trunks(segs, mainTrunks, custRefs, logFileName)
        
        if intermediateFiles:
            segs.to_csv('{0}_segs2trunks.csv'.format(treeName), date_format = False, index = False) 
        
        #f.print2Log(logFileName, '\n\n############## Segments referenced to nodes #################\n')         
        
        """The while loop bleow cycles through all the segments until either all the rows are calculated or until it has cycled though
        a number of times equal to the numer of uncalculated rows + 1"""
        
        #Count the number of missing values
        emptyRows = int(np.isnan(segs.loc[:,['base x', 'base y','top x','top y']]).sum().sum()/2)
        #origNumRows = emptyRows
        counter = 0
        
        #loop until there are no more values to calculate or until a number of iterations = to rows needing calculating + 1
        # This loop is needed because we there are refs to segments that aren't calculated on the first pass. 
        while emptyRows > 0 and counter < 10:
            counter = counter + 1
            previousEmptyRows = emptyRows  #This is for the break statement at the end of the loop
            
            #######################################################################
            ######     References to Nodes      ###################################
            #######################################################################                                
            f.print2Log(logFileName, "\n############  Segments referenced to nodes round {0} #############\n".format(counter))
            segs = rt.segs2nodes(segs, logFileName)
            if intermediateFiles:
                segs.to_csv('{0}_segs2nodes{1}.csv'.format(treeName,counter), date_format = False, index = False)   
                             
            #######################################################################
            ######  References to Tunk segments   #################################
            #######################################################################
            
            f.print2Log(logFileName, "\n############  Segments referenced to trunk segments round {0} #############\n".format(counter))
            segs = rt.segs2reits(segs, logFileName)    
            if intermediateFiles:
                segs.to_csv('{0}_segs2reits{1}.csv'.format(treeName,counter), date_format = False, index = False)
            
            #######################################################################
            ############  Mid Segment Calcs  ######################################
            #######################################################################
            
            f.print2Log(logFileName, "\n############  Segments referenced to mid-segments round {0} #############\n".format(counter))
            segs = rt.segs2midsegs(segs, logFileName)
            if intermediateFiles:
                segs.to_csv('{0}_segs2midSegs{1}.csv'.format(treeName,counter), date_format = False, index = False)   
        
            emptyRows = int(np.isnan(segs.loc[:,['base x', 'base y','top x','top y']]).sum().sum()/2)
            f.print2Log(logFileName,'\nAfter pass {0} there are {1} uncalculated segment base or top locations'.format(counter, emptyRows))
            
            if emptyRows == previousEmptyRows:
                f.print2Log(logFileName,'\nThere are the same number of empty rows after the last pass, \ncheck to make sure these rows have enough information to calculate them'.format(counter, emptyRows))

                #locate where basex and basey are missing
                t1 = segs['base x'].isnull()  
                t2 = segs['base y'].isnull()
                test1 = f.vectorBool(t1,t2,'or')
                
                #locate where topy and topx are missing
                t1 = segs['top x'].isnull()  
                t2 = segs['top y'].isnull()
                test2 = f.vectorBool(t1,t2,'or')
                
                #create a combination "or" vector
                test3 = f.vectorBool(test1,test2,'or')
                
                #subset segnames using above vector
                emptySegs = segs.loc[test3,'name'].tolist()
                f.print2Log(logFileName,'\nThe offending segment(s) are {0}, check that the heights are between origin segment heights'.format(emptySegs))
            
                break             
    
    lf = open(logFileName,'a')  #'a' stands for append
    lf.write('\n\n####################################################\n')
    lf.write('##############   Branch calculations  ##############\n')
    lf.write('####################################################\n')
    
    lf.write('\n############# Branches bases referenced to main trunks ############\n')
    lf.close()
    
    if mapType == 'trunk and branch map' or mapType == 'full map':
        
        branches = treeData['branches']
          
        branches = rt.brBase2Trunks(branches, mainTrunks, logFileName)
        if intermediateFiles:
            branches.to_csv('{0}_brFromTrnk.csv'.format(treeName), date_format = False, index = False)   
                
        f.print2Log(logFileName, '\n############## Branch bases referenced to segments #################\n')
        f.print2Log(logFileName, '####################################################################\n')
        
        if mapType == 'full map' :
            
            f.print2Log(logFileName, '\n############## Branch bases referenced to nodes #################\n')
            branches = rt.brBase2nodes(branches, segs, logFileName)
            if intermediateFiles:
                branches.to_csv('{0}_brFromNodes.csv'.format(treeName), date_format = False, index = False) 
        
            f.print2Log(logFileName, "\n############  Branch bases referenced to trunk segments  #############\n")
            branches = rt.brBase2reits(branches, segs, logFileName)
            if intermediateFiles:
                branches.to_csv('{0}_brFromReits.csv'.format(treeName), date_format = False, index = False)   
                    
            f.print2Log(logFileName, "\n############  Branch bases referenced to mid-segments  #############\n")
            branches = rt.brBase2midsegs(branches, segs, logFileName)
            if intermediateFiles:
                branches.to_csv('{0}_brFromMidSegs.csv'.format(treeName), date_format = False, index = False) 
                
        else: f.print2Log(logFileName, "There are no segments on this tree to map to")
        
        f.print2Log(logFileName, "\n############  All branch tops  #############\n")
        branches = rt.brTops(branches, logFileName)
        if intermediateFiles:
            branches.to_csv('{0}_brFinal.csv'.format(treeName), date_format = False, index = False) 
    
    else: 
        f.print2Log(logFileName,'\nThere are no mapped branches for this tree')  
    
    lf = open(logFileName,'a')  #'a' stands for append
    lf.write('\n\n##################################################################\n')
    lf.write('##############   Final clean and output up etc....  ##############\n')
    lf.write('##################################################################\n')
    lf.close()
    
    date = pd.Timestamp("today").strftime("%d%b%Y").lstrip('0')
    finalFileName = '{0}_{1}.xlsx'.format(treeName, date)
    f.print2Log(logFileName,"Calculated and cleaned tree file output to: '{0}'".format(finalFileName))
                
    ## Rearrange column headers to make pretty
    trunkPrintCols = ['name','base radius','base x','base y','base z','top radius','top x','top y','top z', '% dead','s_fuzz','l_fuzz','notes']
    segPrintCols =['position','name','o/e','type','base radius','base x','base y','base z','top radius','top x','top y','top z', '% dead','s_fuzz','l_fuzz','notes']
    branchPrintCols = ['name','origin','o/e','l/d','base radius','base x','base y','base z','top radius','top x','top y','top z','slope','hd', '% dead','notes']
    
    ##Move non-main segemnts to segments dataframe and only include relevant columns
    sparseTrunks = trunks.loc[:,trunkPrintCols]
    
    if mapType == 'segment map' or mapType == 'full map':
        sparseSegments = segs.loc[:,segPrintCols]
    
    if mapType == 'trunk and branch map' or mapType == 'full map':
        sparseBranches = branches.loc[:,branchPrintCols]
    
    segAppendRows = sparseTrunks['name'] != 'M'
    if any(segAppendRows)==True:
        if mapType == 'trunk map' or mapType == 'trunk and branch map':
            sparseSegments = sparseTrunks.loc[segAppendRows]
        else:
            sparseSegments = sparseSegments.append(sparseTrunks.loc[segAppendRows])
            sparseTrunks = sparseTrunks.loc[segAppendRows == False]
            
    if mapType == 'trunk map':
       treeData = {'trunk': sparseTrunks}
    
    elif mapType == 'segment map':
        treeData = {'trunk': sparseTrunks, 'segments':sparseSegments}
        
    elif mapType == 'trunk and branch map':
        treeData = {'trunk': sparseTrunks, 'branches': sparseBranches}
        
    elif mapType == 'full map':
        treeData = {'trunk': sparseTrunks, 'segments':sparseSegments, 'branches': sparseBranches}

    return(treeData)
