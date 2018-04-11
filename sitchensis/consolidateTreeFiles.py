# -*- coding: utf-8 -*-
"""
This consolidates all tree files within a directory into one file. The main trunk, segments, and branches each have their own tab. 
The treefiles are in the format output by the treeCalcs MainBodyScript. These files only include the column headers shown in rows 78-80 below. 

@author: rdk10
"""

import tkinter as tk
import tkinter.filedialog
#from tkinter.filedialog import askdirectory  #Try this 
import pandas as pd
import os, sys
sys.path.append('C:/Users/rdk10/Desktop/ComputerProgramming/Python/TreeCalcs')  #I need to learn how NOT to hard code in this kind of stuff. 
import pdb
#####################################################
# Improvements
# Get rid of hard coded column headers and path to cwd. 

###################################
####   USER INPUTS   ##############
###################################
cwd = os.getcwd()
root = tk.Tk()
root.lift()
root.attributes('-topmost',True)
fileDirectory = tk.filedialog.askdirectory(parent=root, initialdir=cwd, title='Please select a directory')
root.after_idle(root.attributes,'-topmost',False)
root.withdraw()

heightFile = 'C:/Users/rdk10/Dropbox/FieldDataNeedsCollation/WholeTreeNumbers.xlsx' #file for getting tree heights to calculate total tree heights. 


###########################
## Import function  #######
###########################


def importExcelTree(fileName):
    """This section assumed one excel file per tree with a tabe for each type of measurements (trunk, segment, or branch)"""
    
    #Import data all at once
    treeData = pd.read_excel(fileName, sheet_name = None) #,converters={'name':str,'ref':str, 'referenceType':str})
    
    #list of dictionary keys
    keys = [key for key in treeData]

    #This tests for types of data present and assigns keys
    if any(['trunk' in t.lower() for t in treeData]):
        trunkKey = keys[[i for i, key in enumerate(keys) if 'trunk' in key.lower()][0]]
        if len(treeData[trunkKey])>0:
            trunkBool = True
        else:trunkBool = False
    else:trunkBool = False
    
    if any(['seg' in t.lower() for t in treeData]):
        segKey = keys[[i for i, key in enumerate(keys) if 'seg' in key.lower()][0]]
        if len(treeData[segKey])>0:
            segBool = True
        else:segBool = False
    else:segBool = False
    
    if any(['branch' in t.lower() for t in treeData]):
        brKey = keys[[i for i, key in enumerate(keys) if 'branch' in key.lower()][0]]
        if len(treeData[brKey])>0:
            branchBool = True
        else:branchBool = False
    else:branchBool = False
        
    #Saves the data if it exists and makes changes to columns so they work in the program
    if trunkBool:
        trunkDat = pd.read_excel(fileName, sheet_name = trunkKey, converters={'name':str})#, 'ref type':str})
        trunkDat.columns = [x.lower() for x in trunkDat.columns] 
        trunkDat['name'] = trunkDat['name'].str.upper()
        trunkDat['name'] = trunkDat['name'].str.replace(" ","")
        if any(pd.isnull(trunkDat.index)):
            trunkDat = trunkDat.reset_index(drop = True)
    
    if segBool:
        segs = pd.read_excel(fileName, parse_dates = False, sheet_name = segKey, converters={'name':str,'O/E':str})
        segs.columns = [x.lower() for x in segs.columns]
        segs['name'] = segs['name'].str.replace(" ","")
        if any(pd.isnull(segs.index)):
            segs = segs.reset_index(drop = True)
            
    if branchBool:
        branches = pd.read_excel(fileName,parse_dates = False , sheet_name = brKey, converters={'name':str,'O/E':str, 'L/D':str,'origin':str})
        branches.columns = [x.lower() for x in branches.columns]
        branches['name'] = branches['name'].str.replace(" ","")
        branches['origin'] = branches['origin'].str.replace(" ","")
    
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

    return(treeData, mapType)


##################################
####  run the routine    #########
##################################

