# Python Script, API Version = V17
import math
Tolerance = 1e-5

def checkSurface (aSolid):
    "check the torus and sketch surface"
    sketchFaces = [] # for two sketch faces at the two side of the pipe
    Tori = []
    for iFace in aSolid.Faces:
        if type (iFace.Shape.Geometry) is  Torus  :
            Tori.append(iFace)
        if type (iFace.Shape.Geometry) is  Plane  :
            for iEdge in iFace.Edges:
                Good = True
                if  type(iEdge.Shape.Geometry) is not  Circle:
                    print "The sketch face contains non-circle edges, please check."
                    Good = False
            if not Good:
                return [[], []] # return a empty list of solid
            else:
                sketchFaces.append(iFace)
    return [Tori, sketchFaces]

def createMidPlane(aSolid, FaceAngle):
    "create the mid plane of the pipe"
    # build the mid plane from mid-point of two scketch plane center, and the torus axis
    [Tori, sketchFaces] = checkSurface(aSolid)
    pointA = sketchFaces[0].Edges[0].Shape.Geometry.Frame.Origin
    pointB = sketchFaces[1].Edges[0].Shape.Geometry.Frame.Origin
    midPoint = Point.Create( (pointA.X + pointB.X)/2, (pointA.Y + pointB.Y)/2,  (pointA.Z + pointB.Z)/2 )
    midDatumPoint = DatumPoint.Create(GetRootPart(),"point",  midPoint)
    torusAxis = DatumLine.Create(GetRootPart(),"axis", Tori[0].Shape.Geometry.Axis)
    aList = List[IDocObject]()
    aList.Add(torusAxis)        
#        if FaceAngle == 0.0 or  FaceAngle == 180.0 : # only if 180 degree
    # if math.fabs (FaceAngle - ( -1.0 )) <Tolerance  or math.fabs ( FaceAngle - ( 1.0 ))  <Tolerance: # only if 180 degree
    if sketchFaces[0].Shape.Geometry.IsCoincident (sketchFaces[1].Shape.Geometry) : # only if 180 degree
         #in this case the midpoint is in the torus axis, 
         # we create another axis through the midpoint and pependicular to the torus axis
        aAxis = Line.Create(midPoint, sketchFaces[0].Edges[0].Shape.Geometry.Axis.Direction)
        newAxis = DatumLine.Create(GetRootPart(),"axisB", aAxis)
        aList.Add(newAxis)
    aList.Add(midDatumPoint)
    midPlane = DatumPlane.GetPlane(aList)
    Delete.Execute(Selection.Create(aList))
    return midPlane

def calCosine(vec1, vec2): 
    "calculate the cosine of the angle"
   
    #fix tolerenace problem that cause mis calculation of the angle
    aX = vec1.X if math.fabs(vec1.X) > Tolerance else 0.0
    aY = vec1.Y if math.fabs(vec1.Y) > Tolerance else 0.0
    aZ = vec1.Z if math.fabs(vec1.Z) > Tolerance else 0.0
    vec1 = Vector.Create(aX, aY, aZ)
    aX = vec2.X if math.fabs(vec2.X) > Tolerance else 0.0
    aY = vec2.Y if math.fabs(vec2.Y) > Tolerance else 0.0
    aZ = vec2.Z if math.fabs(vec2.Z) > Tolerance else 0.0
    vec2 = Vector.Create(aX, aY, aZ)   


    # FaceAngle =  math.acos(Vector.Dot(vec1, vec2) ) * 180 / math.pi
    FaceAngle =  Vector.Dot(vec1, vec2) 
    return FaceAngle

def dividePipe(aSolid):
    "divide the pipe if larger than 90 degree"
    #check the surface
    [Tori, sketchFaces] = checkSurface(aSolid)
    if len(Tori) == 0 or len(Tori) > 2 :
        print "This solid is not a pipe, or contain more than 1 pipe segments, or have unsupported surface type."
        return [] # return a empty list of solid        
    if len (sketchFaces) !=  2 :
        print "This solid is not a pipe,the sketch face is strange."
        return [] # return a empty list of solid
    
    # check the angle split the solid
    aSolidList = []
    vec1 = sketchFaces[0].Edges[0].Shape.Geometry.Axis.Direction.UnitVector
    vec2 = sketchFaces[1].Edges[0].Shape.Geometry.Axis.Direction.UnitVector

    FaceAngle = calCosine(vec1, vec2)
#    if FaceAngle > 0  and FaceAngle <= 90
    if FaceAngle > (0 - Tolerance)  and FaceAngle < (1- Tolerance):
        # no need to split
        aSolidList.append(aSolid)
        return aSolidList
    else:
        ## split the solid
        selection = Selection.Create(aSolid)
        midPlane = createMidPlane(aSolid, FaceAngle)
        try:
            SplitResults = SplitBody.Execute(selection, midPlane)
        except:
            print "Split failed!"
            return []
        splitBodies = SplitResults.CreatedBodies
        #add current body also into the list for recursive decomposed
        splitBodies.Add(aSolid)
        return splitBodies # we assume the pipe is bended no larger than 180 degree

