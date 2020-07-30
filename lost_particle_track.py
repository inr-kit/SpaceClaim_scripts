# Python Script, API Version = V16
import pdb
###################### VISUAL EFFECT #####################
# the points drawn are the actual lost particle location
# the green tracks are the lost particle detail history
# the red tracks are the lost partcile travel direction
# if you don't like the line shown above the model, select them and 
# in property-> layout : change from True to False
###################### USER INPUT #####################
#"McnpOutFile" MCNP out put file path. when windows path is used, "\" must be replaced with "\\"
# It is suggested to remove the inrelevant output and keep only the lost particle outputs to speed up
McnpOutFile = "D:\\VirtualMachine\\share\\mcnp\\newTA_errfix_src.mcnpo"
# "maxTrackperHist": The max tracks visualized per lost particle, suitable only with detail lost history
maxTrackperHist = 10  
# "trackLen": the track length to draw the particle track after leaving the lost point
trackLen = 0.1 
########################################################
tracks=[]
IdxTracks = -1
with open(McnpOutFile) as McnpOut:
    while True :
        line = McnpOut.readline()
        if not line:  break
        if "1     event" in line:
            print line
            tracks.append([])
            IdxTracks += 1
            # McnpOut.readline()
            # McnpOut.readline()
            # McnpOut.readline()
            while True :
                line = McnpOut.readline()
                if  ( "source" in  line ) or ( "sur" in  line ):
                    #append the points
                    x0 = float( line[12:19] + "E" + line[19:22]  ) *0.01
                    y0 = float( line[22:29] + "E" + line[29:32] )*0.01
                    z0 = float(line[32:39] + "E" + line[39:42] )*0.01
                    tracks[IdxTracks].append([x0,y0,z0])
                    x1 = float(line[42:49] + "E" + line[49:52] ) * trackLen +x0
                    y1 = float( line[52:59] + "E" + line[59:62])  * trackLen +y0
                    z1 = float(line[62:69] + "E" + line[69:72])   * trackLen +z0
                elif "1   lost" in line:
                    #append the last point to draw the direction of particle travelling
                    tracks[IdxTracks].append([x1 ,y1 ,z1 ])
                    break
                else: 
                    continue
        elif "1   lost" in line:
            print line 
            tracks.append([])
            IdxTracks += 1
            while True :
                line = McnpOut.readline()
                if "energy =" in line:
                    break
                elif ( "x,y,z" in  line ):
                    aLineSplit = line.split()
                    x0 = float(aLineSplit[-3] ) *0.01
                    y0 = float( aLineSplit[-2])*0.01
                    z0 = float(aLineSplit[-1])*0.01
                    tracks[IdxTracks].append([x0 , y0 ,z0 ])
                    line =  McnpOut.readline()
                    aLineSplit = line.split() 
                    x1 = float(aLineSplit[-3] ) * trackLen +x0
                    y1 = float( aLineSplit[-2])  * trackLen +y0
                    z1 = float(aLineSplit[-1])   * trackLen +z0
                    tracks[IdxTracks].append([x1 ,y1 ,z1 ])
                else: 
                    continue
                
print "Done with reading. Creating the tracks..."      
newComponent = ComponentHelper.CreateAtRoot("Points")
ComponentHelper.SetActive(newComponent) # put all the point to it
for i in range(len( tracks )):
    print "Track ", i 
    # Dpoint = designCurvePoint.Create(tracks[i][-1][0],tracks[i][-1][1],tracks[i][-1][2])
    maxOutput = maxTrackperHist +1
    if len (tracks[i]) < maxOutput :
        maxOutput = len (tracks[i]) 
    for j in range ( maxOutput-1 ):
        #print tracks[i][j]
        p1 = Point.Create(tracks[i][-j-1][0],tracks[i][-j-1][1],tracks[i][-j-1][2])
        p2 = Point.Create(tracks[i][-j-2][0],tracks[i][-j-2][1],tracks[i][-j-2][2])
        curveSegment = CurveSegment.Create(p1 , p2)
        
        #curves.Add(curveSegment)
        if curveSegment:
            designCurve = DesignCurve.Create(GetRootPart(),curveSegment)
            #create the point of lost
        if j == 0:
            designCurve.SetColor(None, Color.Fuchsia) # set the color of the last track, the IAppearanceContext can be set to None. 
            DatumPointCreator.Create(p2)   # draw the lost particle position.