if len(fileDirectory) >0:
    #Create a list of the .xlsx files in the directory
    fileList = os.listdir(fileDirectory)
    fileList = [x for x in fileList if x.endswith("xlsx")]

    #For each file in the list
    for i in range(len(fileList)):
        currentFile = fileDirectory + '/' + fileList[i]
        treeName = fileList[i].rsplit('_')[0]
        
        if i == 0: #If it is the first file save the data as a data.frame with headers
            #import file
            treeData, mapType = importExcelTree(currentFile)
            
            #Extract tree name and add column
            for sheet in treeData:
               # treeData[sheet]['treeName'] = treeName
                treeData[sheet].insert(0, 'treeName', treeName)
            
            #mapType var tells you what combination of trunks segments and branches there are.
            #some trees are only trunk mapped, others only segment mapped etc...
        else:
            treeDataAppend, mapType = importExcelTree(currentFile)
            
            #if is is any other file append the info to the original data.frame
            treeDataAppend['trunk'].insert(0, 'treeName', treeName)    #Add treeName
            treeData['trunk'] = treeData['trunk'].append(treeDataAppend['trunk'], ignore_index = True)

            if mapType == 'segment map' or mapType == 'full map':
                treeDataAppend['segments'].insert(0, 'treeName', treeName)  #Add tree name
                treeData['segments'] = treeData['segments'].append(treeDataAppend['segments'], ignore_index = True)
            if mapType == 'trunk and branch map' or mapType == 'full map':
                treeDataAppend['branches'].insert(0, 'treeName', treeName)   #Add tree name
                treeData['branches'] = treeData['branches'].append(treeDataAppend['branches'], ignore_index = True)

    #Import tree heights and join to file
    treeHts = pd.read_excel(heightFile, sheet_name = 'RawData') 
    treeHts = treeHts[['treeName', 'focalTreeHt']]
    
    treeData['trunk'] = pd.merge(treeData['trunk'],treeHts, on = 'treeName', how = 'left')        #Append column to data.frame
    treeData['segments'] = pd.merge(treeData['segments'],treeHts, on = 'treeName', how = 'left')
    treeData['branches'] = pd.merge(treeData['branches'],treeHts, on = 'treeName', how = 'left')

    #calculate relative heights (don't forget to add to final output!!!!!)
    treeData['trunk']['base rel ht'] = treeData['trunk']['base z'] / treeData['trunk']['focalTreeHt']
    treeData['trunk']['top rel ht'] = treeData['trunk']['top z'] / treeData['trunk']['focalTreeHt']
    treeData['segments']['base rel ht'] = treeData['segments']['base z'] / treeData['segments']['focalTreeHt']
    treeData['segments']['top rel ht'] = treeData['segments']['top z'] / treeData['segments']['focalTreeHt']
    treeData['branches']['rel ht'] = treeData['branches']['base z'] / treeData['branches']['focalTreeHt']
    
    #export the resulting data.frams as one excell file
    date = pd.Timestamp("today").strftime("%d%b%Y").lstrip('0')
    newDirectory = fileDirectory + '/consolidated'
    os.makedirs(newDirectory, exist_ok=True)
    outFile = '{0}/AllTreeStructureRaw_{1}.xlsx'.format(newDirectory, date)
    
    ## Rearrange column headers to make pretty
    trunkPrintCols = ['treeName', 'name','base radius','base x','base y','base z','base rel ht','top radius','top x','top y','top z','top rel ht', '% dead','s_fuzz','l_fuzz','notes']
    segPrintCols =['treeName', 'position','name','o/e','type','base radius','base x','base y','base z','base rel ht','top radius','top x','top y','top z','top rel ht', '% dead','s_fuzz','l_fuzz','notes']
    branchPrintCols = ['treeName', 'name','origin','o/e','l/d','base radius','base x','base y','base z','rel ht','top radius','top x','top y','top z','slope','hd', '% dead','notes']
    
    treeData['trunk'] = treeData['trunk'].loc[:,trunkPrintCols]
    treeData['segments'] = treeData['segments'].loc[:,segPrintCols]
    treeData['branches'] = treeData['branches'].loc[:,branchPrintCols]
 
    # Write data
    writer = pd.ExcelWriter(outFile, engine='xlsxwriter')
    treeData['trunk'].to_excel(writer, sheet_name='main trunk', index = False)
    treeData['segments'].to_excel(writer, sheet_name='segments', index = False)
    treeData['branches'].to_excel(writer, sheet_name='branches', index = False)
    writer.save()
    
else:
    print('You must select a directory to consolidate tree files')
