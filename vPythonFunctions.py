# -*- coding: utf-8 -*-
"""
This needs to be tested in the full program
"""
####################################################################
######## Setup         #############################################
####################################################################

import vpython as vp
import pdb

###################################################
###Improvements####################################

#Add smoothing function for normals along sharp conic edges
#Make frustum plotting faster (possibly rotated and translate points before creating shape)

#####################################################
####  Frustum creation functions ####################
   
def getNorm(a,b,c):
    #This takes in three vertices and computers the unit vector perpendicular to both
    return(vp.norm(vp.cross((b-a),(c-b))))

def buildfaces(axis, incs, topR, baseR):  #This builds vertices and normals into a compound list so I can use list comprehension in frustum 2 for speed
        vertexList = []
        normalList = []
        length = vp.mag(axis)
        costheta = 1
        sintheta = 0
        dtheta = 2*vp.pi/incs
        cosdtheta = vp.cos(dtheta)
        sindtheta = vp.sin(dtheta)
        p0 = vp.vec(length,0.0,0.0) #This is the center of the base circle
        p5 = vp.vec(0.0,0.0,0.0) #Center of the top circle
        
        for i in range(incs):
            newcostheta = costheta*cosdtheta-sintheta*sindtheta
            newsintheta = sintheta*cosdtheta+costheta*sindtheta
        
            # Vector / Vertices and Triangles
            p1 = vp.vec(length,topR*costheta,topR*sintheta)
            p2 = vp.vec(0.0, baseR*costheta, baseR*sintheta)
            p3 = vp.vec(0.0, baseR*newcostheta, baseR*newsintheta)
            p4 = vp.vec(length, topR*newcostheta, topR*newsintheta)
            vertexList = vertexList + [[p0,p1,p4],[p1,p2,p3],[p1,p3,p4],[p5,p3,p2]] #First three = triangle from top center to edge, Next 6 are two triangles along slopd of conic, last three are triangle from edge to center of conic base
            
            #Normals bitches!
            n0 = vp.vec(1,0,0); n4 = vp.vec(-1,0,0)
            n2 = getNorm(p1,p2,p3)
            n3 = getNorm(p1,p3,p4)
            
            #Play with this to smooth out the shape
            normalList = normalList + [[n0,n0,n0],[n2,n2,n2],[n3,n3,n3],[n4,n4,n4]]
            
#            #Insert section here to average normals between the normals for p3-p4 of current section with p1-p2 of previous section
#            #NOT TESTED
#            for i in range(int(len(normalList)/incs)):
#                #avg p1 of current with p4 of previous
#                normalList[i+2][0] = (normalList[i+2][0] + normalList[i-3][2])/2
#                #avg p2 of current with p3 of previous
#                normalList[i+2][1] = (normalList[i+2][1] + normalList[i-3][1])/2
#                i = i+4
                
            sintheta = newsintheta
            costheta = newcostheta
    
        return(vertexList, normalList)
    
def triFun(vertices, normals, color): #This is to pass to the list comprehension in the frustum2 function.
    a = vp.vertex(pos = vertices[0], normal = normals[0], color = color)
    b = vp.vertex(pos = vertices[1], normal = normals[1], color = color)
    c = vp.vertex(pos = vertices[2], normal = normals[2], color = color)
    return (vp.triangle(vs =[a,b,c]))

def frustum(basePos, topPos, baseR, topR, color, visible = True):  #This function should be faster than frustum1 because if uses list comprehension 
    #takes in vpython vectors at this point
    if baseR > 0.5:
        incs = 40*int(round(baseR))  #make this a function of the radius, this is the number of breaks in the shape, controls resolution
    else:
        incs = 25
    
    axis = topPos-basePos
    centroid = (basePos + topPos)/2 #Center position along axis
    vertexList, normalList = buildfaces(axis, incs, topR, baseR)
    
    #Create a list of triangles, is there a way to make this faster? 
    shape = [triFun(vertices =i, normals = j, color = color) for i,j in zip(vertexList,normalList)] #list comprehension version
    #pos is position of the centroid of the shape
    #shp = vp.compound(shape, pos = vp.vec(0,0,0)) #move centroid to origin before rotation and translation
    if visible == True:
        shp = vp.compound(shape, pos = vp.vec(0,0,0)) #move centroid to origin before rotation and translation
    elif visible == False:
        shp = vp.compound(shape, pos = vp.vec(0,0,0), visible = False) #move centroid to origin before rotation and translation
    #first rotate the shape around z on the xy plane, is it possible to rotate points before creating shape?
    if axis.x == 0 and axis.y == 0: #This is so we don't divide by zero below
        thetaXY = 0
    elif axis.x == 0 and axis.y < 0: #rotate to y-axis topY negative
        thetaXY = vp.radians(270)
    elif axis.x == 0 and axis.y > 0: #rotate to y-axis topY positive
        thetaXY = vp.radians(90)
    elif axis.x != 0:                            #rotate somewhere between
        thetaXY = vp.atan2(axis.y,axis.x)
    shp.rotate(angle = thetaXY, axis = vp.vec(0,0,1))
    
    #Then rotate the shape around an axis perpendicular to shape axis and z-axis (cross product of axis and z-axis)
    rotAxis = vp.cross(shp.axis,vp.vec(0,0,1))
    thetaZ = vp.asin(axis.z/vp.mag(axis))  #Sin of z/magnitude of shape axis. 
    shp.rotate(angle = thetaZ, axis = rotAxis)
    
    #Translate to centroid location
    shp.pos = centroid
   
    return(shp)