def pullPipe (sketchFace, midPlane, midPoint):
    "pull the pipe based on the sketch plane"
    options = ExtrudeFaceOptions()
    selection = Selection.Create(sketchFace)
    midDatumPlane = DatumPlane.Create(GetRootPart(),"plane",midPlane)
    upToSelection = Selection.Create(midDatumPlane)
    options.ExtrudeType = ExtrudeType.ForceIndependent
    #note: without  options.PullSymmetric = True the pipe will not pull always straightly (sometimes it creates again a torus )
    #pull a symetric solid, and cut it and throw away one side.
    options.PullSymmetric = True
    try :
        result = ExtrudeFaces.UpTo(selection, sketchFace.Edges[0].Shape.Geometry.Axis.Direction, upToSelection, midPoint, options)
    except :
        print "extrude failed!"
        Delete.Execute(Selection.Create(midDatumPlane))
        return None
    aSolid = result.CreatedBodies[0]
    selection = Selection.Create(aSolid)
    try:
        SplitResults = SplitBody.Execute(selection, sketchFace.Shape.Geometry)
    except:
        print "Split failed!"
        return None
    #clean up
    Delete.Execute(Selection.Create(midDatumPlane))
    splitBody = SplitResults.CreatedBodies[0]
    # check the correct one, and delete another one
    found = False
    for iFace in aSolid.Faces:
        if iFace.Shape.Geometry.IsCoincident( midPlane ):
            found = True
    if found:
        Delete.Execute(Selection.Create(splitBody))
        return aSolid
    else:
        Delete.Execute(Selection.Create(aSolid))
        return splitBody

    


def tor2cyl(aSolid) :
    "convert torus to two joined cylinder "
    ### we found out it has higher chance of success when copy the solid to a new document###
    
    result = Copy.ToClipboard( Selection.Create(aSolid) ); ##time.sleep(0.2)
    # remembering the parent
    comp =aSolid.Parent.Parent 
    if aSolid.Parent == GetRootPart() :
        comp = GetRootPart()
    #create a new document to save the solid to STEP file
    DocumentHelper.CreateNewDocument(); 
    result = Paste.FromClipboard();
    bSolid = Selection.GetActive().Items[0]      
    
    # do the job
    [Tori, sketchFaces] = checkSurface(bSolid)  
    vec1 = sketchFaces[0].Edges[0].Shape.Geometry.Axis.Direction.UnitVector
    vec2 = sketchFaces[1].Edges[0].Shape.Geometry.Axis.Direction.UnitVector
    FaceAngle = calCosine(vec1, vec2)
    midPlane = createMidPlane(bSolid, FaceAngle)
    pointA = sketchFaces[0].Edges[0].Shape.Geometry.Frame.Origin
    pointB = sketchFaces[1].Edges[0].Shape.Geometry.Frame.Origin
    midPoint = Point.Create( (pointA.X + pointB.X)/2, (pointA.Y + pointB.Y)/2,  (pointA.Z + pointB.Z)/2 )
    # the solid should be hide first, otherwise the pull option is add or cut this solid
    ViewHelper.SetObjectVisibility(Selection.Create(bSolid), VisibilityType.Hide, False)
    #pull two sketch faces toward the midplane
    #sometime one is failed, try to mirror another one
    newSolid = pullPipe (sketchFaces[0], midPlane, midPoint)
    if newSolid is None:
        newSolid = pullPipe (sketchFaces[1], midPlane, midPoint)
        if newSolid is None:
            print "Not able to convert the pipe due to failure of pulling"
            ViewHelper.SetObjectVisibility(Selection.Create(bSolid), VisibilityType.Show, False)
            return
    #mirror the one 
    selection = Selection.Create(newSolid)
    midDatumPlane = DatumPlane.Create(GetRootPart(),"plane",midPlane)
    mirrorPlane = Selection.Create(midDatumPlane)
    options = MirrorOptions()
    options.MergeObjects = False
    options.CreateRelationships = False
    result = Mirror.Execute(selection, mirrorPlane, options, None)
    #clean up 
    Delete.Execute(Selection.Create(bSolid))   
    Delete.Execute(Selection.Create(midDatumPlane))   
   
     #copy all solids to the working document
    Copy.ToClipboard( Selection.Create( GetRootPart().GetBodies()))    
    CloseWindow() 
    # delete the original solid
    if type(comp) is Part :
        ComponentHelper.SetRootActive()
    else :
        ComponentHelper.SetActive(comp)
    Delete.Execute(Selection.GetActive())
    result = Paste.FromClipboard() 
    
    
    

##Main process
SelectSolids = Selection.GetActive().Items
for iSel in SelectSolids : 
    #check if solid body. Components will be filtered
    if ( (type(iSel) is DesignBody) or ( hasattr(iSel, "Master") and (type(iSel.Master) is DesignBody) ) ):
        #check if needed and divide the pipe
        dividedPipes = dividePipe(iSel)
        for iSolid in dividedPipes:
            tor2cyl(iSolid)     
            