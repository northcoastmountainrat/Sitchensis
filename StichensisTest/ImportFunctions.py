# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 12:55:16 2017

@author: rdk10
"""
import os
import pandas as pd
import Functions as f
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pdb

#############  Functions below #############################################

def getFileName():
    cwd = os.getcwd()
    root = tk.Tk()
    root.lift()
    root.attributes('-topmost',True)
    fullFileName = askopenfilename(initialdir = cwd ,title = "Select a tree file and directory", filetypes = [("Excel","*.xlsx"),("Excel","*.xlsm")])        #Ask user to pick files
    root.after_idle(root.attributes,'-topmost',False)
    root.withdraw()
    workingDir = os.path.dirname(fullFileName) #path to file
    fileName = fullFileName.rsplit('/')[-1] #Excludes path to file
    treeName = fileName.rsplit('.')[0] #For input file (excludes '.xlsx')
    return(workingDir, treeName, fullFileName)
    
def importExcelTree(fullFileName):
    """This section assumed one excel file per tree with a tabe for each type of measurements (trunk, segment, or branch)"""
    
    #Import data all at once
    treeData = pd.read_excel(fullFileName, sheet_name = None) #,converters={'name':str,'ref':str, 'referenceType':str})
    ####IMPORTANT  if version of pandas is <21 then sheet_name is not recognized and needs to be sheetname. better to update pandas
    
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
    
     #Assign declination to variable
    if any(['declin' in t.lower() for t in treeData]):
        if len([i for i, key in enumerate(keys) if 'declin' in key.lower()])>0:
            declinKey = keys[[i for i, key in enumerate(keys) if 'declin' in key.lower()][0]]
            declinRefs = pd.read_excel(fullFileName, sheet_name = declinKey ,converters={'name':str})
            declinRefs.columns = [x.lower() for x in declinRefs.columns]
            declination = declinRefs['declination'].iloc[0] #extract number
            declination = declination.item() # convert to python float from numpy.float64
    else:
        declination = 0.00
    
    #Assign cust refs to dataFrame
    if len([i for i, key in enumerate(keys) if 'cust' in key.lower()])>0:
        custKey = keys[[i for i, key in enumerate(keys) if 'cust' in key.lower()][0]]
        custRefs = pd.read_excel(fullFileName, sheet_name = custKey ,converters={'name':str})
        custRefs.columns = [x.lower() for x in custRefs.columns]
        custRefs['azi'] = custRefs['azi'] + declination
        custRefs = f.calcCustRefs(custRefs)
        
    else:
        custRefs = []
        
    #Saves the data if it exists and makes changes to columns so they work in the program
    if trunkBool:
        trunkDat = pd.read_excel(fullFileName, sheet_name = trunkKey, converters={'name':str,'ref':str})#, 'ref type':str})
        trunkDat.columns = [x.lower() for x in trunkDat.columns] 
        trunkDat['name'] = trunkDat['name'].str.upper()
        trunkDat['name'] = trunkDat['name'].str.replace(" ","")
        trunkDat['azi'] = trunkDat['azi'] + declination
        if any(pd.isnull(trunkDat.index)):
            trunkDat = trunkDat.reset_index(drop = True)
    
    if segBool:
        segs = pd.read_excel(fullFileName, parse_dates = False, sheet_name = segKey, converters={'name':str,'O/E':str,'base ref':str, 'top ref':str,'midsegment ref':str})
        segs.columns = [x.lower() for x in segs.columns]
        segs['name'] = segs['name'].str.replace(" ","")
        if segs['base azi'].dtype == 'O':
            print("Make sure there is no text in the 'base azi' column such as 'CALC' \n or there will be problems later")
        else:
            segs['base azi'] = segs['base azi'] + declination
            segs['top azi'] = segs['top azi'] + declination
        if any(pd.isnull(segs.index)):
            segs = segs.reset_index(drop = True)
        if 'base ht' in segs.columns and 'top ht' in segs.columns:        
            segs['base z'] = segs['base ht']
            segs['top z'] = segs['top ht']
        else:
            print("Warning: you must have segment columns labeled 'base ht' and 'top ht'")

        if any(pd.isnull(segs['name'])):
            print('These is at least one missing name in the segments file, please rectify this.')
                
        names = f.splitName(segs['name'])
        segs['top name'] = names['topNames']
        segs['base name'] = names['baseNames']
            
    if branchBool:
        branches = pd.read_excel(fullFileName, parse_dates = False , sheet_name = brKey, converters={'name':str,'O/E':str, 'L/D':str,'origin':str,'base ref':str, 'top ref':str,'midsegment ref':str})
        branches.columns = [x.lower() for x in branches.columns]
        branches['name'] = branches['name'].str.replace(" ","")
        branches['origin'] = branches['origin'].str.replace(" ","")
        branches['orig azi'] = branches['orig azi'] + declination
        branches['cent azi'] = branches['cent azi'] + declination
        if any(pd.isnull(branches.index)):
            branches = branches.reset_index(drop = True)
        if 'base ht' in branches.columns and 'top ht' in branches.columns:    
            branches['base z'] = branches['base ht']
            branches['top z'] = branches['top ht']
        else:
            print("Warning: you must have a branch columns labeled 'base ht' and 'top ht'")

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
        print('There were not trunk data specified, also check your version of pandas, you need version 21 or greater.')
    return(treeData, custRefs,  mapType)


def renameNotesCol(treeData, treeName, newname = 'notes'):
    
    #logFileName = '{0}_ErrorScan.txt'.format(treeName)
    
    for data in treeData:
        i = 0
        for col in treeData[data].columns:
            if 'notes' in col:
                ind = i
            i = i + 1
        #pdb.set_trace()
        currentName = treeData[data].columns.values[ind]
        treeData[data] = treeData[data].rename(columns = {currentName:newname})
        
        #textout = 'The notes column labeled {0} for {1} data was changed to "{2}"'.format(currentName, data, newname)
        #f.print2Log(logFileName, textout)
        
        noteColChanges = {'treePart':data , 'oldNoteName': currentName, 'renamedTo':newname}
        
    return (treeData, noteColChanges)

def excelExport(treeData, outPath, treeName):
    
    #Brings in raw data and fileName (with full path), and exports and excel file to that location and name
    #Appends the current date in daymonthyear format. 
    
    date = pd.Timestamp("today").strftime("%d%b%Y").lstrip('0')
    
    #segs.name = segs.name.apply(repr)
    #branches.origin = branches.origin.apply(repr)
    #branches.to_csv("brFromNode.csv")
    
    #This tests for types of data present
    trunkBool = any(['trunk' in t.lower() for t in treeData])
    segBool = any(['segment' in t.lower() for t in treeData] )
    branchBool = any(['branch' in t.lower() for t in treeData] )
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    #Makes new directory for output files
    
    writer = pd.ExcelWriter('{0}_{1}.xlsx'.format(outPath + '/' + treeName, date), engine='xlsxwriter')
   #Need to make this prettier 
 
    # Write each dataframe to a different worksheet.
    if trunkBool:
        treeData['trunk'].to_excel(writer, sheet_name='main trunk', index = False)
    if segBool:
        treeData['segments'].to_excel(writer, sheet_name='segments', index = False)
    if branchBool:
        treeData['branches'].to_excel(writer, sheet_name='branches', index = False)
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
def importForAcadTree(fileName):
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
        trunkDat = pd.read_excel("{0}.xlsx".format(fileName), sheet_name = trunkKey, converters={'name':str,'ref':str})#, 'ref type':str})
        trunkDat.columns = [x.lower() for x in trunkDat.columns] 
        trunkDat['name'] = trunkDat['name'].str.upper()
        trunkDat['name'] = trunkDat['name'].str.replace(" ","")
        if any(pd.isnull(trunkDat.index)):
            trunkDat = trunkDat.reset_index(drop = True)
    
    if segBool:
        segs = pd.read_excel("{0}.xlsx".format(fileName),parse_dates = False, sheet_name = segKey, converters={'name':str,'O/E':str,'base ref':str, 'top ref':str,'midsegment ref':str})
        segs.columns = [x.lower() for x in segs.columns]
        segs['name'] = segs['name'].str.replace(" ","")
        if any(pd.isnull(segs.index)):
            segs = segs.reset_index(drop = True)
        if 'base ht' in segs.columns and 'top ht' in segs.columns:        
            segs['base z'] = segs['base ht']
            segs['top z'] = segs['top ht']
        else:
            print("Warning: you must have segment columns labeled 'base ht' and 'top ht'")

        names = f.splitName(segs['name'])
        segs['top name'] = names['topNames']
        segs['base name'] = names['baseNames']
            
    if branchBool:
        branches = pd.read_excel("{0}.xlsx".format(fileName),parse_dates = False , sheet_name = brKey, converters={'name':str,'O/E':str, 'L/D':str,'origin':str,'base ref':str, 'top ref':str,'midsegment ref':str})
        branches.columns = [x.lower() for x in branches.columns]
        branches['name'] = branches['name'].str.replace(" ","")
        branches['origin'] = branches['origin'].str.replace(" ","")
        if any(pd.isnull(branches.index)):
            branches = branches.reset_index(drop = True)
        if 'base ht' in branches.columns and 'top ht' in branches.columns:    
            branches['base z'] = branches['base ht']
            branches['top z'] = branches['top ht']
        else:
            print("Warning: you must have a branch columns labeled 'base ht' and 'top ht'")
    
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
        print('There were no trunk data specified')
    return(treeData,  mapType)    