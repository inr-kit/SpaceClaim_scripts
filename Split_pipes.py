# Python Script, API Version = V17

def SplitRecursive (aSolid):
    "recursively split the pipe"
    CircleCurve  = []
    ## first get the circle curve
    for iEdge in  aSolid.Edges:
        if type (iEdge.Shape.Geometry) is Circle or type (iEdge.Shape.Geometry) is Ellipse or type (iEdge.Shape.Geometry) is NurbsCurve:
            CircleCurve.append(iEdge)
    ## filter circle with the same origin    
    SelectedCurve = []
    for i in range(len (CircleCurve)):
        curveA = CircleCurve[i]
        isSelect = True
#        for j in range(i+1,len (CircleCurve) ):
#            if curveA.Shape.Geometry.Frame == CircleCurve[j].Shape.Geometry.Frame:
#                isSelect = False
#                break
        if isSelect:
            #select only circle by joining the cycliner and torus surface
            for iFace in curveA.Faces:
                if (type (iFace.Shape.Geometry) is not Cylinder ) and (type (iFace.Shape.Geometry) is not Torus) and (type (iFace.Shape.Geometry) is not Cone) and (type (iFace.Shape.Geometry) is not ExtrudeFaces):
                    if ( type (iFace.Shape.Geometry) is  not Plane) and  ( type (iFace.Shape.Geometry) is  not Sphere) :
                        print "Error: unrecognized surface type!"
                    isSelect = False
                    break
            if isSelect:    
                SelectedCurve.append(curveA) 
    
    ## split the solid 
    if len(SelectedCurve) == 0:
            print "finished one solid"
            return
     
     #fill the circle to get a design plane, other ways is not successful. To be optimized
    aCircle  = SelectedCurve[0]
    #for aCircle in SelectedCurve:
    selection = Selection.Create(aSolid)
    aList = List[IDocObject]()
    aList.Add(aCircle)
    try:
        SplitResults = SplitBody.Execute(selection, DatumPlane.GetPlane(aList))
    except:
        print "Split failed!"
        return    
#    SplitResults = SplitBody.Execute(selection, DatumPlane.GetPlane(aList))
    resultBodies = SplitResults.CreatedBodies
    #add current body also into the list for recursive decomposed
    resultBodies.Add(aSolid)
    for iResult in resultBodies:
        SplitRecursive(iResult)

##main process            
SelectSolids = Selection.GetActive().Items
for iSel in SelectSolids :
    #check if solid body. Components will be filtered
    if ( (type(iSel) is DesignBody) or ( hasattr(iSel, "Master") and (type(iSel.Master) is DesignBody) ) ):
        #!!only for intellisense convinences, muss be comment out!!
        # isel = GetRootPart().Bodies[0].Edges[0].Faces[0].Shape.Geometry
        SplitRecursive(iSel)