##################################################################################
##### Other plotting-relevant functions    #######################################
##################################################################################
    
def centroidPositions(plotData):
    #finds centroid locations for plotting labels and translating frusta to correct locations
    plotData['centroid x'] = plotData.loc[:,['base x','top x']].mean(axis = 1)
    plotData['centroid y'] = plotData.loc[:,['base y','top y']].mean(axis = 1)
    plotData['centroid z'] = plotData.loc[:,['base z','top z']].mean(axis = 1)
    return(plotData)

def plotFrusta(treeData, plotType, colors):
    plotData = treeData[plotType]
    plotData = centroidPositions(plotData) #adds centroid cols to dataframe
    
    col = colors[plotType]
    
    frusta=[] # = sphere, = 
    labels =[]
    for i in range(len(plotData)):
        baseRadius = plotData['base radius'].iloc[i]
        topRadius = plotData['top radius'].iloc[i]
        basePosition = vp.vec(plotData['base x'].iloc[i],plotData['base y'].iloc[i],plotData['base z'].iloc[i])
        topPosition = vp.vec(plotData['top x'].iloc[i],plotData['top y'].iloc[i],plotData['top z'].iloc[i])
        dead = plotData['% dead'].iloc[i]
        
        #only plot is if the frusta top and bottom position are not the same, issue a warning if they are
        if not basePosition.mag == topPosition.mag:
            if dead > 95:
                if plotType == 'branches':
                    frusta.append(vp.cylinder(pos = basePosition, axis = topPosition-basePosition, radius = baseRadius, color = colors['dead']))
                else:
                    frusta.append(frustum(basePos = basePosition, topPos = topPosition, baseR = baseRadius, topR= topRadius, color = colors['dead']))
                #spheres[i] = vp.sphere(pos = basePos, radius = baseR, color = colors['dead'])
            else:
                if plotType == 'branches':
                    frusta.append(vp.cylinder(pos = basePosition, axis = topPosition-basePosition, radius = baseRadius, color = col))
                else:
                    frusta.append(frustum(basePos= basePosition, topPos= topPosition, baseR = baseRadius, topR = topRadius, color = col))
                #spheres[i] = vp.sphere(pos = basePos, radius = baseR, color = col)
            textPos = vp.vec(plotData['centroid x'].iloc[i] ,plotData['centroid y'].iloc[i] ,plotData['centroid z'].iloc[i])
            if plotType == 'trunk':
                textStr = str(plotData['base z'].iloc[i]) + " - " + str(plotData['top z'].iloc[i]) + "m"
            else:
                textStr = plotData['name'].iloc[i]
            labels.append(vp.label(pos = textPos, text = textStr, color = vp.color.black, visible = False))
        else:
            if plotType == 'trunk':
                frustName = str(plotData['base z'].iloc[i]) + "-" + str(plotData['top z'].iloc[i]) + "m"
            else:
                frustName = plotData['name'].iloc[i]
            print("Warning: The tree {0} named {1} has the same top base position and was not plotted.".format(plotType, frustName))    
    return(frusta, labels) #spheres, labels

def axes(origin):
    #Creates a visual of the 3d axes
    orig = vp.vec(origin[0],origin[1],origin[2])
    vp.arrow(pos = orig, axis = vp.vec(10,0,0), color = vp.color.green)
    vp.arrow(pos = orig, axis = vp.vec(0,10,0), color = vp.color.blue)
    vp.arrow(pos = orig, axis = vp.vec(0,0,10), color = vp.color.red)
    vp.text(pos = vp.vec(10,0,0) + orig, text = 'X', color = vp.color.green, billboard = True)
    vp.text(pos = vp.vec(0,10,0) + orig, text = 'Y', color = vp.color.blue, billboard = True)
    vp.text(pos = vp.vec(0,0,10) + orig, text = 'Z', color = vp.color.red, billboard = True)

