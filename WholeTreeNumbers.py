# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 15:54:03 2017

@author: rdk10
"""

################################################################################
## Make a frustum class and start making methods for it ########################
################################################################################

class frustum(object):
    # Forms a cone with the top cut off. Mag of axis sets height.
    def __init__(self, basePos=(0,0,0), topPos = (0,0,1), topR=2.0, baseR=10.0, dead = 0, color):
        self.__basePos = basePos
        self.__topPos = topPos
        self.__baseR = baseR
        self.__topR = topR
        self.__color = color
        self.__dead = dead
            
    def getbase(self):
        return self.__basePos

    def setbase(self, basePos):
        self.pos = self.__pos = basePos

    basePos = property(getbase, setbase)

    def gettop(self):
        return self.__topPos

    def settop(self, topPos): # scale all points in front face
        self.topPos = self.__topPos = topPos
        
    topPos = property(getaxis, setaxis)

    def getbaseR(self):
        return self.__baseR
    
    def setbaseR(self, baseR): # scale all points involving r1
        self.__baseR = baseR

    baseR = property(getbaseR, setbaseR)

    def gettopR(self):
        return self.__topR
    
    def settopR(self, topR):# scale all points involving r2
        self.__topR = topR

    topR = property(gettopR, settopR)

    def getcolor(self):
        return self.__color
    
    def setcolor(self, color):
        self.__color = color
        self.color = color

    color = property(getcolor, setcolor)
    
    def cambiumSA(self):
       
    return (cSA)

#Define formulas and equations

#### Extract trunks, segments, and branches for all trees at once
#Open database
#import one dataframe for each and coerce columns into correct types

## Create new columns for each tree type


##Calculate relevant variables for each tree section
for i in trunks.index:
    trunks.set_values(i,'heartwoodVolume') = frustVol(bX,bY,bZ,bHW,tX,tY,tZ,tHW)
    trunks.set_values(i,'heartwoodSA') = frustSA(bX,bY,bZ,b)
    trunks.set_values(i,'woodVolume') = 
    trunks.set_values(i,'woodVolume') = 
    trunks.set_values(i,'woodVolume') = 
    trunks.set_values(i,'woodVolume') = 
    trunks.set_values(i,'woodVolume') = 
    trunks.set_values(i,'woodVolume') = 
    
for i in segments.index:
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    segments.set_values(i,'woodVolume') = 
    
for i in branches.index:
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 
    branches.set_values(i,'woodVolume') = 

##Aggregate numbers by tree and save to a new excel file and/or database table


##Estimate standard error based on uncertainty in bark, sap, diam measurements, and branche equations etc...






